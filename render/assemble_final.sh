#!/bin/bash
set -euo pipefail
SC="/tmp/claude-0/-home-user-Video/ff07980b-3dfb-56d1-a7c1-b99b6b65bd35/scratchpad"
cd "$SC"
TOTAL=$(python3 -c "import json;print(json.load(open('timeline.json'))['total'])")
WEBM=$(ls video_raw/*.webm | head -1)
ffmpeg -y -i "$WEBM" -i audio/final_audio.wav \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset medium -crf 26 -pix_fmt yuv420p -profile:v high -level 4.0 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,apad" -t "$(python3 -c "print($TOTAL+1.0)")" \
  -c:a aac -profile:a aac_low -ar 48000 -ac 2 -b:a 160k \
  -metadata:s:a:0 language=eng -disposition:a:0 default \
  -movflags +faststart ../capco_technology_team.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 ../capco_technology_team.mp4
ffmpeg -i ../capco_technology_team.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
