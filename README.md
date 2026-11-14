# Big Bang — native C++ graphics renderer

This repository is the **final C++ implementation** for the owner's 300-second, eight-scene Big Bang / early-universe cinematic animation. The existing code is a C++17 OpenGL 3.3 prototype using GLFW, GLAD, GLM, HDR framebuffers, a particle point renderer, GLSL and bloom. **The current prototype is not yet a verified finished animation.**

## Relationship to the Blender reference

The separate repository [primordial-universe-animation](https://github.com/IKitheka/primordial-universe-animation) uses Blender/Python/Cycles to **design, evaluate and approve the visual look**. The final 300-second film must be **rendered from this C++ application**. Blender images are reference targets only, not frames to relabel as C++ output. Python scripts may prepare/import scene data, but the final rendering must be executed by C++/GLSL without requiring Blender at render time.

See [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md) for parallel milestones, interchange design, a nine-stage pipeline, native render acceptance gates, C++ build/test priorities and production approvals.

## Existing development build (Ubuntu)

System dependencies: CMake 3.20+, C++17 compiler, OpenGL development libraries, GLFW 3.3+, GLM. CMake fetches GLAD (internet access needed at first configure).

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
./build/bigbang
```

The current program opens an interactive OpenGL window and renders the earlier particle-based test. This is *not* yet the automated 300-second C++ cinematic renderer, and current camera, art and timeline do not match the Blender references. No offscreen or CLI frame exporter is claimed until implemented and tested.

## Immediate next development work

1. Add deterministic time/frame evaluation and native PNG export.
2. Define a renderer-neutral Blender-to-C++ camera and scene-data contract.
3. Reimplement and compare the **0–50 second** opening/inflation scene in OpenGL/GLSL.
4. Extend to six remaining scenes only after early native-reference parity is demonstrated.

**No full 4K run or paid cloud/GPU rendering without explicit owner approval.**
