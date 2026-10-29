#!/bin/bash
# 素材の動画5本を Google Flow（Veo 3.1 Lite、9:16、8秒、720p）で作る。flow-poster の flow_automation.py を使う
# flow_automation.py は、ひとつ前に作った動画を新しい動画と取り違えて保存することがある（2026-10-30 に5本中4本がずれた）。
# 作ったら1本ずつコマを見て、場面とファイル名が合っているか確かめる
OUT="$(cd "$(dirname "$0")" && pwd)"
cd ~/Workspace/flow-poster
S="Rendered like a late-1990s CGI screensaver: early 3D, smooth plastic shading, soft bloom glow, saturated blue sky colors, dreamlike, nostalgic, no people faces, no text."
venv/bin/python flow_automation.py new-project --name hitori-av-2026-11-08
gen(){ venv/bin/python flow_automation.py generate-video "$2 $S" --out "$OUT" && f=$(ls -t "$OUT"/flow_video_*.mp4 | head -1) && mv "$f" "$OUT/$1_v1.mp4"; echo "== $1 $?"; }
gen door "A lone white wooden door stands in a bright green grassy hill under a blue sky with fluffy white clouds. The door slowly swings open, revealing a starry purple galaxy inside. The camera slowly pushes toward the door."
gen tv "An old CRT television sits alone in a field of tall grass at golden hour. Its screen shows drifting clouds. The camera slowly dollies into the screen until the clouds fill the frame."
gen jelly "Huge translucent glowing jellyfish float slowly above an empty suburban street at dusk, pastel pink and blue sky, streetlights flicker on. Slow upward camera tilt."
gen chrome "Shiny chrome spheres float above an endless black and white checkerboard floor stretching to the horizon under a gradient purple and cyan sky. The camera glides forward smoothly."
gen moon "An empty merry-go-round carousel slowly turns, lights glowing, alone on the grey surface of the moon. The blue Earth hangs in the black starry sky. Slow orbiting camera."
