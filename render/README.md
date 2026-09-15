# Render pipeline

This folder reproduces `output/capco_technology_team.mp4` from scratch. It's a
custom, dependency-light pipeline built because this environment has no
video/animation-generation API — everything here runs locally with
open tools.

Inspired by the shot-recipe/beat-sync methodology in
[dlazy-ai/ai-product-video](https://github.com/dlazy-ai/ai-product-video)
(Remotion-based), but implemented with a lighter stack: plain HTML/CSS
animation + a real-time headless-browser capture instead of a React/Remotion
frame-by-frame renderer. A Remotion rewrite (frame-accurate, faster,
easier to re-edit per shot) is the natural next step if this gets reused
often — see "Possible upgrade" below.

## Tools used

| Purpose | Tool |
| --- | --- |
| Source artwork | The Capco storyboard image the user attached — cropped into its 8 numbered panels and used as the actual on-screen visuals (Ken Burns pan/zoom), not redrawn |
| Panel crop-boundary detection | Python + Pillow/NumPy, sampling pixel colors along scan-lines to find the real card edges (see "Cropping the storyboard" below) instead of a naive even grid split |
| Panel upscaling/sharpening | ffmpeg `scale` (lanczos) + `unsharp` filter, since the source panels are ~400×520px and need to fill a 1920×1080 frame |
| Voice-over | [Piper](https://github.com/rhasspy/piper) — offline neural TTS, `en_US-lessac-medium` voice |
| Background music | Procedurally generated with NumPy (sine/triangle pads + a soft pluck pulse) — no royalty-free-music API was reachable from this environment |
| Animation / motion graphics | Hand-written HTML/CSS/JS (Ken Burns keyframes, crossfades, the scene-8 capability-network overlay, the scene-4 bug sight-gag) |
| Rendering the animation to video | [Playwright](https://playwright.dev/) driving headless Chromium, using `recordVideo` to capture the page in real time |
| Audio mixing & final encode | ffmpeg — mixes narration + music, re-encodes the recorded `.webm` to H.264/AAC `.mp4` |

## Cropping the storyboard

The storyboard is one flat 1672×940 image: a header banner, then an 8-panel
grid (4 columns × 2 rows) with connector arrows between cards. An even
`width/4 × height/2` split cuts through those arrows and — because the rows
aren't exactly half the image height — bleeds the bottom of row 1's cards
into the top of row 2's crops. The real boundaries were found by sampling
pixel colors along horizontal/vertical scan-lines to locate the navy gaps
between cards. Final crop rectangles (x0-x1, y0-y1), measured from the near-white page
background between cards: 1: 0-428, 86-510 · 2: 434-833 · 3: 843-1262 ·
4: 1269-1667 (row 1) · 5: 4-430, 521-931 · 6: 435-834 · 7: 842-1229 ·
8: 1237-1671 (row 2). Note the column-3/4 boundary differs between rows.
Each panel is then lanczos-upscaled to 1700px wide and lightly
sharpened.

In the video every slide is shown **in full** (`.card`, height-fitted and
centered) over a blurred, darkened copy of itself as the backdrop; the only
motion on the slide is a gentle 0.955→1.0 zoom that never crops content.
Taglines, the bug gag and the scene-8/9 overlays live in the bottom band and
side gutters, never over the slide.

## Pipeline

1. **`gen_narration.py`** — synthesizes the voice-over with Piper, one clip
   per scene, and writes `timeline.json` with exact per-scene
   start/voStart/voEnd/end timings (narration duration + hand-tuned
   lead-in/hold padding for pacing).
2. **`gen_music.py`** — procedurally generates the background track.
3. **`build_narration_track.sh`** — delays and mixes the 9 per-scene voice
   clips into one `narration.wav` using the offsets from `timeline.json`.
4. **`scene.html`** — the animation: a 1920×1080 page with one
   absolutely-positioned `<div class="scene">` per beat. Each scene's
   background is the real storyboard panel (`panels/panelN.png`) animated
   with a per-scene Ken Burns `@keyframes` pan/zoom; scenes crossfade and a
   few small overlays (tagline chip, bug gag, capability-network labels)
   sit on top. Driven by `setTimeout`s scheduled from the injected
   `timeline.json`.
5. **`record.js`** — Playwright loads `scene.html` in headless Chromium and
   records it in real time via `recordVideo` (produces a silent `.webm`).
6. **`assemble_final.sh`** — mixes narration (full volume) with music
   (ducked ~-9dB) into `final_audio.wav`, then re-encodes the `.webm` to
   H.264/AAC `.mp4` with ffmpeg, muxing in that audio track.

## Regenerating

Requires: `piper-tts` (pip), a Piper voice model (`.onnx` + `.onnx.json`,
not committed here — ~60MB, fetched from the Piper GitHub releases), numpy,
Pillow, Playwright + a Chromium build, and ffmpeg with libx264/aac.

```bash
python3 gen_narration.py        # -> timeline.json, audio/*_raw.wav
python3 gen_music.py            # -> audio/music.wav
bash build_narration_track.sh   # -> audio/narration.wav
# inject timeline.json into scene.html in place of __TIMELINE_JSON__
node record.js                  # -> video_raw/*.webm  (real-time capture, ~4 min)
bash assemble_final.sh          # -> capco_technology_team.mp4
```

## Possible upgrade: Remotion

For frame-accurate, parallelizable rendering (no real-time capture, no
crossfade/timing races) and easier per-shot editing, port `scene.html`'s
scenes into React components driven by `useCurrentFrame()`/`interpolate()`
in a [Remotion](https://www.remotion.dev/) project, matching the approach
in `dlazy-ai/ai-product-video`. The scene structure, palette, and beat
timings in `timeline.json` carry over directly.
