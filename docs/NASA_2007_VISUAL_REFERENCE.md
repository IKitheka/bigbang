# Target lock: NASA Goddard "The Big Bang" (2007), user-chosen visual reference

**User direction 2026-11-15:** "this is exactly what I want, this exact scene the way it is" referring unambiguously to
https://www.youtube.com/watch?v=LeUcjqqhNxM

**Reference identification (verified by NASA and YouTube):**
- Title **NASA | The Big Bang**, NASA Goddard video originally published to YouTube on 2007-06-27.
- NASA Scientific Visualization Studio **#10128, "The Big Bang"**, published July 3, 2007.
- Original animation credited **Dana Berry (Skyworks Digital)**, writer **Michael McClare**.
- Official original video: https://svs.gsfc.nasa.gov/vis/a010000/a010100/a010128/BigBang_HD_LARGE_QT_Video_1.mp4
- NASA page: https://svs.gsfc.nasa.gov/10128
- **NOT the later NASA 2017 5K Big Bang Animation #12656**; do not mix its very different purple starburst art direction into the exact target.

## Owner's priority

The NASA 2007 reference is now **the specific visual and shot-progression target**, not just an inspiration for a broad narrative. Match the original sense of progression from a pinpoint and luminous energetic expansion toward many recognisable galaxies scattered in true black, with believable changes of scale, particle/gas appearance, camera dynamics, density and light. All eight science chapters of our existing 300s film may still be conveyed, but our final edit should read visually like the reference with richer detail and modern renderer fidelity.

**Do not promise pixel-identical reproduction from source footage.** Rebuild with native C++17/OpenGL/GLSL primitives, volumes, particles, astrophysical geometry, procedural shading, exposure/tonemapping and cinematic camera motion. The required university project must visibly *compute and render new frames*, not project NASA's video through the C++ pipeline or repackage frames. A recreation that matches overall shot design (once analyzed) is the target; exact frame-for-frame copying is not a substitute for implementation.

## Early observations grounded in NASA source description and official still

- NASA identifies a **pinpoint of light** opening, with continuing **star and galaxy formation**.
- NASA's official still `BigBang842.jpg` shows a deep-black frame with **many tiny diverse blue-white/yellow galaxies**, varied orientation, sparsity and size. The current native C++ 240–300s scene's three large luminous ovals and over-smoothed spherical bulges fail this target.
- The linked user reference is a **single compact visualization** that can be re-timed within 300s, not necessarily nine separate cinematic visual languages. Coherent visual transformation is more important than forcing unrelated abstract scenes together.
- The reference is an **artist's representation**, not an observational documentary recording of the earliest instant.

## Before making confident shot-by-shot claims

Run `nasa-2007-reference-review.yml`. It fetches the **exact 2007 NASA-supplied MP4** (with WebM fallback) into a temporary GitHub Actions runner, extracts 18 evenly spaced frames, creates `scene_storyboard.png` and retains sample timestamps, **without adding NASA video to the repository or final film**. Inspect actual frames, color, camera cues, rhythm and scene transitions; document a timestamped shot map and user-facing target comparisons.

If the NASA download fails, state that you inspected only the description and official still; do **not** claim to have watched the full sequence.

## Next scene-first implementation after visual review

1. Freeze / preserve the native 18–22s early work as a technical regression reference; the owner may explicitly revise its art direction for closer NASA-style matching after seeing a new preview.
2. Produce a **5–10s C++ cinematic look-test** that matches one NASA reference shot, preferably end-state many-galaxies field. Thousands of varied distant ellipsoid/disc/irregular galaxies and differential depth/scale should replace just three pale, large blobs; don't just brighten a few volumes.
3. Design a strong origin-to-galaxy **shot progression** that keeps the existing 300s science content while feeling like the 2007 NASA motion reference.
4. Create side-by-side frame/contact comparison and matching movement evidence from the genuine C++ render, with manual user review. Do not rerender all 9,000 frames until look is approved.
5. Keep PR #10 full-film baseline; compare PR #11 scene-first and PR #12 galaxy alternate without merging either blindly.
6. No paid GPU/4K production or branch merges without authorization; credit NASA source appropriately in notes and any final project references.

**High-quality, scientifically responsible cinematic visualization can employ metaphors.** Mark speculative physics as such in an optional teaching note while favoring the owner-chosen cinematic language.
