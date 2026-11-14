#!/usr/bin/env bash
# Runs inside a bounded Mesa/Xvfb context. Each image comes from C++ OpenGL.
set -euo pipefail
mkdir -p output/native/motion
for i in $(seq 0 40); do
  t="$(awk -v i="$i" 'BEGIN {printf "%.3f", 18.0 + i/10.0}')"
  printf -v file 'output/native/motion/frame_%04d.png' "$i"
  # 480x270, 41 frames, 18.0–22.0 seconds @ 10 samples/sec.
  timeout 30s ./build/bigbang --time "$t" --fps 30 \
    --width 480 --height 270 --output "$file" >/dev/null
  if (( i % 10 == 0 )); then echo "Native render: t=$t s, frame $i/40"; fi
done
