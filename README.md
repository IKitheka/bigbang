# Native universe film

C++17 / GLFW / GLAD / GLM / OpenGL 3.3 and GLSL render a deterministic, 300-second cinematic interpretation of cosmic history. Every movie pixel comes from the native renderer. Python supervises and verifies captures; FFmpeg encodes them.

This branch replaces the later orange-particle prototypes with continuous world-space volumes, recombination, subdued dark ages and procedural stellar/galaxy formation. It preserves the approved 18–22 second shader, camera, HDR and composite path. This is a review film, not an approved photorealistic or quantitative cosmological simulation.

## Build and verify

Ubuntu dependencies: CMake 3.20+, a C++17 compiler, Git, GLFW 3.3, GLM and OpenGL development libraries. CMake fetches GLAD v2.0.8. FFmpeg and Python 3 are needed for movie delivery. Headless captures need Mesa, Xvfb and xauth.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
python3 -m unittest discover -s tests -p 'test_film_render.py' -v
```

## Capture

From a desktop with a working OpenGL display:

```sh
# Genuine native still.
./build/bigbang --time 185 --fps 30 --width 960 --height 540 --output output/t185.png
# Bounded two-second pipeline check.
python3 scripts/render_film.py --binary build/bigbang --output-dir output/check --end-frame 60
# Explicit complete 1080p review invocation: 9000 native frames, 300 seconds.
python3 scripts/render_film.py --binary build/bigbang --output-dir output/review1080 --width 1920 --height 1080 --fps 30 --crf 16
# Resume only the same source, binary, driver and settings.
python3 scripts/render_film.py --binary build/bigbang --output-dir output/review1080 --width 1920 --height 1080 --fps 30 --crf 16 --resume
```

For headless use, prefix the invocation with `LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a`. Check benchmarks first: the software driver can be much slower than a desktop GPU. No movie runs automatically at application launch. Batch review dimensions are capped at 1920×1080. The interactive defaults and single-frame capture interface remain available.

Frames are one-based and sample `(frame-1)/fps`. At 30 fps, frames 1–9000 cover exactly 300 seconds of playback, with the last sample at 299.966667 seconds. One native process/context renders each chunk. Completed chunks receive hashes, metadata and full decode checks before checkpointing. A final MP4 is published only after all required frames validate. Never describe a partial artifact as a completed film.

The existing bounded Actions previews remain in place. `Complete native review film` adds an independently rebuilt protected-opening comparison and a full 640×360/30 fps review with 30-day artifacts. CI success verifies engineering, not artistic approval. See [rendering stages](docs/RENDERING_PIPELINE.md), [implementation and limits](docs/NATIVE_FILM_REVIEW.md), and the original [story contract](docs/CINEMATIC_STORY_REFERENCE.md).
