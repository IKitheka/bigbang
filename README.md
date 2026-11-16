# Big Bang — V12 planetary formation focus (university graphics project)

C++17 / OpenGL 3.3 Core / GLSL 330 / GLFW / GLAD / GLM native rendering. Five-minute (300-second) cinematic visualization at 30 frames per second; production goal is 9,000 actual 1920×1080 frames with an original deterministic stereo score.

**Status: V12 is a lecturer-feedback revision, not yet a validated full movie.** The completed [V11 1080p film](https://github.com/IKitheka/bigbang/actions/runs/43738384428/artifacts/14172696894) remains the reliable backup. Do not submit a V12 preview as a complete 1080p master.

## Lecturer review and new emphasis

The lecturer requested a shorter cosmic/darkness sequence and much stronger planet-formation coverage. V12 now allocates approximately 2:00 to the Big Bang, early universe, first galaxies and molecular-cloud bridge, followed by approximately **3:00 of young Sun, circumstellar disc, visible dust clumps, planetesimal/embryo growth, eight planets and the Earth fly-in**.

The story is deliberately cinematic, not a quantitative N-body/accretion simulation. Physical times, sizes, velocities and orbital distances are greatly compressed. See [V12 director's notes and timeline](docs/V12_LECTURER_REVIEW.md) and the [nine conceptual graphics rendering stages](docs/RENDERING_PIPELINE.md).

## Build on Ubuntu

```bash
sudo apt update
sudo apt install -y build-essential cmake git libglfw3-dev libglm-dev \
  libgl1-mesa-dev libgl1-mesa-dri xvfb xauth ffmpeg python3-numpy
git clone --branch feature/v12-planetary-formation-focus https://github.com/IKitheka/bigbang.git
cd bigbang
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
python3 -m unittest discover -s tests -p test_film_render.py -v
```

The first CMake configuration fetches GLAD 2.0.8 and needs internet. `PROJECT_ROOT` is embedded at build time, so recompile after moving the checkout.

## Run and inspect the film

```bash
./build/bigbang
./build/bigbang --renderer-info
mkdir -p output/stills
./build/bigbang --time 204 --fps 30 --width 960 --height 540 --output output/stills/planetesimals.png
./build/bigbang --time 253 --fps 30 --width 960 --height 540 --output output/stills/protoplanet.png
./build/bigbang --time 297 --fps 30 --width 960 --height 540 --output output/stills/earth.png
```

To record a native 1080p clip under an Ubuntu display:

```bash
python3 scripts/render_film.py --binary build/bigbang \
  --output-dir output/v12_solar_preview --first-frame 7501 --end-frame 7560 \
  --width 1920 --height 1080 --fps 30 \
  --chunk-frames 30 --chunk-timeout 900 --preset fast --crf 18
```

For headless CPU rendering, prefix the Python command with `LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1920x1080x24'`. Source frame IDs are one-based; frame N samples (N-1)/30 seconds. Do not confuse a 2-second preview with a complete movie.

## Native production and automated validation

- [V12 native preview workflow](.github/workflows/v12-planetary-preview.yml) compiles and tests from scratch, captures real stage frames and four consecutive 2-second scenes, and verifies the revised original score.
- [V12 full native 1080p workflow](.github/workflows/v12-native-1080p-fullfilm.yml) distributes thirty nonoverlapping 300-frame sections. On success it invokes [V12 film assembly](scripts/assemble_v12_true1080p.py), which checks exact source commit, native resolution, decoded frame counts, H264, 300-second duration, stereo AAC, full decode and chapter transition metrics.
- Movie previews and automated tests are engineering evidence, not proof of scientific calibration or subjective artistic approval.

## Main source files

`src/main.cpp` implements OpenGL context, scene routing, framebuffer HDR/bloom and readback.
`include/CinematicStory.hpp` defines narrative chapters, `include/CinematicTimeline.hpp` remaps deterministic scene time.
`shaders/postprocess/primordial_volume.frag`, `cosmic_evolution.frag` and `galaxy_to_solar_bridge.frag` render the first two minutes.
`shaders/postprocess/solar_system.frag` and `protoplanetary.glsl` render the young Sun, world-space clumps, analytic accreting objects, mature planets, rings and Earth.
`scripts/create_original_score.py` synthesizes original stereo music.

There are nine **narrative** chapters and separately nine **conceptual rendering-pipeline** stages; these are not the same thing. Optional tessellation/geometry shader stages are not implemented by this OpenGL 3.3 film.
