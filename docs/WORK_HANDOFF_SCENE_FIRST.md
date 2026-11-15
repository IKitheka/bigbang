# Scene-first cinematic renderer: handover to ChatGPT Work

**Owner decision (2026-11-15):** The full native C++ 300-second first cut is technically complete but visually inadequate for the Computer Graphics assessment. User wants visually dramatic, professionally composed, scientifically responsible cosmic environments—not diagrams. Concentrate on high-quality distinct scenes and actual native 2–5s motion previews **before** another full-length or 1080p/4K rerender.

## Where to pick up

- Source: `IKitheka/bigbang`; active feature branch: `feature/scene-first-qgp-galaxy-cinematic-v1`.
- Stacked **draft PR #11**, based on **draft PR #10** (`codex/complete-native-universe-film`), preserving the known playable first cut.
- PR #10 full-C++ review run: [43689444487](https://github.com/IKitheka/bigbang/actions/runs/43689444487), verified **300.000s / 9,000 native frames / 640×360 / 30fps**; NOT visually approved.
- Protected t=18.0–22.0s look was provisionally liked by the user. `tests/compare_native_opening.py` does same-driver comparison with pre-Work base. Never change this clip inadvertently.
- **No merges, paid GPUs, unapproved 4K render or changes to main.** Do not overwrite unrelated Work state or assume the 1080p local render survived its previous usage limit.

## Work completed in this draft

1. **QGP redesign:** `shaders/postprocess/cosmic_early.glsl` adds a time-gated t=52–101s correlated, advected medium with emissive ribbon fronts, dark cavities and gently shifting amber/cool-blue radiation. It is explicitly NOT literal colored quark dots or a hydro solver; the other early scenes retain their existing character.
2. **Galaxy redesign:** `shaders/postprocess/cosmic_late.glsl` tilts/flattens galaxy volumes, emphasizes dusty irregular two-arm structures and integrates a seeded galactic-plane stellar distribution in 3D. Its earliest influence is after 240s.
3. **Preview factory:** `scripts/render_scene_previews.sh` renders 8 x 2-second C++/OpenGL clips at 30fps + 4 native PNG stills/chapter (32 total) + a 16-second concatenated reel + eight-row contact sheet. FFmpeg **only encodes C++ RGB frames**.
4. **Diagnostics:** `tests/scene_preview_audit.py` extracts actual C++ PNG RGB scanlines and measures SDR luminance/contrast/black and white fractions; it makes no visuals.
5. **CI:** `.github/workflows/scene-first-native-previews.yml` runs bounded software GL/Xvfb native tests and 14-day artifacts. `native-film-review.yml` now requires explicit **workflow_dispatch** to avoid spending 28 minutes rendering 9,000 frames each time a shader is edited.
6. Corrected a GLSL parser error (reserved identifier `active` renamed `starVisible`). Do not confuse first failed CI runs with final pass status; inspect the **latest PR #11 commit** and workflows.

## Review procedure, in priority order

1. **Get GitHub Actions results for PR #11**, especially `Scene-first native cinematic previews`. Download `native-scene-first-...` artifact, extract `storyboard_8x4.png`, inspect **actual** t=55,65,75,85 and t=244,258,275,295 C++ images; watch `scene_reel_8_epochs_16s.mp4`, `clips/02_qgp.mp4` and `clips/07_cosmic_dawn.mp4`. Also review the 47–55s boundary CI run and the protected 18–22s motion regression.
2. Compare same timestamps from original PR #10 full review, not Blender or generic images. Measure apparent contrast, diversity and spatial hierarchy. Archive before/after contact sheet; verify C++ provenance.
3. **If QGP is still a repetitive grey haze**: refine per-voxel correlated structure/dark gaps and restrained localized emission, not global exposure. Check whether it reads as a hot, optically thick continuous fluid with nontrivial motion. Avoid whiteout and flat smoke.
4. **If galaxies still resemble grey spheres**: reduce spherical emissive bulk, enforce geometrically thin star/dust disks, add a legible warm nucleus / irregular cold young clusters / dark dust lane; focus camera framing and multi-scale gas/stars, keeping world-anchored structure coherent under motion.
5. Improve **nucleosynthesis t=90–130** and **opaque plasma t=130–170** next: they still reuse similar pale fractal folds and need materially distinct composition/dynamics. Do not represent nucleons with giant toy spheres.
6. Next refine **recombination t=170–200** to visibly change radiative transport, then **dark ages t=200–240** and first-light transition. Add unobtrusive chapter label overlays *only in an optional educational mode*, not the cinematic master.
7. Continue iteratively: one scene change -> C++ render -> inspect real clip -> image comparison -> revise. Once eight chapters receive visual owner approval, reassemble one complete 300s native cut. A full 1080p or 4K master is **not** an appropriate intermediate smoke test.

## Technical benchmarks & invariants

