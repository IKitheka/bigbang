#!/usr/bin/env bash
# Preview-only: 41 C++/GLSL native frames from 47.0–55.0s at 5fps.
# The intermediate scene is an illustrative QGP bridge, not final M2 physics.
set -euo pipefail
mkdir -p output/native/boundary
for i in $(seq 0 40); do
  t="$(awk -v n="$i" 'BEGIN {printf "%.3f",47.0+n/5.0}')"
  printf -v file 'output/native/boundary/frame_%04d.png' "$i"
  timeout 30s ./build/bigbang --time "$t" --fps 30 \
    --width 480 --height 270 --output "$file" >/dev/null
  if (( i % 5 == 0 )); then echo "Boundary sample t=$t s ($i/40)"; fi
done
