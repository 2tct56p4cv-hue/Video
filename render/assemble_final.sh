#!/bin/bash
set -euo pipefail
SC="/tmp/claude-0/-home-user-Video/ff07980b-3dfb-56d1-a7c1-b99b6b65bd35/scratchpad"
cd "$SC"

TOTAL=$(python3 -c "import json;print(json.load(open('timeline.json'))['total'])")
echo "total=$TOTAL"

# 1) find the recorded webm
WEBM=$(ls video_raw/*.webm | head -1)
echo "webm=$WEBM"

# 2) mix narration (full) + music (ducked) into final audio track, padded to TOTAL+1s
ffmpeg -y -i audio/narration.wav -i audio/music.wav -filter_complex \
  "[0:a]volume=1.0[voice];[1:a]volume=0.35[mus];[voice][mus]amix=inputs=2:duration=longest:normalize=0[mixed];[mixed]apad,atrim=0:$(python3 -c "print($TOTAL+1.0)")[out]" \
  -map "[out]" -ar 44100 -ac 2 audio/final_audio.wav

# 3) re-encode webm to mp4 (h264) and mux with final audio
ffmpeg -y -i "$WEBM" -i audio/final_audio.wav \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest \
  -movflags +faststart \
  ../capco_technology_team.mp4

echo "DONE"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 ../capco_technology_team.mp4
