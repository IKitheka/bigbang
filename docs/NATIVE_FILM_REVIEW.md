# Native five-minute review implementation

Implements Issue #8 on an independent feature branch based on PR #9 commit `e6d299579a1b06d3d9dcb2e79bddafb8784d0a7e`. Existing PRs are not merged or rewritten. The supplied accelerated video and GLUT source inform storytelling only. This native request supersedes the separate Blender Issue #2 task.

## Chapter coverage

| Film seconds | Native visual treatment | Interpretation limits |
| --- | --- | --- |
| 0–20 | Protected original speculative primordial fluctuations. | Unobservable era; abstract field, not a recording. |
| 20–50 | Original inflation camera/field, followed by a gradual radiation-medium handoff after 45 seconds. | Correlation-scale metaphor, not an explosion into external empty space. |
| 50–90 | Coherent 3D radiation interfaces with extinction and dark passages. | No literal quarks; no calibrated QCD or hydrodynamic solver. |
| 90–130 | Local exchange of warm radiation along the same evolving medium. | Nuclear-reaction metaphor; no particle-resolved nuclear abundances or reaction-network calculation. |
| 130–170 | Growing extinction within the persistent radiation medium. | Shares morphology with prior chapters; its narrative distinction is subtle. |
| 170–200 | Radiation fades as opacity decreases; a low-amplitude neutral background illustrates perturbations. | Neither a quantitative CMB map nor a literal visible-light sky. |
| 200–240 | Faint neutral density traces and coherent gravitational concentration. | Explanatory brightness makes neutral gas visible; it is not luminous pre-stellar emission. |
| 240–300 | Compact first-light populations develop into three tilted, volumetric stellar/dust distributions. | Procedural assembly, not N-body dynamics; mature disc morphology compresses much later evolution into the ending. |

The main story stays 300 seconds. No solar-system/Earth epilogue, credits extension, HUD, paid resource or 4K master was added. This film has no sound track.

## Protected look and baseline evidence

Approved native baseline: Actions run `43635822159`, artifact `14129433323`, source head `9ce5d028ac0fef2f256bbaa208c87c5e71c45a3e`. Baseline transition: run `43638913619`, artifact `14131452529`, PR #9 head `e6d299579a1b06d3d9dcb2e79bddafb8784d0a7e`.

`tests/data/protected_opening_sha256.json` retains all 41 historical PNG hashes for 18–22 seconds. `tests/compare_native_opening.py` independently renders the unchanged base and candidate on the same driver and fails on any byte difference. It separately reports historical exact matches, never treating environment differences as exact matches.

The initial local comparison on Mesa 25.2.8 / LLVM 20.1.2 llvmpipe produced **41/41 byte-identical candidate/base PNGs**. Against historical Actions, both unchanged base and candidate matched 38/41; at 18.9, 19.3 and 20.4 seconds each differed in just one RGB channel by one 8-bit level. That is a measured cross-environment discrepancy, not a passing historical exact-hash result. Captured images and driver logs must accompany any later verification claim.

Before: 47–55 seconds fell toward near-black; 65/85 seconds showed broad featureless grey/brown gradients. The first new shader attempt was also rejected after actual images showed flat fog. The revised pass uses sparse coincident 3D interfaces, lower background density and selective emission. It reveals structured folds and black gaps. Later orange-particle placeholders are no longer rendered. The new structures remain visibly procedural, with soft lobes; photorealism is not established.

## Delivery and validation

- The C++ batch path reuses one OpenGL context per inclusive chunk, emits RGB24 only on stdout and sends diagnostics to stderr. Timestamp evaluation remains exact and global across chunks.
- The supervisor records source-file hashes, binary hash, graphics identity, explicit driver environment, encoder version/settings and frame range. It locks the output directory, atomically checkpoints verified chunks, refuses incompatible resume, rebuilds corrupted chunks and verifies final frame count, dimensions, frame rate, duration and full decoding before publishing `film.mp4`.
- Unit tests cover timeline, capture arguments, camera continuity and PNG export. Delivery tests use small FFmpeg fixtures to exercise concat, resume, corruption and interruption. They do not certify image quality.
- Actions runs the existing bounded native previews plus a full 640×360/30 fps film with an independently built opening comparison. It retains film, recoverable chunks, comparison PNGs, checkpoint and logs for 30 days. Inspect artifact completion state, not only its existence.
- Final render metadata and sampled motion findings belong in the delivered completion report. Until those actual outputs exist, this document makes no claim of a successfully completed movie.

## Next production steps

Owner artistic review should first address soft early structures, clearer physical/narrative differentiation of nucleosynthesis, quadrature aliasing and galaxy morphology. A higher-quality transport pass would need better volume sampling, physically calibrated scattering, explicit simulation data or validated density evolution, and a denser galaxy population with natural star fields. Obtain scene-specific temporal/spatial convergence measurements and benchmark representative 4K/60 fps frames before estimating resources. A full 4K master remains subject to separate user authorization.
