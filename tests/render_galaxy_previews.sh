#!/usr/bin/env bash
# Bounded native C++ visual gate; no Blender/Python frame synthesis.
set -euo pipefail
BASE=work/reference/build/bigbang
CURRENT=build/bigbang
mkdir -p output/galaxy_review/{baseline,candidate,motion}
for t in 18 20 22 240 250 260 270 290; do
  for variant in baseline candidate; do
    exe="$CURRENT"
    if [ "$variant" = baseline ]; then exe="$BASE"; fi
    printf -v file 'output/galaxy_review/%s/t%s.png' "$variant" "$t"
    timeout 35s "$exe" --time "$t" --fps 30 --width 640 --height 360 \
      --output "$file" >/dev/null
  done
  echo "Native stills completed at t=$t"
done
for i in $(seq 0 20); do
  t="$(awk -v i="$i" 'BEGIN {printf "%.3f",270+i/5}')"
  printf -v file 'output/galaxy_review/motion/frame_%04d.png' "$i"
  timeout 35s "$CURRENT" --time "$t" --fps 30 --width 640 --height 360 \
    --output "$file" >/dev/null
done
echo 'Completed 21 C++ candidate motion frames at 5fps; 270–274s'
