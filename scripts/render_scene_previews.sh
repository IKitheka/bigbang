#!/usr/bin/env bash
# Short, independently reviewable scene previews. All visuals come from
# ./build/bigbang C++/OpenGL/GLSL. ffmpeg only encodes native RGB24 frames.
set -euo pipefail

binary="${1:-./build/bigbang}"
out="${2:-output/scene_review}"
mkdir -p "$out/stills" "$out/clips" "$out/logs" "$out/contact"
: > "$out/scene_reel_concat.txt"

# Each row: chapter name, clip starting second, four still times.
scenes=(
  'origin 10 5 10 15 19'
  'inflation 35 22 30 40 48'
  'qgp 68 55 65 75 85'
  'nucleosynthesis 107 95 105 115 125'
  'opaque_plasma 148 135 145 155 165'
  'recombination 183 173 181 191 198'
  'dark_ages 217 205 215 225 235'
  'cosmic_dawn 271 244 258 275 295'
)
scene_id=0
for record in "${scenes[@]}"; do
  read -r label second t0 t1 t2 t3 <<< "$record"
  echo "Native C++ scene ${scene_id}: ${label} (${second}s, 2s clip)"
  still_id=0
  for t in "$t0" "$t1" "$t2" "$t3"; do
    printf -v ix '%02d' "$scene_id"
    printf -v jx '%02d' "$still_id"
    target="$out/stills/scene_${ix}_${jx}_t${t}.png"
    timeout 75s "$binary" --time "$t" --fps 30 \
      --width 480 --height 270 --output "$target" \
      > "$out/logs/still_${ix}_${jx}.log" 2>&1
    still_id=$((still_id+1))
  done

  # Continuous 2-second native draw sequence, with a SINGLE GL context.
  # The C++ renderer restricts batch fps to 30/60, so use 30fps honestly.
  first=$((second*30+1))
  last=$((first+59))
  printf -v ix '%02d' "$scene_id"
  timeout 180s "$binary" --start-frame "$first" --end-frame "$last" \
    --fps 30 --width 480 --height 270 --raw-video - \
    2>"$out/logs/clip_${ix}.log" |
      ffmpeg -hide_banner -loglevel error -y -f rawvideo -pix_fmt rgb24 \
        -video_size 480x270 -framerate 30 -i pipe:0 \
        -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
        -movflags +faststart "$out/clips/${ix}_${label}.mp4" \
        2>"$out/logs/ffmpeg_${ix}.log"
  printf "file 'clips/%s'\n" "${ix}_${label}.mp4" >> "$out/scene_reel_concat.txt"
  ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 \
    "$out/clips/${ix}_${label}.mp4" >"$out/logs/duration_${ix}.txt"
  scene_id=$((scene_id+1))
done

ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 \
  -i "$out/scene_reel_concat.txt" -c copy -movflags +faststart \
  "$out/scene_reel_8_epochs_16s.mp4"

# Ordered stills and fixed-size contact tiles: 4 columns = four moments per
# chapter; eight rows = eight chapters. No Python-generated visual pixels.
i=0
for png in "$out"/stills/scene_*.png; do
  printf -v idx '%02d' "$i"
  cp "$png" "$out/contact/frame_${idx}.png"
  i=$((i+1))
done
test "$i" -eq 32
ffmpeg -hide_banner -loglevel error -y -framerate 1 \
  -i "$out/contact/frame_%02d.png" \
  -vf 'tile=4x8:margin=8:padding=8:color=black' \
  -frames:v 1 "$out/storyboard_8x4.png"

sha256sum "$out"/stills/*.png > "$out/native_still_sha256.txt"
ffprobe -v error -count_frames \
  -show_entries format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_read_frames \
  -of json "$out/scene_reel_8_epochs_16s.mp4" > "$out/reel_metadata.json"
printf 'renderer=Native C++17/GLSL (FFmpeg only encodes)\nsource_commit=%s\n' \
  "${GITHUB_SHA:-local-checkout}" > "$out/provenance.txt"
echo "PASS: Eight independent native C++ scene clips and 32 stills created."
