#!/usr/bin/env bash
set -euo pipefail
OUT=output/nasa2007_native
mkdir -p "$OUT"/{baseline,candidate,motion}
for t in 0 2 5 8 12 16 18 20 22 50 55 100 245 250 255 260 270 280 290 299; do
  timeout 35s build/bigbang --time "$t" --fps 30 --width 640 --height 360 \
    --output "$OUT/candidate/t${t}.png" >/dev/null
  # V7 intentionally revises 18-50s. Guard unchanged V5-parent shots
  # AFTER the new expansion gate reaches exactly zero at t=50.
  if [ "$t" = 50 ] || [ "$t" = 55 ] || [ "$t" = 100 ] ||
     [ "$t" = 260 ] || [ "$t" = 290 ]; then
    timeout 35s work/baseline/build/bigbang --time "$t" --fps 30 \
      --width 640 --height 360 --output "$OUT/baseline/t${t}.png" >/dev/null
    cmp "$OUT/candidate/t${t}.png" "$OUT/baseline/t${t}.png" \
      || { echo "Unrelated V5 parent scene changed at t=$t" >&2; exit 1; }
  fi
  echo "Verified C++ frame t=$t"
done
for i in $(seq 0 40); do
  t="$(awk -v i="$i" 'BEGIN {printf "%.3f",276+i/10.0}')"
  printf -v path "$OUT/motion/frame_%04d.png" "$i"
  timeout 35s build/bigbang --time "$t" --fps 30 --width 640 --height 360 \
    --output "$path" >/dev/null
done
