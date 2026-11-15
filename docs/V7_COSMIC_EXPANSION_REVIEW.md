# V7 expansion milestone — cinematic 0–50 second handoff

## Intent
Follow the owner-requested **bright violet-white ignition** with a clearly visible, continuous cosmic expansion sequence from **18–50 seconds**. The previous native V4/V5 cinematic material at 50–300 seconds, particularly the approved 260–300-second Solar System formation/Earth finale, must remain unchanged.

This is an **original artistic representation** of expanding spatial correlations and early radiation. It is not a physical simulation of inflation, observed Big Bang photography, an explosion into existing space, or a representation of early galaxies/stars in the 18–50s epoch.

## Native C++/GLSL implementation
- `shaders/postprocess/nasa_origin.frag`: increase the constrained 5.9s violet-white ignition pulse. Retain alpha fade to exactly zero by 18s.
- `shaders/postprocess/primordial_volume.frag`: new spatially coherent, evolving volumetric emission from 17.5–50s, supplementing—not replacing—the original sparse early radiation folds.
- Maintain V4 camera, 64-step integration, native HDR exposure/bloom, original soundtrack and all later C++ scenes.
- Avoid stars, shell debris, literal spacetime grid, dense galaxy-like cosmic web and sudden whiteout.
- `expansionWeight` reaches **exactly zero at >=50s**, while the original volume and QGP shaders continue unchanged.

## Preview evidence available
A **separate 2D artistic looktest** using GLSL 330 compiled/rendered with local Mesa OpenGL through EGL:
- 50.000s, 1500 frames, 640×360, 30fps, H.264, AAC stereo from the recovered V4 original soundtrack.
- FFprobe frame/duration checks and full FFmpeg video+audio decode passed.
- Note: this demonstration combines the earlier V6 bright ignition with an art-direction field over preserved V4 frames. It is **not** a native C++ production render of the exact 3D `primordial_volume.frag`; the final native C++ appearance must be assessed independently.

## Acceptance gates before any full-length render
1. Run bounded C++/Mesa native pipeline still/motion previews on this branch.
2. Inspect frames and *consecutive* frames at t=16,17,18,20,22,25,30,35,40,45,48,50,52,55.
3. Check visible non-star spatial structures; no flat-black interval or abrupt 18s/50s transition; check exposure and temporal shimmer at full 30fps.
4. Verify native frames at t>=50 remain identical to the V5 parent branch for unaffected shaders, except at the expected cosmic transition boundary when shaders are blended. Verify 260–300s solar system unmodified.
5. Owner reviews 0–50s cinematic look and only then approves rerendering/replacing the long-form film.

**Status:** V7 candidate, native artistic validation pending; no 9,000-frame render authorized; never overwrite recovered V4 final.
