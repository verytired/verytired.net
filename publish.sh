#!/bin/zsh
# その日の分までをビルドして main に push する（launchd から毎日実行）
set -e
cd "${0:A:h}"
python3 build.py
git add -A
git diff --cached --quiet && exit 0
git commit -q -m "publish $(date +%F)"
git push -q origin HEAD:main
