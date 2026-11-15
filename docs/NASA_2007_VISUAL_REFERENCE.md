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

## Verified shot map from the actual NASA 2007 movie (native NASA file)

**Evidence:** [GitHub Actions run 43699424358](https://github.com/IKitheka/bigbang/actions/runs/43699424358) downloaded `BigBang_HD_LARGE_QT_Video_1.mp4` directly from NASA SVS, verified by ffprobe as **1280×720, H.264, 60fps, duration 14.033333s, 11,034,279 bytes**, and extracted 18 evenly spaced **real source frames** into [artifact 14155492680](https://github.com/IKitheka/bigbang/actions/runs/43699424358/artifacts/14155492680). Original NASA movie is not copied into the Git repository.

| Original NASA time | Directly observed appearance | Exact art-direction implications for C++ |
| --- | --- | --- |
| **0.39–1.17s** | Near-black charcoal-violet background, tiny **centrally placed purple-magenta pinpoint**; subdued concentric violet glow grows steadily | Quiet pinprick beginning, fixed attention in the middle, smooth energy ramp, no premature starfield |
| **1.95s** | Point becomes **bright lavender-white starburst** with soft radiant violet spokes on almost black | Controlled anamorphic/star diffraction glow; explicit bright hot core and purple halo, no simple orange blob |
| **2.73s** | **Full-frame near-white transition**, almost featureless for a brief moment | Prior instruction to *avoid all white-outs* is overridden by user's **exact selected NASA sequence**; match a brief deliberate luminous transition, not repeated arbitrary flashes |
| **3.51–4.29s** | Pale light grey / cool-grey translucent **irregular cloudy plasma field**, large soft foam-like overlapping volume forms | High-key, genuinely structured volume/fog; no hard edge or spheres; retain broad spatial variation |
| **5.07–6.63s** | As the same layered grey field remains, **tiny white pinpricks and increasingly visible small individual galactic forms** emerge throughout it | Maintain same shot continuity: thousands of seed galaxy forms appear embedded *inside* haze instead of replacing fog with a different unrelated scene |
| **7.41–8.97s** | Grey translucent veils **thin dramatically**, revealing many sharper stars and miniature spirals/ellipses; background darkens toward nearly black | Cross-fade using depth-dependent physical-inspired extinction; local colors mainly neutral white, cool blue, soft amber, distant low-contrast grey |
| **9.75–13.64s** | Dense black 3D **deep-field of many varied galaxies** of clearly distinct angular sizes, orientation, shapes and brightness (blue, amber, warm white), with very many small point sources | This is the decisive late-time reference. **Do not settle for three blurry ellipsoids.** Use hundreds/thousands of heterogeneous angular galaxy profiles, recognizable spirals/ellipticals/irregulars, subtle dust and glow on black; preserve parallax/motion and spatial depth |

The early high-key cloud is **much brighter than our present restrained 18–22s opening**. The earlier protected opening remains an engineering baseline, but the user's new explicit reference **supersedes the old styling preference** if we propose a deliberate look revision. Show before/after owner clips before changing those previously accepted frames.

### What this means for our overall editing / scene architecture

This 14.03-second reference visually compresses cosmic history into **one flowing transformation**: dark violet point → luminous starburst → broad milky-white translucent gas → emerging many tiny galaxies inside gas → clearing to a dark deep-field of diverse, colorful galaxies. The C++ 300-second film should implement the same **visual trajectory and organic continuity** while giving extra narrative time to inflation, quark–gluon plasma, nucleosynthesis, recombination and dark ages. Don't pad the NASA 14-second source, display it through C++, or pretend its original 14-second duration satisfies the university requirement.

**Camera/motion caution:** the sampled frames establish composition and succession; the exact per-frame camera path, motion vectors and ease curves have *not* been measured. The requested goal includes close motion matching, so follow-up should extract true source motion samples at 60fps to estimate temporal changes; do not invent claims about exact camera acceleration.

**Credit:** NASA, animator Dana Berry (Skyworks Digital), NASA SVS 10128. NASA imagery serves strictly as a shot and style reference; independently shade/render all final pixels in native C++/GLSL, documenting that all early-universe visuals are artistic interpretation.

## Before making confident shot-by-shot claims

The `nasa-2007-reference-review.yml` workflow has now **passed** and fetched the **exact 2007 NASA-supplied MP4** (with WebM fallback) into a temporary GitHub Actions runner, extracted 18 evenly spaced frames and created `scene_storyboard.png` and retains sample timestamps, **without adding NASA video to the repository or final film**. The timestamped shot map above records the observed sequence. Precisely measuring camera motion still requires additional temporal inspection.

If the NASA download fails, state that you inspected only the description and official still; do **not** claim to have watched the full sequence.

## Next scene-first implementation after visual review

1. Freeze / preserve the native 18–22s early work as a technical regression reference; the owner may explicitly revise its art direction for closer NASA-style matching after seeing a new preview.
2. Produce a **5–10s C++ cinematic look-test** that matches one NASA reference shot, preferably end-state many-galaxies field. Thousands of varied distant ellipsoid/disc/irregular galaxies and differential depth/scale should replace just three pale, large blobs; don't just brighten a few volumes.
3. Design a strong origin-to-galaxy **shot progression** that keeps the existing 300s science content while feeling like the 2007 NASA motion reference.
4. Create side-by-side frame/contact comparison and matching movement evidence from the genuine C++ render, with manual user review. Do not rerender all 9,000 frames until look is approved.
5. Keep PR #10 full-film baseline; compare PR #11 scene-first and PR #12 galaxy alternate without merging either blindly.
6. No paid GPU/4K production or branch merges without authorization; credit NASA source appropriately in notes and any final project references.

**High-quality, scientifically responsible cinematic visualization can employ metaphors.** Mark speculative physics as such in an optional teaching note while favoring the owner-chosen cinematic language.
