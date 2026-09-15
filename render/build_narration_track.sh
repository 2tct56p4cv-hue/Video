#!/bin/bash
set -e
SC="/tmp/claude-0/-home-user-Video/ff07980b-3dfb-56d1-a7c1-b99b6b65bd35/scratchpad"
AUD="$SC/audio"
cd "$AUD"

python3 - <<'PY'
import json
tl = json.load(open("../timeline.json"))
delays = []
for s in tl["scenes"]:
    delays.append((s["id"], int(round(s["voStart"]*1000))))
with open("delays.txt","w") as f:
    for sid, d in delays:
        f.write(f"{sid} {d}\n")
print(delays)
PY

INPUTS=()
FILTERS=()
LABELS=()
i=0
while read -r sid delay; do
  INPUTS+=(-i "${sid}_raw.wav")
  FILTERS+=("[$i:a]adelay=${delay}|${delay}[a$i]")
  LABELS+=("[a$i]")
  i=$((i+1))
done < delays.txt

FILTERCHAIN=$(IFS=';'; echo "${FILTERS[*]}")
MIXINPUTS=$(IFS=''; echo "${LABELS[*]}")
N=${#LABELS[@]}

ffmpeg -y "${INPUTS[@]}" -filter_complex "${FILTERCHAIN};${MIXINPUTS}amix=inputs=${N}:duration=longest:normalize=0[out]" -map "[out]" narration.wav

echo "done"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 narration.wav