- Main cut: exactly 300s, eight scenes, 0–20 origin, 20–50 inflation, 50–90 QGP, 90–130 nucleosynthesis, 130–170 opaque plasma, 170–200 recombination/CMB, 200–240 dark ages, 240–300 first stars/galaxies.
- End-exclusive boundaries in `include/CinematicStory.hpp`; source art is C++ + modern GLSL using GLFW/GLAD/GLM/HDR. Python/FFmpeg may analyze and encode **but never synthesize or substitute rendered frames**.
- Preserve the opening reference, stable camera, exact timestamp determinism and all nine explicit graphics pipeline demonstrations described in `docs/RENDERING_PIPELINE.md`.
- Visual gate rubric (informal 0–5 each): spatial depth; recognizable cosmic epoch without caption; fine vs large-scale structure; physically defensible color/emission; cinematic composition and motion; no abrupt temporal pops; credible galaxy morphology. Treat 3/5 as **not** good enough for production.
- C++ GitHub-hosted software Mesa is an engineering preview only; do not claim it already equals a 4K cinematic production.

## User-facing deliverables after each Work cycle

Provide clickable: GitHub draft PR, latest scene-preview Actions run, downloadable storyboard, 16-second scene reel and per-scene native motion clips. State exactly which scenes visually improved, which remain weak, and quality gates that were not passed. Do **not** simply report 'CI green' or another complete 300s MP4.

## Important operational distinction

This chat works synchronously only; it cannot keep modifying GitHub in the background or transfer a live process into ChatGPT Work automatically. This handover file is persistent in the feature branch so the user's Work session can pick up at its next opportunity. If its prior workspace is unavailable, resume from PR #11 without restarting from main.

## Verified initial scene-first results (latest snapshot)

- Current latest commit: `8c86fc1eb73008f34b24fc78e053024a39300cc0` (check branch head for newer work).
- [Native eight-scene workflow run #43695040181](https://github.com/IKitheka/bigbang/actions/runs/43695040181): **PASS**. [Artifact #14153283732](https://github.com/IKitheka/bigbang/actions/runs/43695040181/artifacts/14153283732) expires **2026-11-29**; includes 8 clips, 32 source PNGs, 16s reel, 8×4 storyboard, metrics, provenance. This is the exact artifact to open first when Work resumes.
- [Protected opening run #43695040095](https://github.com/IKitheka/bigbang/actions/runs/43695040095), [native still regression #43695040103](https://github.com/IKitheka/bigbang/actions/runs/43695040103) and [47–55s transition #43695040092](https://github.com/IKitheka/bigbang/actions/runs/43695040092) all **PASS**. Expensive full review correctly **skipped**; don't confuse skipped with regression.
- QGP: first look was whitewashed (>80% near-white at 65–85s), latest has zero near-white there and mean luma **0.312–0.343**. Real native images show desaturated amber clouds, with pronounced dark cavities; **still not a final cinematic look**. Scene #2 is ready for art direction iteration, not approved.
- Galaxies: physically flatter ellipses, faint world-anchored stars and grain, but still too much like three isolated glowing ovals. Need visually legible dust lane, stellar disk and irregular arms + improved hero-camera framing. Scene #7 is still unapproved.
- Nucleosynthesis, opaque plasma, recombination still mostly pale correlated-noise curls and were **not** visually redesigned in this initial PR. They are now the next required scene-specific art tasks alongside galaxies.
- PR #11 conversation contains an exact independent native-C++ visual gate comment with metrics; consult it rather than inferring success from a green CI check.

## Latest hero-galaxy camera patch (the most recent evidence)

- Start from **this branch's current head**; it now includes `include/UniverseCamera.hpp`, `src/main.cpp` and `tests/test_native_m0.cpp` changes implementing a deterministic smooth target shift and dolly toward the primary galaxy only after 240s. The opening remains protected.
- **Use the more recent** [scene-first native run #43695821668](https://github.com/IKitheka/bigbang/actions/runs/43695821668) / [artifact #14154600690](https://github.com/IKitheka/bigbang/actions/runs/43695821668/artifacts/14154600690), not the older run #43695040181, for latest camera visuals. All latest native C++/GLSL previews and checks passed; [opening #43695821690](https://github.com/IKitheka/bigbang/actions/runs/43695821690), [M0 stills #43695821649](https://github.com/IKitheka/bigbang/actions/runs/43695821649) and [50s handoff #43695821645](https://github.com/IKitheka/bigbang/actions/runs/43695821645) passed too.
- New 278–280s galaxy shot has measurable pixel motion (average adjacent grayscale delta ~0.00060 vs an older *271–273s* shot ~0.00011; **different sampling intervals, so not a controlled A/B movement claim**). At t275/295 the native images visibly push toward the hero galaxy. But actual galaxies remain **too simple glowing ellipses** with weak arm and dust-lane definition. Galaxy chapter mean luma 0.0532, contrast 0.0604 across four stills.
- **Do not call any of the 8 scenes production-approved.** Final next tasks are physically informed and clearly distinct nucleus formation, opaque plasma scattering, recombination clearing and more convincing star-forming galaxy anatomy; this branch delivers only initial targeted improvements and evidence.
