# Video diagnostics

Use for code-rendered clips and for an existing video reported as frozen, choppy or slow to start. Independently written, informed by Designer Stack v6's decoded-frame and page-playback methods. The owned helper reports file measurements; it does not certify smoothness or taste.

## Inspect the delivered file

Use local files and the existing `ffmpeg`/`ffprobe` installation. From the skill directory:

```sh
python3 scripts/video_diagnostics.py /absolute/path/clip.mp4 --start 0 --duration 5
python3 scripts/video_diagnostics.py /absolute/path/clip.mp4 --start 5 --duration 5 --poster /absolute/path/poster.png
```

The default sample is the first ten seconds, capped at the video's remaining duration. Select additional intervals from the shot list, especially transitions and any reported hitch; one sample does not cover a whole film. Each call accepts at most sixty seconds. Exit 0 means measurements completed, not that quality passed. Exit 2 with `status: unavailable` means the file, tools or measurement failed.

The helper requires usable video-stream duration metadata. Some containers expose only a duration for all tracks; an audio tail can extend beyond the last video frame. Those files return unavailable rather than presenting the extra audio time as frozen video. Inspect them with the project's existing media tools instead of substituting container duration.

- **Declared frame rate** describes the stream; duplicate padding can make a low-motion capture declare 30 or 60 fps.
- **Estimated changed fps and longest unchanged interval** come from decoded pixel differences in the named sample, including its tail. Compare with the intended motion and source frame rate. Deliberate reading holds and low-motion shots can look like freezes; do not silently ignore the largest gaps. Animated grain can make a frozen composition look active to this measurement. Review meaningful objects on a contact sheet and in playback.
- **MP4 faststart** reports whether the metadata box precedes media data. False suggests remuxing with `-movflags +faststart` when progressive delivery needs it; null means the helper did not establish ordering. This is not a network-startup measurement or a universal claim about streaming behaviour.
- **Poster difference** compares an optional image with video frame zero, even when the motion sample starts later. It is a coarse grayscale difference, not a perceptual threshold. Colour-only changes and small local differences can escape it. Inspect the real poster-to-playback transition; if a seamless handoff is intended, generate the poster from the final delivered file and verify its crop.

Keep the JSON report with the actual sample interval and contact-sheet evidence. Do not change the film to satisfy a global unique-frame or background-flatness target. Sourced content, intentional holds and approved visual direction govern.

## Separate file defects from page playback

Play the final asset in its actual page on the target browser/device, with its real crop, poster, autoplay rules and surrounding effects. If available, sample `getVideoPlaybackQuality()` at the start and end of a controlled interval; report deltas for total and dropped frames, with viewport and page state. A cumulative counter, metadata probe or headless file decode cannot prove current playback quality.

If the file is sound but playback stutters, isolate one page cost at a time using the project's performance tools. Compare repeated before/after runs under comparable load, recording the effects enabled and sample duration. Layout counts are diagnostic evidence, not a load-independent performance score; transform-only motion can still be expensive through paint, compositing or GPU work. Check actual dropped frames and user-visible playback before claiming improvement. Preserve reduced-motion behaviour and Safari checks when the page is used there.
