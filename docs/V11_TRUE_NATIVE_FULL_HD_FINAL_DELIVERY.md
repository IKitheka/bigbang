# V11 — Final true-native Full HD production master

## User-approved delivery goal

Produce a complete **five-minute Big Bang animation** with all chapters integrated, **1920×1080 native C++/OpenGL rendering for every frame**, 30 frames per second, and the complete original stereo score. Preserve the previously approved Solar System and Earth fly-in in the final 40 seconds.

The owner cannot download ChatGPT sandbox attachments reliably and requires **one GitHub Actions ZIP** that can be extracted and played on Ubuntu.

## Explicit provenance and constraints

- Branch base: V10 verified 300-second native C++ screening cut, itself stacked on V9/V8/V7/V5, whose base contains the approved original V4 solar system.
- **No changes to any shader, camera, scene, C++ rendering source, or five-minute musical composition**. V11 changes only the build, render, assembly, review and delivery workflows.
- Every frame is computed by the true C++ OpenGL renderer at **1920×1080**, not upscaled or AI-infilled from the earlier 270p/720p screenings.
- 30 deterministic, source-identified 10-second **high-resolution native** segments, with 150-frame internal recoverable checkpoints. Exact counts: 30 segments × 300 frames = **9,000 frames**, 300 seconds, 30 FPS.
- Each segment performs native C++ compiler/unit tests, checks source protection against V10, exports H.264 yuv420p, validates full native geometry, decoding, SHA and frame counts, and preserves checkpoint/renderer logs.
- The assembly job checks all original commit IDs and video streams, fully decodes parts, joins without resampling/downscaling, adds the original deterministic 300-second stereo music (AAC 48 kHz), verifies full 1080p 9,000-frame movie and decoded audio, checks chapter boundary jumps and saves a 25-frame storyboard. It additionally makes a lower-bandwidth **optional 360p version** from the exact same film.
- All codecs use standards-compatible H.264/AAC in MP4, with fast-start metadata.

## Technical acceptance criteria

1. Source-unchanged CI assertion against `feature/v10-integrated-300s-native-screening-cut`.
2. 30/30 native OpenGL render jobs PASS with 1920×1080 pixels, 30 FPS, 300 verified frames each, no dropped samples, all source commits identical.
3. Final master contains **9,000 verified frames** at 1920×1080/30FPS, 300-second duration, original 2-channel AAC soundtrack, no full decode errors.
4. 25-frame chapter storyboard; continuity luma metrics near 20,50,82,116,149,176,196,220,240,260,280 seconds. Artistic quality remains subjective; potential jumps flagged for inspection.
5. GitHub downloadable ZIP contains true-HD full film, smaller playback alternative, storyboard, validation proof and extraction instructions. Do not represent preview as native-HD before this succeeds.
6. The approved 260–300s solar system/Earth GLSL and the early explosive opening are unchanged in source.

## Note on scientific fidelity

Big Bang expansion, dark ages, galaxy formation and the compressed Solar System finale are educational cinematic visualizations, not physically exact cosmological simulations. Original soundtrack is an artistic score; space does not transmit the music acoustically.

## If runner resources fail

Keep all successfully uploaded render chunks and checkpoints. Re-render **only failed 10-second segments**, then assemble verified segments; do not quietly substitute V10's low-resolution video or legacy V4 footage. Distinguish *native 1080p* from *1080p upscaled delivery* in every status update.

## GitHub access

The user downloads from the successful `V11 FINAL true-native 1920x1080 five-minute render` workflow's final artifact, which is a ZIP from GitHub Actions (not a ChatGPT sandbox link). Artifacts expire based on GitHub retention policy; save a local copy.
