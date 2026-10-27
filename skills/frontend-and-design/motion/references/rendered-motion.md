# Rendered motion

Independently written for this repository, informed by Florence's "Opus 5.5 Motion Lab" (@flxrnc, 2026-09-30). Use it when the deliverable is an animation or video drawn by code and recorded frame by frame: a launch video, a looping social clip, a product shot, an explainer. Interface motion inside a running product follows [motion design](motion-design.md); where the two differ (exit easing, durations), the interface rules govern interface work.

## Direct with numbers, not adjectives

Every adjective leaves a decision to the model, and the model's decisions are the default look. Replace each one with what it means:

- "Premium" becomes materials: roughness, clearcoat, which surface carries the accent.
- "Cool" becomes a lighting setup: key, fill, and rim with colours and strengths.
- "Modern" becomes a camera: field of view, path, and the frame and curve of each move.
- "Animated" becomes timing: tempo, anticipation frames, and spring damping per element.

Name the defaults to avoid explicitly. A general "avoid the AI look" swaps one default for another; a named list works. A starting list: purple or blue gradients, glow and lens flares, decorative floating particles, everything fading in at once, fade-and-slide-up on every element, centred everything, text that moves while it is being read. After every first render, name what the model used anyway and add it to the list.

## Prompt anatomy

Fill every line before generating:

- **Goal:** one sentence on what the viewer should feel or do. If it cannot be written, no curve will rescue the piece.
- **Output:** engine, canvas size, fps, and frame count ("Remotion composition, 1920×1080, 30 fps, 450 frames"). Pick the canvas first; changing it later re-directs every shot.
- **Shots:** for each, a frame range, one hero move, and a handoff (a cut on the beat by default; a match cut or wipe only as a decision).
- **Look:** palette, type, materials, light, camera.
- **Preserve:** what must not change, such as a logo's or character's exact proportions.
- **Ban list:** the named defaults above plus any the brand rules out.
- **QA:** which stills to check before rendering the whole clip.

One hero per shot. Secondary moves travel 50–70% as far as the hero and start 100–200 ms after it; ambient motion stays under 5% of the hero's travel.

## Numbers

- **Easing:** in video, enter with ease-out, exit with ease-in about 40–50% shorter, move across the frame with ease-in-out. Linear only for rotation, progress, and loop phase.
- **Springs:** translate any library's settings to a damping ratio. 1.0 never bounces; 0.7–0.85 reads as premium; 0.4–0.6 playful; under 0.3 cartoon. Position and size may bounce; opacity and colour never do.
- **Stagger:** start the next element when the previous one is 30–50% done. Letters about one frame apart, words 60–120 ms, list items 40–80 ms.
- **Beat grid:** frames per beat = fps × 60 / BPM. Compute each beat from time and round it, rather than adding a rounded interval repeatedly, which drifts. Cut on the beat; change layout on the bar.
- **Holds:** on-screen text stays at least 0.3 s per word plus 0.5 s.
- **Camera:** the softest curves; objects get snappier ones. Parallax starts at 1.0, 0.5, and 0.2 for foreground, middle, and background.
- **Accessibility:** text keeps 4.5:1 contrast on every frame, including over moving backgrounds; never more than three flashes per second.

## Render contract

State it under every rendered-motion prompt:

- Every frame is a pure function of time `t` (or frame number). No clock, timer, or real-time delta.
- All randomness is seeded.
- A loop renders frames 0 to N−1, never N, and drives cyclic motion from `phase = frame / N` with whole-number cycles; organic drift samples noise along a circle so it returns to its start. Frame 0 is a finished composition.
- The page can be frozen at any time (for example `?t=2.5`) and exposes a frame counter during iteration, removed for the final render.

Render by driving a headless browser to each frame, saving the frames, and assembling them with ffmpeg. When a failure recurs, add its fix to the contract.

## Review loop

The first render is a draft; two to four rounds is normal.

For a final clip, hero poster, or reported stutter, use [video diagnostics](video-diagnostics.md) to inspect decoded frame changes and the actual page separately. The optional local helper reports measurements without judging intentional holds or declaring visual quality.

1. Render stills at key frames and a contact sheet of about twelve frames; read them before changing anything.
2. Write notes that name frames and numbers, not feelings ("the punch at frame 84 peaks two frames late"). Translate feelings first: "make it pop" becomes a 1.0 → 1.08 → 1.0 scale over six frames peaking on the beat; "it drags" becomes holds shortened by one beat; "it looks like AI" becomes the defaults it used, named and banned.
3. Change one or two things per round and re-render only what changed.
4. When the prompt pins numbers (labels lighting on frame 69, a landing on frame 140), audit the scene against them numerically across every frame, not only by eye.
5. When a fix does not hold, render the frames either side of the problem and describe the difference.

## Engine choice

| Piece | Engine |
|---|---|
| One idea under about 10 seconds, 2D | Plain HTML, CSS, and canvas |
| A series, template, or data-driven video | Remotion (free for individuals and companies of up to three people; larger companies need its company licence) |
| HTML and GSAP timelines rendered to MP4 | HyperFrames (Apache-2.0) |
| Anything 3D | Three.js; pin the version, since parameters change between releases |
| Motion inside a live product | Motion or GSAP, following [motion design](motion-design.md) |

Check each licence against the project before use.

## Sound and export

- The picture must work muted; feeds autoplay silently.
- Synthesized or licensed sound only. Land each sound one frame after its visual hit, never before. Mix to about −14 LUFS with peaks at −1 dBTP. A model cannot listen, so verify sync and levels by measuring the decoded file.
- MP4 for posts; GIF for inline loops, with one palette for the whole GIF. GIF delays are stored in hundredths of a second, so at 24 fps use five 40 ms frames then one 50 ms frame, repeating, to keep the loop's length exact.
- Check the target platform's current size, duration, and frame limits before export rather than relying on remembered figures.
