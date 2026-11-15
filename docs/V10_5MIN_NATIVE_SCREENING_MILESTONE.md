# V10 — integrated native five-minute screening master

## Why this milestone exists
The owner has approved the direction of the bounded V5–V9 visual milestones and requests continuing to a complete cinematic film. V10 **assembles all previous native C++/OpenGL source changes into one continuous, 300-second screening master** before a high-cost full-native-1080p release.

## Deliverables
- **Full 5 minutes**, exactly **9,000 native frames at 30 FPS**, source-rendered at **480×270**. Resolution is deliberately for screening and **must not** be labeled 1080p.
- **Original synthesized stereo soundtrack**, continuous, matching the exact 300-second narrative timeline.
- 24-frame storyboard to review transitions.
- JSON with per-part SHA-256, source provenance, verified video/audio codec/length, and frame-jump diagnostics at key chapter joins.
- ZIP download automatically published to **GitHub Actions Artifacts** so the user can download and extract on Ubuntu. Prior ChatGPT sandbox links did not work for the user.

## Source and protection
- The branch is stacked on draft V9 PR #21, incorporating native C++/GLSL opening, V7 cosmic expansion, V8 galaxy reveal, V9 pre-solar dust passage, and the V4-approved solar-system/Earth finale.
- **No edit to `src/`, `include/` or `shaders/`**. An explicit CI diff verifies that V10 is only integration and QA work.
- Underlying visual metaphors are artistic illustrations, not a physically correct rendering of inflation or galaxy dynamics.

## 12-way restartable native rendering
- Twelve parallel GitHub CI jobs render time intervals bounded by the existing narrative chapter structure, all **480×270 / 30 FPS**.
- Each job checks native C++ compilation/tests, renders deterministic C++ frames under Mesa OpenGL, and checkpoints every 150 frames with SHA/manifest.
- Segment art is never sourced from a previous assistant-written video or another movie; every V10 frame comes directly from the V9-branch native renderer.
- `scripts/assemble_v10_review.py` recursively locates CI artifacts (fixing the V4 nested artifact path failure), verifies all source commits match, checks exact frame counts, fully decodes each segment, joins the twelve clips, adds the original score, verifies **9000 frames / 300 seconds / AAC stereo** and complete decode, then generates storyboard, hashes and transition metrics.
- The script flags abrupt frame changes for artistic review, without erasing deliberate cinematographic cuts.

## Milestone exit and subsequent 1080p production
1. All twelve native jobs pass, and CI master pass publishes the full five-minute GitHub artifact.
2. Inspect 0–20, 18–50, 50–176, 176–240, 240–260 and 260–300-second sections, especially exact join times 20,50,82,116,149,176,196,220,240,260,280.
3. Approve brightness, contrast, motion, fades and soundtrack alignment.
4. **Only after review** move to the next milestone: truly native 1920×1080/30fps 9,000-frame production render, with original soundtrack and all nine computer-graphics rendering-pipeline stages documented.

Current status: automated V10 continuous preview execution; no final 1080p release or branch merge yet.
