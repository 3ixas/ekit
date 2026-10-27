from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/frontend-and-design/motion/scripts/video_diagnostics.py"
spec = importlib.util.spec_from_file_location("video_diagnostics", SCRIPT)
video_diagnostics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video_diagnostics)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe unavailable")
class VideoDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.ffmpeg = shutil.which("ffmpeg")
        for name, source, filters in [
            ("smooth", "testsrc2=size=160x96:rate=30:duration=2", None),
            ("padded", "testsrc2=size=160x96:rate=5:duration=2", "fps=30"),
            ("native24", "testsrc2=size=160x96:rate=24:duration=2", None),
            ("held", "testsrc2=size=160x96:rate=30:duration=1", "tpad=stop_mode=clone:stop_duration=1"),
            ("grain", "color=c=gray:size=160x96:rate=30:duration=2", "noise=alls=40:allf=t+u"),
        ]:
            command = [cls.ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", source]
            if filters:
                command += ["-vf", filters]
            subprocess.run(command + ["-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(cls.root / f"{name}.mp4")], check=True, capture_output=True, timeout=30)
        subprocess.run([cls.ffmpeg, "-v", "error", "-y", "-i", str(cls.root / "smooth.mp4"), "-c", "copy", str(cls.root / "slowstart.mp4")], check=True, capture_output=True, timeout=30)
        # Matroska exposes container duration, with no stream duration here.
        # The audio lasts twice as long as the smooth video.
        subprocess.run([
            cls.ffmpeg, "-v", "error", "-y", "-i", str(cls.root / "smooth.mp4"),
            "-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-c:v", "copy",
            "-c:a", "aac", str(cls.root / "audio-tail.mkv"),
        ], check=True, capture_output=True, timeout=30)
        for name, timestamp in [("match", "0"), ("wrong", "1")]:
            subprocess.run([cls.ffmpeg, "-v", "error", "-y", "-ss", timestamp, "-i", str(cls.root / "smooth.mp4"), "-frames:v", "1", str(cls.root / f"{name}.png")], check=True, capture_output=True, timeout=30)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def report(self, name: str, **options: object) -> dict:
        return video_diagnostics.diagnose(self.root / f"{name}.mp4", **{"start": 0, "duration": 2, **options})

    def test_distinguishes_smooth_from_duplicate_padded_video(self) -> None:
        good, padded = self.report("smooth"), self.report("padded")
        self.assertGreater(good["sample"]["estimated_changed_fps"], 27)
        self.assertLess(padded["sample"]["estimated_changed_fps"], 15)
        self.assertGreater(padded["sample"]["longest_unchanged_seconds"], 0.15)
        self.assertEqual(good["video"]["average_fps"], padded["video"]["average_fps"])

    def test_intentional_hold_is_measurement_not_failed_quality_gate(self) -> None:
        held = self.report("held")
        self.assertEqual(held["status"], "measured")
        self.assertGreater(held["sample"]["longest_unchanged_seconds"], 0.8)
        motion_only = self.report("held", duration=0.8)
        self.assertLess(motion_only["sample"]["longest_unchanged_seconds"], 0.1)
        hold_only = self.report("held", start=1.2, duration=0.6)
        self.assertLess(hold_only["sample"]["estimated_changed_fps"], 5)
        self.assertAlmostEqual(hold_only["sample"]["duration_seconds"], 0.6)

    def test_native_24fps_and_grain_never_become_quality_verdicts(self) -> None:
        native, grain = self.report("native24"), self.report("grain")
        self.assertAlmostEqual(native["sample"]["estimated_changed_fps"], 24, delta=1)
        self.assertGreater(grain["sample"]["estimated_changed_fps"], 27)
        self.assertEqual(grain["status"], "measured")
        self.assertTrue(any("grain" in note for note in grain["limitations"]))
        self.assertNotIn("pass", json.dumps(grain).lower())

    def test_faststart_and_poster_measure_real_file_properties(self) -> None:
        self.assertTrue(self.report("smooth")["mp4_faststart"])
        self.assertFalse(self.report("slowstart")["mp4_faststart"])
        match = self.report("smooth", start=0.5, duration=1, poster=self.root / "match.png")
        wrong = self.report("smooth", poster=self.root / "wrong.png")
        self.assertLess(match["poster"]["grayscale_mean_absolute_difference"], 2)
        self.assertGreater(wrong["poster"]["grayscale_mean_absolute_difference"], 3)

    def test_cli_reports_missing_dependency_as_unavailable(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root / "smooth.mp4")], env={**os.environ, "PATH": ""}, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "unavailable")

    def test_cli_reports_the_selected_interval_and_frame_zero_poster(self) -> None:
        result = subprocess.run([
            sys.executable, str(SCRIPT), str(self.root / "smooth.mp4"),
            "--start", "0.5", "--duration", "1", "--poster", str(self.root / "match.png"),
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "measured")
        self.assertEqual(report["sample"]["start_seconds"], 0.5)
        self.assertEqual(report["sample"]["duration_seconds"], 1)
        self.assertLess(report["poster"]["grayscale_mean_absolute_difference"], 2)

    def test_container_only_duration_does_not_turn_audio_tail_into_video_freeze(self) -> None:
        path = self.root / "audio-tail.mkv"
        probe = subprocess.run([
            shutil.which("ffprobe"), "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=duration:format=duration", "-of", "json", str(path),
        ], check=True, capture_output=True, text=True, timeout=10)
        info = json.loads(probe.stdout)
        self.assertNotIn("duration", info["streams"][0])
        self.assertGreater(float(info["format"]["duration"]), 3.9)
        result = subprocess.run([
            sys.executable, str(SCRIPT), str(path), "--duration", "4",
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "unavailable")
        self.assertNotIn("sample", report)

    def test_invalid_inputs_are_not_successful_measurements(self) -> None:
        for options in [{"start": -1}, {"duration": 0}, {"duration": float("nan")}, {"start": 10}]:
            with self.subTest(options=options), self.assertRaises(video_diagnostics.DiagnosticError):
                self.report("smooth", **options)
        with self.assertRaises(video_diagnostics.DiagnosticError):
            video_diagnostics.diagnose(self.root / "missing.mp4", 0, 2)
        corrupt = self.root / "corrupt.mp4"
        corrupt.write_bytes(b"not a video")
        with self.assertRaises(video_diagnostics.DiagnosticError):
            video_diagnostics.diagnose(corrupt, 0, 2)


class ContainerDiagnosticTests(unittest.TestCase):
    def test_other_formats_and_malformed_boxes_are_not_false_faststart_claims(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            path.write_bytes(b"not an mp4 container")
            self.assertIsNone(video_diagnostics.mp4_faststart(path))
            path.write_bytes(b"\x00\x00\x00\x04ftyp")
            with self.assertRaises(video_diagnostics.DiagnosticError):
                video_diagnostics.mp4_faststart(path)
