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
