#!/usr/bin/env bash
set -euo pipefail
OUT=output/nasa2007_native
mkdir -p "$OUT"/{baseline,candidate,motion}
for t in 0 2 5 8 12 16 18 20 22 245 250 255 260 270 280 290 299; do
  timeout 35s build/bigbang --time "$t" --fps 30 --width 640 --height 360 \
    --output "$OUT/candidate/t${t}.png" >/dev/null
  if [ "$t" = 18 ] || [ "$t" = 20 ] || [ "$t" = 22 ]; then
    timeout 35s work/baseline/build/bigbang --time "$t" --fps 30 \
      --width 640 --height 360 --output "$OUT/baseline/t${t}.png" >/dev/null
    cmp "$OUT/candidate/t${t}.png" "$OUT/baseline/t${t}.png" \
      || { echo "Protected scene changed at t=$t" >&2; exit 1; }
  fi
  echo "Verified C++ frame t=$t"
done
for i in $(seq 0 40); do
  t="$(awk -v i="$i" 'BEGIN {printf "%.3f",276+i/10.0}')"
  printf -v path "$OUT/motion/frame_%04d.png" "$i"
  timeout 35s build/bigbang --time "$t" --fps 30 --width 640 --height 360 \
    --output "$path" >/dev/null
done
