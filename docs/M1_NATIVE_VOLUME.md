# M1 experiment: first 50 seconds as native C++ / GLSL volume

**Status: engineering and image-quality experiment. No cinematic approval.**

The opening and inflation periods (0–20 and 20–50 seconds) now render directly in the original C++17/OpenGL 3.3 executable through a fullscreen GLSL fragment-raymarching pass, using the existing native HDR framebuffer, bloom and composite passes. The output is captured by the existing C++ `glReadPixels` PNG path. It does **not** invoke Blender or copy Blender rendered images.

## Rejected Blender reference: do not emulate overexposure

The Blender branch `visual/issue-2-coherent-opening-inflation`, Actions run [43629611663](https://github.com/IKitheka/primordial-universe-animation/actions/runs/43629611663) **passed CI but failed visual quality**. Actual frames at 10/25 seconds appear washed-out grey/white with dark flecks, and mean normalized luminance 0.7156/0.7890 respectively (versus previous 0.0003/0.0915). It should **not** be treated as an approved visual target. The native M1 shader is an independently restrained prototype that must pass its own visual review.

## Reference camera/time contract

Imported key positions + focal lengths for time 0,12,20,24,28,35,43,50s from the Blender source. Target is the origin; the Blender sensor width is 36mm and the scene uses 16:9 framing. Native camera vectors assume world Z up, and native vertical half-FOV is `(36mm/(width/height))/(2*focal_length_mm)`. Intermediate keys are *smoothstep approximations*, not the exact Blender FCurve Bezier handles or DOF. No claim of pixel parity yet.

The field uses camera-origin rays marching into a world-anchored sparse density distribution using deterministic 3D value noise and corrugated wave sheets. Scale length evolves smoothly through inflation. These are scientifically **illustrative fluctuations**, not measured inflation physics, and the film is not an explosion into pre-existing space. Keep field radiance low and avoid white-out, fake spheres, radial beams or homogeneous clouds.

## Native rendering tests

The workflow [`Native C++ preview`](../.github/workflows/native-cpp-preview.yml) renders bounded 480×270 frames at 0,10,18,20,25,30,45,50s using software Mesa/Xvfb. It checks CMake/CTest, compares `--time 25` to `--frame 751 --fps 30`, and inspects complete PNG CRC and decoded scanlines. A flat black frame is intentionally allowed at t=0, but other frames must be non-flat.

Review the *actual native images* for exposure, coherent 3D structure, continuous camera framing, aliasing and artificial geometry. Low-res single frames cannot establish full-rate motion quality. After first passing renders, do visual A/B against the previously approved reference where possible (not the rejected overexposed branch) and run a short consecutive-frame clip as a later M1 follow-up. This branch does not implement all eight scenes.

## Intentional M1 limits

- Only 0–50s is a new native GLSL scene. The later six scenes still display the old orange particle core/shockwave placeholder; the 50s handoff is not yet continuous and must not be visually approved.
- The native shader does not reproduce Cycles scattering, depth of field, denoising, automatic exposure or the exact Blender noise node graph; it is a GL3.3-compatible first approach.
- `Shader`/OpenGL context must successfully compile the new GLSL and render actual pixels on CI. Unit tests alone are not sufficient.
- Do not merge until owner has inspected and approved the native visual experiment. No full 4K render or paid cloud GPU job.
