# M0 native C++ renderer: frame-seek and PNG proof

This stage is **engineering infrastructure**, not the cinematic parity milestone. It runs the original C++ OpenGL particle/HDR/bloom pipeline at a deterministic 300-second film time and exports actual pixels via `glReadPixels` and a C++ PNG encoder. Blender and Python do **not** generate these images. The art is still the old particle/shockwave prototype; visual parity with the Blender opening/inflation remains M1.

## Ubuntu build

Requirements: CMake 3.20+, C++17, GLFW 3.3, GLM, OpenGL development libraries; first CMake configuration downloads GLAD v2.0.8 from GitHub.

```bash
sudo apt update
sudo apt install -y build-essential cmake git libglfw3-dev libglm-dev libgl1-mesa-dev

cd ~/bigbang
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
ctest --test-dir build --output-on-failure
```

## Native image capture

Requires an actual OpenGL context. On a desktop session, a hidden GLFW window is created for each capture, then destroyed. On headless Linux use `xvfb-run` and Mesa/X11; test driver support before claiming it works on your machine.

```bash
./build/bigbang --time 25 --fps 30 --width 480 --height 270 --output output/native/t25.png
./build/bigbang --frame 751 --fps 30 --width 480 --height 270 --output output/native/frame751.png
cmp output/native/t25.png output/native/frame751.png
./build/bigbang --frame 1 --fps 30 --width 480 --height 270 --output output/native/first.png
python3 tests/inspect_native_png.py output/native/first.png output/native/t25.png --width 480 --height 270
```

- `--time` and `--frame` are mutually exclusive, and must accompany `--output`. Frame 1 = t=0; frame 751 at 30fps = t=25; 300s is the exclusive endpoint.
- `--fps` is 30 or 60. `--width` and `--height` default to 1280×720, with a one-frame upper bound of 4096 pixels per dimension.
- Without `--output`, the program keeps its original interactive mode (`./build/bigbang`). `--help` does not initialize OpenGL.
- Capture uses **exact requested seconds** for `--time` (plus a nearest frame label), or exact rational frame time for `--frame`.
- Native PNG images are RGB8, top-down, from a bottom-up OpenGL readback, in the current shader's gamma-mapped SDR output. The C++ writer uses valid PNG CRC and stored DEFLATE blocks; files can be larger than compressed PNGs. C++ reads final composited pixels, not EXR/HDR float masters.
- The image parser and unit tests validate PNG structure, zlib/CRC, non-flat pixels and deterministic time mapping. **They do not assess artistic fidelity**, continuity or agreement with Blender.
- For headless CI, the `Native C++ preview` workflow builds the program on an ephemeral Ubuntu runner, runs tests under Mesa/Xvfb, captures time 0/25s and repeats time 25 via a frame seek. Artifacts are limited to small native PNGs and logs and expire after seven days. No production sequence.

## M0 limitations and M1 next step

- C++ currently renders the old 20k-particle core/shockwave look at arbitrary timeline times. The shader, camera and all other six scenes are **not** yet ported from Blender.
- Current point-sprite shader represents an early OpenGL experiment, not path-traced primordial physics. It is not scientific proof.
- Blender 10/18/20/25/30/45/50s camera and field settings should be exported into a versioned schema and recreated in GLSL fragment-raymarching in M1. Match C++ and Blender composition/FOV and restrained exposure first.
- Before full native rendering, add contiguous multi-frame export, checked resume and production-approved scaling; do not reuse reference PNGs as native output.
