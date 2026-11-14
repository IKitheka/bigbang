# Native C++ film — agent instructions

## Owner's mandatory delivery rule
- The final 300-second film **must be rendered by this C++ application**, not merely played, wrapped or encoded by C++ from Blender/Python-rendered frames.
- Blender/Python in `IKitheka/primordial-universe-animation` is for visual design, test references and data export. Follow [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md).
- Preserve the eight-scene windows and the actual nine pipeline stages. Use deterministic 1-indexed frame mapping `t=(frame-1)/fps`. Deliver working C++ code and recorded native render evidence.
- Use the existing C++17 / GLFW / GLAD / GLM / OpenGL 3.3 / HDR FBO / bloom stack unless a measured reason supports a change. Do not assume compute shaders are available on OpenGL 3.3.
- Keep C++ render and Blender reference comparison separate; never claim copied reference images are C++ outputs.
- Initial task: native deterministic timeline and frame export, followed by porting the 0–50 second opening/inflation. Build/test first, review actual C++ render output, then expand.

## Safe engineering workflow
- Work in focused feature branches and leave PRs unmerged for owner approval.
- Preserve existing source/code unless the change is explicitly scoped; do not alter unrelated branches/PRs.
- No production-length or 4K full render, expensive cloud/GPU worker, new credentials, or installation of runners without owner approval.
- Label speculative Planck/inflation illustrations and differentiate physically inspired approximations from simulations. Track source SHA and frame times in tests.
