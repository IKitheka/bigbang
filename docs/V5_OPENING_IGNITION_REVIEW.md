# V5 opening ignition — bounded visual experiment

## Target and scope
Continue the owner-approved V4 C++/GLSL film at `feature/v4-protoplanetary-formation-cinematic` with an original violet-white Big Bang look inspired by NASA Goddard 2007 SVS #10128. This is **not** NASA footage, a physical explosion or a quantitative inflation solver.

Only `shaders/postprocess/nasa_origin.frag` changes. The nebula, eight forming planets, Earth flyby, original soundtrack, native timeline, middle epochs, HDR pipeline and nine documented conceptual graphics-pipeline stages remain unchanged. In particular the V4 native Solar System at t=260–300 s is protected.

## Visual issues identified in recovered V4
- 4–8 s: circular luminous ring and stiff symmetrical optical spikes
- 8–15 s: nearly screen-wide pale monochrome cloud with weak depth and contrast
- 15–18 s: visually difficult handoff from bright cloud to existing dark spatial field

## V5 source modifications
- Break rotational symmetry using coherent, slowly varying noise for irregular violet-white expanding front
- Layer an animated turbulent interior with blue-violet emission and localized highlights
- Add dark, shadowed cloud folds to avoid flat global grey exposure
- Concentrate the transient flash near the seed; retain familiar opening timing
- Blend this opening overlay away using alpha `cover = 1.0 - smoothstep(14.5,18.0,t)`. At t>=18 the overlay is exactly transparent, preserving original underlying V4 frames (actual C++ production render to verify).

## Evidence obtained locally
- GLSL 330 shader compiled and linked under Mesa llvmpipe OpenGL 4.5 using an actual offscreen EGL context.
- 20-second 640x360 looktest rendered at 30 fps as 600 actual GLSL frames, tone-mapped using a **preview-only** operator and composited against the recovered V4 master.
- Original five-minute V4 soundtrack excerpt included (AAC stereo).
- FFprobe verified H.264 / yuv420p / 640x360 / 30 FPS / 600 frames / 20.000 s; FFmpeg full decode passed.
- Local preview source SHA256: `30395c33b2f16c89a67f9d5838c330affdd967bd628db02d8d6bf045013e9d25`.
- Local 20-second preview SHA256: `84f68bd9d7c2333a583bd2186012580b11f4699e4ac6372e29195ba7d6add68d`.

## Quality gate before acceptance
1. Run existing native C++ bounded NASA-style still/motion looktests for this branch. The local EGL composition is a looktest, **not a substitute** for that native renderer or production HDR/bloom.
2. Compare representative frames at 3, 5, 7, 9, 12, 15, 17, 18, 20 and 22 seconds with V4 using actual C++ outputs; check no abrupt cut, temporal shimmer, or sudden overexposure.
3. Require pixel-identical underlying 18–22 s reference frames where the source overlay should be zero.
4. Inspect 30fps native motion for continuity and ensure later scenes stay unchanged.
5. Seek owner approval before any merge or costly full-film render. **Do not re-render 9,000 frames automatically.**

Current status: **candidate / not artistically approved**. The approved recoverable five-minute V4 export remains the baseline.

## Native C++ evidence checked 15 November 2026

Bounded full-engine [NASA C++ looktest run 43725816991](https://github.com/IKitheka/bigbang/actions/runs/43725816991) **passed** on the V5 draft PR #18. It compiled the candidate and baseline native C++ sources, rendered 17 native stills plus the protected source frames, encoded the short opening and galaxy samples, and uploaded original PNG/video evidence. This is not a full five-minute production render.

Critical protection assertion, independently byte-compared from the uploaded artifacts:

| Film time | Native V5 candidate versus native V4 baseline |
|---|---|
| 18 s | Identical PNG bytes — PASS |
| 20 s | Identical PNG bytes — PASS |
| 22 s | Identical PNG bytes — PASS |

The other four bounded preview workflows for PR #18 passed: native C++ preview, native M1.2 motion, M1.3 50-second transition, and scene-first cinematic previews. The native looktest opened at 480×270/10 FPS, i.e. **diagnostic frame sampling**, not proof of full 1080p/30 FPS quality. Owner cinematic approval and 1080p motion inspection remain pending. The final 40 seconds of the established V4 film remain the approved, unmodified production baseline.
