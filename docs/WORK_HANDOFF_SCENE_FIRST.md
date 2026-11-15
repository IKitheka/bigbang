# Work handoff — cinematic C++ scene-first graphics pass

**Captured:** 2026-11-15, after the user asked ChatGPT in this chat to continue engineering until ChatGPT Work access returns. No autonomous process remains running beyond explicit bounded GitHub Actions jobs.

## User's visual objective

Make the 300-second Big Bang / cosmic evolution film **genuinely cinematic and impressive to a Computer Graphics lecturer**, still scientifically responsible. Use the uploaded old GLUT video only for narrative, not for its colored atom/diagram look. **Final pixels must be rendered by native C++17/OpenGL/GLSL**, with Python only supervising/exporting/analyzing. Keep nine rendering pipeline stages demonstrable. Target photorealistic-inspired depth, purposeful lighting, coherent camera/epoch transitions, multiple visibly distinct materials. No placeholder sphere galaxies, colored quark balls or cartoon white explosion.

## Source of truth & existing completed first cut

- Authoritative baseline: `codex/complete-native-universe-film` at `83f2c6850158eb20622ce3965deaa247adc2bb06`; its [draft PR #10](https://github.com/IKitheka/bigbang/pull/10), completed 300.000s at 640×360, 30fps, 9,000 native C++ frames (CI run 43689444487, artifact 14152387719, expires 2026-12-15). 1080p local render was separately reported incomplete; do NOT claim complete until verified.
- Owner liked the native 18–22s restrained blue-grey opening. Preserve in future rendering tests.
- Previous build used `shaders/postprocess/cosmic_early.glsl` and `cosmic_late.glsl` included by `cosmic_evolution.frag`. Native scene tests use Mesa llvmpipe/Xvfb.
- **Do not run a full 300s rerender until individual scene clips pass owner review**; especially galaxies, QGP, nucleosynthesis, recombination.

## Concurrent active PRs — handle carefully

- [PR #11](https://github.com/IKitheka/bigbang/pull/11): `feature/scene-first-qgp-galaxy-cinematic-v1`, SHA `d5d19f12a091e08e8ea0177da447c9b90d02d117`, a *parallel draft* from PR #10 that improves QGP and galaxy GLSL and provides 8 short scene previews. **Strong candidate to continue as primary integration branch.**
  - Actual run: [43696265179](https://github.com/IKitheka/bigbang/actions/runs/43696265179), artifact `14155010243`. Contains 32 stills (4 per epoch), 8 motion clips, a 16-second gallery reel, contact sheet and metrics.
  - Reviewed PR11 275/295s previews: improved disc shapes with lots of resolved point-like stars, still overly uniform / particulate; more iteration needed.
- [PR #12](https://github.com/IKitheka/bigbang/pull/12): `feature/cinematic-galaxy-morphology`, SHA `d5cba10b15d1f4f274203b23a946acede99ee253`, a **parallel experimental** morphology renderer also based on PR10, **not** a successor of PR11. Adds thin inclined discs, broken 3D spiral arms, dust absorption and more visible disk organization, plus a dedicated baseline-vs-candidate proof workflow. Full 9,000-frame action changed to *manual only* in this PR, not in PR11.
  - Actual bounded [run 43697560801](https://github.com/IKitheka/bigbang/actions/runs/43697560801) passed, [artifact 14154464325](https://github.com/IKitheka/bigbang/actions/runs/43697560801/artifacts/14154464325) includes 8 baseline PNGs + 8 candidate PNGs at t=18,20,22,240,250,260,270,290; 21 candidate native motion frames 270–274s at 5fps and MP4; metrics/contact sheets.
  - Same-environment t=18/20/22s identical to PR10. Our PR12 still shows too much luminous oval behavior at 270s, improved arms at 290s; **NOT approved**.
  - **Do not indiscriminately merge PR11 and PR12** (both edit `cosmic_late.glsl`). Compare real visual results; choose improvements individually. PR11 offers more stellar granularity; PR12 an alternative disk-arm density field.
- PRs #1/#3/#4/#6/#7/#9 are earlier stacked drafts. Never rewrite/force push their branches. Existing base PRs remain unmerged.

## What has been done on PR12

1. Preserved C++ renderer and original full film baseline.
2. Changed only `shaders/postprocess/cosmic_late.glsl`: finite locally oriented volume, 18 samples per intersected disk, thin Z height, small bulge, pair of 3D density-wave arms, blue-white star-forming knots, passive dust optical depth and non-neon color.
3. Added `.github/workflows/native-galaxy-review.yml`, `tests/render_galaxy_previews.sh`, `tests/compare_galaxy_previews.py` for low-cost CI comparisons and contact sheet/video.
4. Confirmed C++ tests and protected opening and manually inspected native actual t270/t290 images.
5. No 4K render, no merge, no Work task edits or changes to the source video.

## Next concrete priorities

1. Continue primarily on PR11 scene-first branch. Compare PR11 and PR12 late-scene actual PNGs at near-match times (270/275 and 290/295), recognize camera changes, avoid objective claims that one is universally better.
2. Improve galaxy dust lanes, resolved stars with camera-consistent finite angular footprints, dark gas lanes and spatially connected backdrop. Consider local analytic disk-plane star points from PR11 and differential disk inclination from PR12; render t=260/275/290/295 and 3–6s C++ clips to evaluate.
3. Improve luminous plasma 50–90s and all mid-epochs so QGP (energetic turbulent medium), nucleosynthesis (cluster interaction visual), opaque plasma (diffusive, luminous radiative field), and recombination (opacity clearing) visually differ.
4. Deliver eight short scene-specific motion clips and a single contact sheet before another full render; use `Native scene-first` workflow in PR11 or bounded jobs. Review with owner before 1080p/4K.
5. Record actual SHA, CI run, artifact, frame count, manual visual shortcomings at each iteration. CI passing does not mean artistic or scientific approval.

**Stop conditions:** never claim photorealism is achieved just because native pixels exist; no merging, no 4K production/paid GPUs, no loss of baseline film, no automatic overnight work promise. The next Work invocation should start by reading this note and PR #11 / #12 reviews.
