# Big Bang: native C++ / OpenGL animation

A deterministic, five-minute educational visualization of cosmic history, built with C++17, OpenGL 3.3 Core and GLSL. The native engine draws the images; Python coordinates capture and validation, and FFmpeg encodes the video. The story progresses from ignition and expansion through cooling, nucleosynthesis, recombination, cosmic dawn, galaxies and the Solar System/Earth finale.

## Release status

This branch continues V11 at commit 127b96ca1ca74c2eebf7fb5ef0ca03e5f9f5f9dc and preserves the V4–V11 history. Native UHD batch capture (3840 x 2160) is enabled, with regression coverage and a bounded five-scene validation workflow. **The final 4K film and university submission package are not yet verified or released.** Passing a short preview does not establish final-film acceptance or artistic approval.

The successful [V11 Full HD production](https://github.com/IKitheka/bigbang/actions/runs/43738384428) is prior 1920 x 1080 work. Its output must not be described as native 4K. No production scene shader is changed by the initial UHD-enablement work, including the approved 260–300-second Solar System/Earth sequence.

## Ubuntu dependencies

The build requires CMake 3.20+, a C++17 compiler, GLFW 3.3+, GLM and OpenGL 3.3 Core. CMake fetches GLAD v2.0.8 from its upstream Git repository, so the first configure requires network access. Headless rendering uses Xvfb and a working Mesa software driver. Python 3, FFmpeg and FFprobe are needed for capture/verification; NumPy is needed by the original-score generator.

~~~bash
sudo apt-get update
sudo apt-get install --no-install-recommends -y build-essential cmake git libglfw3-dev libglm-dev libgl1-mesa-dev libgl1-mesa-dri xvfb xauth ffmpeg python3 python3-numpy
~~~

A working desktop GPU driver can be used instead of software OpenGL. Actual supported driver/package versions and performance must be taken from the build/render logs; a GPU has not been established merely by requesting an OpenGL context.

## Build and test from a clean checkout

~~~bash
git clone --branch release/native-4k-university-final https://github.com/IKitheka/bigbang.git
cd bigbang
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
python3 -m unittest discover -s tests -p test_film_render.py -v
~~~

The CMake build embeds this checkout's absolute source directory as PROJECT_ROOT. Build after extracting/moving the source archive; do not relocate an old binary and assume its shader paths remain valid. Shader includes are loaded by the native Shader implementation.

## Run and capture

Run the interactive animation on a desktop display; Escape exits:

~~~bash
./build/bigbang
~~~

Query the actual rendering driver without scene rendering:

~~~bash
./build/bigbang --renderer-info
~~~

Capture a genuine native UHD still at a specified global time:

~~~bash
mkdir -p output/stills
./build/bigbang --time 292 --fps 30 --width 3840 --height 2160 --output output/stills/earth-4k.png
~~~

First run a bounded native UHD check, then inspect the image, motion and timing:

~~~bash
python3 scripts/render_film.py --binary build/bigbang --output-dir output/uhd-check --first-frame 901 --end-frame 903 --width 3840 --height 2160 --fps 30 --chunk-frames 1 --chunk-timeout 150 --preset fast --crf 16
~~~

For headless software capture, prefix the Python capture command with:

~~~bash
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 3840x2160x24'
~~~

The prefix and capture command belong on the same shell command line. The [bounded UHD workflow](.github/workflows/native-4k-validation.yml) supplies complete examples and preserves native previews, manifest/checkpoint JSON, checksums and failure logs. The current workflow samples three native frames each at ignition, expansion, the molecular cloud and Earth, checkpointing every frame to bound software-render cost. A completed thirty-frame native UHD galaxy sample is retained in [the initial benchmark run](https://github.com/IKitheka/bigbang/actions/runs/43744398179#summary-132904383560). The expansion sample exceeded its initial 270-second budget for fifteen frames; the expensive initial run was stopped and its evidence preserved. Three-frame pilots measure capture feasibility and timing; they are insufficient for motion-quality acceptance. These samples have no soundtrack and are not final deliverables.

After performance, visual and resource checks pass, this explicit invocation requests all 9,000 native UHD frames:

~~~bash
python3 scripts/render_film.py --binary build/bigbang --output-dir output/uhd-production --first-frame 1 --end-frame 9000 --width 3840 --height 2160 --fps 30 --chunk-frames 150 --chunk-timeout 1800 --preset fast --crf 16
~~~

This command produces a silent picture track called film.mp4. It does not produce the final sound master, documentation or GitHub Release. Production should be segmented to suit measured hardware limits. Existing V11 assembly scripts enforce 1080p provenance and are historical delivery tools, not a validated 4K assembly path.

Resume a matching output directory using the identical capture command plus --resume. Resume validates source, binary, driver, environment, dimensions, codec and checksums; changed identity is rejected. Verified chunks survive interruption. Never combine different sources or settings without explicit validation.

## Frame and output contract

Frame numbers are one-based and inclusive: frame N samples (N-1)/30 seconds. Frames 1–9000 occupy exactly 300 seconds of 30 FPS playback; the last sample is 299.9666667 seconds. The engine verifies actual framebuffer dimensions against the requested capture size. Batch output is top-down RGB24, with diagnostic text separated from its byte stream. FFmpeg encodes H.264/yuv420p; chunk validation counts decoded frames and performs a full strict decode.

The final sound master must separately pass exact 3840 x 2160 geometry, 30 FPS, 9,000 decoded frames, 300-second duration, synchronized stereo audio, transition review and full-film audiovisual review. Release assets must be uploaded and downloaded/validated before availability is claimed.

## Source layout and demonstration

| Location | Role |
| --- | --- |
| src/main.cpp | OpenGL context, deterministic capture loop, scene passes, composition and readback |
| include/FilmClock.hpp, RenderOptions.hpp | Frame/time contract and validated CLI options |
| include/CinematicTimeline.hpp, UniverseCamera.hpp | Story-time compression, camera and target motion |
| include/GalaxyCatalog.hpp | Procedural 3D galaxy catalogue |
| shaders/postprocess/ | Native ray-marched cosmic scenes, Sun/planets, bloom and composite shaders |
| src/HDRFramebuffer.cpp, BloomEffect.cpp | HDR target management and post-processing |
| scripts/render_film.py | Checkpointed native capture, encoding and decode verification |
| scripts/create_original_score.py | Original deterministic score synthesis |
| tests/ | Native clock/camera/CLI/PNG tests and Python pipeline regression tests |
| docs/ | Development references and implementation evidence |

For a lecturer demonstration: build and run the application, capture a known time, show its corresponding shader and draw call, then show the capture manifest and decode checks. The repository's [nine-stage explanation](docs/RENDERING_PIPELINE.md) uses a conceptual scene-to-framebuffer model. A separate lecturer rubric has not been supplied. Tessellation, geometry-shader processing and stencil operations must not be claimed simply because OpenGL supports them; the current main film primarily rasterizes screen geometry and computes implicit scene shading in fragment shaders.

## Scientific and artistic scope

This is a compressed educational film, not a calibrated cosmological simulation. Ignition, shockwave-like structures, visible colors, distances, camera travel and epoch durations are artistic representations. The Big Bang is not a conventional explosion into pre-existing empty space. The original soundtrack is artistic accompaniment and does not imply acoustic propagation through a vacuum.

See the [story reference](docs/CINEMATIC_STORY_REFERENCE.md), [implementation and limits](docs/NATIVE_FILM_REVIEW.md) and [V11 delivery evidence](docs/V11_TRUE_NATIVE_FULL_HD_FINAL_DELIVERY.md). Preserve these records when preparing the final submission; distinguish prior results from checks actually rerun on the final source commit.
