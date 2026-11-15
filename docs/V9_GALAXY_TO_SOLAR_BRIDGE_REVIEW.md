# V9 — galaxy journey to the forming Solar System

## Narrative aim
Bridge the vast, mature galaxy field to the **already owner-approved 260–300 s protoplanetary formation and Earth fly-in**. The visual shift from the old galaxy field to the warm, dusty disc should feel like a purposeful camera journey, not a sudden cut.

## Actual native implementation
- **New:** `shaders/postprocess/galaxy_to_solar_bridge.frag` performs bounded 18-sample world-space volumetric transport. Its coherent, low-opacity dust starts cool blue and gradually picks up warm nebular color. The changing camera creates genuine depth parallax rather than a pasted image.
- **Changed:** `src/main.cpp` draws the transparent gas **only for film time 240 < t < 260** after the native 4,400-object galaxy catalog. It blends additively to avoid washing out the pre-existing galaxies.
- **Unchanged:** 0–240 s opening, physics visual metaphors, dark ages/dawn, soundtrack synthesis, galaxy morphology and the complete approved solar-system GLSL renderer. By construction **no bridge draw call occurs at t>=260**.
- This is an artistic time-compression device, not a scientific model showing an individual galaxy actually becoming a solar nebula.

## Verification and performance
The V9 bounded workflow builds C++17, OpenGL 3.3, HDR and shader code under Mesa llvmpipe, then outputs **900 consecutive native frames, presentation t=238..268 s (30 s) at 480×270 and 30 FPS**. FFmpeg encodes real C++ RGB24, adds the **original synthesized** soundtrack at the correct 238 s offset, verifies H264 video/AAC stereo/duration and full decode. Independent still-versus-video RGB checks reject the channel-corruption defect detected and fixed during V8.

Critical visual checkpoints: 239 (unchanged), 243, 248, 253, 257, 259, 260, 262, 265, 268, 280 and 295 seconds. At 260+ candidate native C++ pixels should be byte-identical to the V8 baseline, subject to identical native renderer setup.

## Acceptance policy
This is **V9 draft looktest only**. No merge, full 9,000-frame render or high-resolution release until the user reviews actual motion and approves. Keep the recovered Work V4 master as fallback. Preserve the solar finale from V4.

## Downloading
GitHub Actions evidence appears under the successful run of the workflow “V9 native galaxy-to-solar bridge 30s”. Click the artifact to obtain a ZIP that includes the native MP4 with sound, still frames and verification. The user specifically prefers ZIP rather than a direct chat MP4 and has experienced failures with ChatGPT sandbox links.
