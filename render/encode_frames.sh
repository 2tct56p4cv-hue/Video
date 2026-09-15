#!/bin/bash
# Encode the lossless PNG frame sequence + mixed soundtrack into a high-quality H.264 MP4.
set -euo pipefail
SC="/tmp/claude-0/-home-user-Video/ff07980b-3dfb-56d1-a7c1-b99b6b65bd35/scratchpad"
cd "$SC"
TOTAL=$(python3 -c "import json;print(json.load(open('timeline.json'))['total'])")
OUT="${1:-../capco_technology_team.mp4}"
ffmpeg -nostdin -y -framerate 25 -i frames/%06d.png -i audio/final_audio.wav \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.1 -x264-params keyint=125:min-keyint=25 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,apad" -t "$(python3 -c "print($TOTAL+1.0)")" \
  -c:a aac -profile:a aac_low -ar 48000 -ac 2 -b:a 192k \
  -metadata:s:a:0 language=eng -disposition:a:0 default \
  -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$OUT"
