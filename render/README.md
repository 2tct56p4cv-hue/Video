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
| Panel super-resolution | Real-ESRGAN x4plus (weights from its GitHub release) run through a self-contained RRDBNet in PyTorch (`upscale_panels.py`), since the source panels are only ~400×420px |
| Voice-over | [Piper](https://github.com/rhasspy/piper) — offline neural TTS; a different narrator per capability (ryan, amy, alan, southern_english_female, lessac, kathleen, danny — US/UK, male/female), intro and closing share the host voice; mapping in `gen_narration.py` |
| Background music | Procedurally generated with NumPy: 112 BPM electronic bed (16th-note synth arpeggio, soft kick, hats, sub bass, low-passed pad), mixed at -14 dB and side-chain ducked under the narration with ffmpeg `sidechaincompress` — no royalty-free-music API was reachable from this environment |
| Animation / motion graphics | Hand-written HTML/CSS/JS (Ken Burns keyframes, crossfades, the scene-8 capability-network overlay, the scene-4 bug sight-gag) |
| Rendering the animation to video | [Playwright](https://playwright.dev/) driving headless Chromium frame by frame: the page exposes `__seek(t)` (scene state + every CSS animation's `currentTime` set deterministically), one lossless PNG per frame at 25 fps (`render_frames.js`) |
| Audio mixing & final encode | ffmpeg — mixes narration + music; `encode_frames.sh` encodes the PNG sequence with libx264 CRF 17 (preset slow) + AAC 192k |

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

In the video every slide is first shown whole at full frame height (sides
extended with a blurred continuation of the slide, no border), then the
camera pushes in ~1.5× on the slide's focal area and holds. Overlays (tagline
chip, bug gag, scene-8 labels) are lower-thirds over the picture.

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
5. **`render_frames.js`** — Playwright loads `scene.html`, calls `__seek(t)`
   for every frame (25 fps) and saves a lossless PNG per frame.
6. **`encode_frames.sh`** — encodes the PNG sequence with the mixed
   soundtrack (narration + side-chain-ducked music) into a high-quality
   H.264/AAC `.mp4`.

## Regenerating

Requires: `piper-tts` (pip), a Piper voice model (`.onnx` + `.onnx.json`,
not committed here — ~60MB, fetched from the Piper GitHub releases), numpy,
Pillow, Playwright + a Chromium build, and ffmpeg with libx264/aac.

```bash
python3 gen_narration.py        # -> timeline.json, audio/*_raw.wav
python3 gen_music.py            # -> audio/music.wav
bash build_narration_track.sh   # -> audio/narration.wav
# inject timeline.json into scene.html in place of __TIMELINE_JSON__
python3 upscale_panels.py panels_src panels RealESRGAN_x4plus.pth   # 4x super-resolution
node render_frames.js           # -> frames/%06d.png (25 fps, ~12 min)
bash encode_frames.sh           # -> capco_technology_team.mp4
```

## Possible upgrade: Remotion

For frame-accurate, parallelizable rendering (no real-time capture, no
crossfade/timing races) and easier per-shot editing, port `scene.html`'s
scenes into React components driven by `useCurrentFrame()`/`interpolate()`
in a [Remotion](https://www.remotion.dev/) project, matching the approach
in `dlazy-ai/ai-product-video`. The scene structure, palette, and beat
timings in `timeline.json` carry over directly.
