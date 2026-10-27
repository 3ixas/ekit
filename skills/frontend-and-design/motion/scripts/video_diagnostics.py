#!/usr/bin/env python3
"""Measure a bounded sample of a local video; measurements are not a quality verdict.

Independently written, informed by Designer Stack v6's decoded-frame diagnostics.
Requires ffmpeg and ffprobe on PATH. No capture, encoding, downloads or writes.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys


class DiagnosticError(RuntimeError):
    """The requested measurements could not be completed."""


def run_tool(args: list[str], *, binary: bool = False) -> str | bytes:
    try:
        result = subprocess.run(args, capture_output=True, timeout=120, check=True)
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        raise DiagnosticError(f"{Path(args[0]).name} could not complete the measurement") from exc
    if binary:
        return result.stdout
    # ffmpeg emits showinfo on stderr; ffprobe JSON is on stdout.
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


def mp4_faststart(path: Path) -> bool | None:
    """Inspect top-level MP4 boxes; other formats have no MP4 faststart verdict."""
    total = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(8)
        if len(header) != 8 or header[4:] != b"ftyp":
            return None
        offset = 0
        moov = mdat = None
        while offset + 8 <= total:
            stream.seek(offset)
            size, kind = struct.unpack(">I4s", stream.read(8))
            header_size = 8
            if size == 1:
                extended = stream.read(8)
                if len(extended) != 8:
                    raise DiagnosticError("Truncated MP4 box")
                size = struct.unpack(">Q", extended)[0]
                header_size = 16
            elif size == 0:
                size = total - offset
            if size < header_size or offset + size > total:
                raise DiagnosticError("Invalid MP4 box size")
            if kind == b"moov" and moov is None:
                moov = offset
            if kind == b"mdat" and mdat is None:
                mdat = offset
            offset += size
        return moov < mdat if moov is not None and mdat is not None else None


def gray_frame(ffmpeg: str, path: Path) -> bytes:
    result = run_tool([
        ffmpeg, "-nostdin", "-v", "error", "-i", str(path), "-map", "0:v:0",
        "-frames:v", "1", "-vf", "scale=128:96", "-pix_fmt", "gray", "-f", "rawvideo", "-",
    ], binary=True)
    if not isinstance(result, bytes) or len(result) != 128 * 96:
        raise DiagnosticError("Could not decode a complete first frame")
    return result


def diagnose(path: Path, start: float, duration: float, poster: Path | None = None) -> dict[str, object]:
    if not math.isfinite(start) or start < 0 or not math.isfinite(duration) or not 0 < duration <= 60:
        raise DiagnosticError("Use a nonnegative start and a duration greater than 0 and at most 60 seconds")
    if not path.is_file() or (poster is not None and not poster.is_file()):
        raise DiagnosticError("Video and optional poster must be existing local files")
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise DiagnosticError("ffmpeg and ffprobe are required on PATH")
    raw = run_tool([
        ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,avg_frame_rate,duration", "-of", "json", str(path),
    ])
    try:
        info = json.loads(raw)
        video = info["streams"][0]
        # A container's audio can outlast its video. Never turn that tail into
        # an invented frozen frame interval when video duration is unavailable.
        length = float(video["duration"])
        fps = float(Fraction(video["avg_frame_rate"]))
        if not math.isfinite(length) or length <= 0 or fps <= 0:
            raise ValueError("invalid duration or rate")
    except (ValueError, KeyError, IndexError, TypeError, ZeroDivisionError) as exc:
        raise DiagnosticError("Video stream metadata lacks a usable duration or frame rate; container duration cannot establish the video endpoint") from exc
    if start >= length:
        raise DiagnosticError("Sample start must precede the end of the video")
    sampled = min(duration, length - start)
    log = run_tool([
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "info", "-ss", str(start),
        "-t", str(sampled), "-i", str(path), "-map", "0:v:0", "-an",
        "-vf", f"trim=duration={sampled},setpts=PTS-STARTPTS,mpdecimate=hi=256:lo=128:frac=0.1,showinfo",
        "-f", "null", "-",
    ])
    times = [float(value) for value in re.findall(r"pts_time:([0-9.eE+\-]+)", log)]
    if not times:
        raise DiagnosticError("No decoded frame measurements were returned")
    gaps = [b - a for a, b in zip(times, times[1:])]
    gaps.append(max(0.0, sampled - times[-1]))
    report: dict[str, object] = {
        "status": "measured",
        "source": str(path),
        "video": {"width": video["width"], "height": video["height"], "average_fps": fps, "duration_seconds": length},
        "sample": {
            "start_seconds": start, "duration_seconds": sampled, "duration_basis": "video_stream",
            "changed_frames": len(times), "estimated_changed_fps": round(len(times) / sampled, 3),
            "longest_unchanged_seconds": round(max(gaps), 6),
        },
        "mp4_faststart": mp4_faststart(path),
        "limitations": [
            "Changed pixels do not prove meaningful motion; animated grain can conceal frozen content.",
            "Intentional holds and low-motion content can produce low changed-fps or long unchanged intervals.",
            "Only the named sample was scanned; this does not measure browser playback or dropped frames.",
            "MP4 faststart reports box ordering, not network startup latency; null means not established.",
        ],
    }
    if poster is not None:
        first, image = gray_frame(ffmpeg, path), gray_frame(ffmpeg, poster)
        report["poster"] = {
            "path": str(poster), "compared_to": "video frame zero, regardless of sample start",
            "grayscale_mean_absolute_difference": round(sum(abs(a - b) for a, b in zip(first, image)) / len(first), 3),
            "limitation": "A coarse grayscale comparison can miss colour-only and small local differences; inspect both images.",
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float, default=10, help="sample seconds, at most 60 (default: 10)")
    parser.add_argument("--poster", type=Path)
    args = parser.parse_args()
    try:
        report = diagnose(args.video.resolve(), args.start, args.duration, args.poster.resolve() if args.poster else None)
    except (DiagnosticError, OSError) as exc:
        print(json.dumps({"status": "unavailable", "reason": str(exc)}))
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
