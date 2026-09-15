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

## Pipeline

1. **`gen_narration.py`** — synthesizes the voice-over with
   [Piper](https://github.com/rhasspy/piper) (offline neural TTS,
   `en_US-lessac-medium` voice), one clip per scene, and writes
   `timeline.json` with exact per-scene start/voStart/voEnd/end timings
   (narration duration + hand-tuned lead-in/hold padding for pacing).
2. **`gen_music.py`** — procedurally generates a subtle corporate pad/pluck
   background track with numpy (no royalty-free-music API available here).
3. **`build_narration_track.sh`** — delays and mixes the 9 per-scene voice
   clips into one `narration.wav` using the offsets from `timeline.json`.
4. **`scene.html`** — the actual animation: a single 1920×1080 HTML/CSS/JS
   page with one absolutely-positioned `<div class="scene">` per beat,
   crossfaded and internally animated (data pipelines, code typing, a
   pass-rate ring, a bridge with traveling packets, a network graph, etc.)
   driven by `setTimeout`s scheduled from the injected `timeline.json`.
5. **`record.js`** — a Playwright script that loads `scene.html` in headless
   Chromium and records it in real time via `recordVideo` (produces a silent
   `.webm`).
6. **`assemble_final.sh`** — mixes narration (full volume) with music
   (ducked ~-9dB) into `final_audio.wav`, then re-encodes the `.webm` to
   H.264/AAC `.mp4` with ffmpeg, muxing in that audio track.

## Regenerating

Requires: `piper-tts` (pip), a Piper voice model (`.onnx` + `.onnx.json`,
not committed here — ~60MB, fetched from the Piper GitHub releases), numpy,
Playwright + a Chromium build, and ffmpeg with libx264/aac.

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
