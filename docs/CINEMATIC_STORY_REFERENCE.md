# Cinematic story bible — reference film to native C++ production

**Status:** owner-selected visual direction, 2026-11-14. This is a **design/engineering contract**, not proof of cinematic quality or a complete film. The final 300-second movie must be rendered by native C++17/OpenGL/GLSL, not Blender/Python and not the original fixed-function GLUT program.

## The source we are adapting

| Reference | Verified facts |
| --- | --- |
| User-supplied `bigbang_preview(1).mp4` | 20-second accelerated H.264 preview, 960×540, 12 fps / 240 frames; SHA-256 `1a5e5b2b574b4426d37cad936380b4fa17b5d866c60c9b8b0ed0ed8ba3dd9eb2` |
| User-supplied `BigBang4.cpp(1).txt` | Original 350-second single-file C++/GLUT OpenGL fixed-pipeline teaching animation; SHA-256 `a0c97ad5623073d6868586ecbbae344bd8687bd72f3f247b1a19334cc1f65e57` |
| Existing native film project | C++17, GLFW/GLAD/GLM, GLSL 3.30, HDR/bloom, deterministic frame export, procedural field volume ray marching; latest M1.3 preview includes provisional transition across 50s |

Original reference chapter starts at seconds **0, 25, 55, 90, 125, 160, 180, 225, 275, 335**, then credits to 350. The video shows this full progression in accelerated form. The reference is a **coverage and narrative prototype**, not an art-quality benchmark.

**Rights/retention:** these supplied assets remain in the user's conversation, not committed into Git. Only observations and checksums are committed. Do not infer that the uploaded film is open-licensed media.

## Non-negotiable art direction

- **Realistic, cinematic, physically inspired. Not diagrammatic.** The final output should resemble carefully art-directed astronomical/scientific visualizations with depth, variation in scale, controlled dynamic range, subtle motion, coherent scene evolution and plausible materials.
- **No screen-filling white flashes, glowing central fireballs, shockwave circles, wireframe horizon spheres, giant red/blue nucleon balls, literal RGB quarks, toy atom orbits, neon filaments in a not-yet-luminous era, simplistic repeated spiral sprites, or rainbow CMB skies presented as visible color.**
- Distinguish what is scientifically measured, model-based, speculative, or purely illustrative; label or explain in **optional informational mode**, not intrusive HUD boxes printed over the film.
- Use physically motivated effects where feasible in OpenGL 3.3: spatially anchored 3D noise and volume ray marching, extinction and in-scattering approximations, multiscale geometry and particle distributions, HDR composition, restrained bloom, deterministic time-sampled camera, exposure and color-grade consistency, and full-frame motion checks.
- Preserve the **owner-liked native 18–22s C++ clip** *pixel-for-pixel* as a protected visual reference until the owner approves a deliberate alteration. That approval is limited to those four seconds, not the whole opening.

## Mapping the full reference narrative to our contractual 300-second film

| Main cut time | Original film's narrative contribution | Cinematic scene direction and technical work |
| --- | --- | --- |
| **00–20** Planck/abstract origin | 'Singularity' and quantum flicker (reference 0–25s) | Speculative fluctuation visual, restrained luminous structure emerging from darkness; no literal point packed with all spacetime |
| **20–50** Inflation | 'Big Bang & Inflation' (25–55s) | One evolving 3D correlated field, camera + length-scale cues, deep black negative space, continuous motion; protect approved native 18–22s frames |
| **50–90** Quark–gluon plasma | Dense RGB particle scene (55–90s) | Dense hot radiation-coupled medium; plausible optical depth, scattering/transmission and local turbulence; avoid literal red/green/blue charge dots |
| **90–130** Nucleosynthesis | Large colored proton/neutron balls (90–125s) | Macro-to-micro scene transition showing energy and interactions, limited physically meaningful particle clusters/collision visuals, no glossy classroom spheres |
| **130–170** Opaque plasma | Reference recombination's initial orange fog (125–160s) | Radiative optically thick medium, rich depth and evolving opacity; avoid uniform orange filter |
| **170–200** Recombination/CMB | Reference decoupling and CMB map (125–160s) | Progressively transparent medium with recombination/cosmic background field; CMB colors are visualization conventions, not visible-color photons |
| **200–240** Dark ages | Reference dark ages (160–180s) | Near-darkness, subtle neutral medium/correlated collapse with no visible stellar web or arbitrary blue particles |
| **240–300** Cosmic dawn / galaxies | Reference first stars and galaxy formation (180–275s) | First luminous compact sources, self-consistent gas collapse, hierarchical galaxy development, realistic stellar brightness, coherent morphologies rather than flat spiral icons |

### Solar System/Earth and credits — controlled scope decision

The reference source then depicts **Solar System formation → Earth → credits** (275–350s). Those chapters are part of its *full story*, but **not** in the project's pre-existing eight-scene 300-second contract. Do not quietly add them or erase the prescribed 240–300s cosmic-dawn/galaxies sequence. Keep them explicitly in the narrative backlog; the owner may approve either (A) a separate 300–350s epilogue/extended cut, or (B) a deliberately re-timed final 240–300s scene. Neither is authorized merely by liking the reference film's story.

## Priority scene transitions, reference output and acceptance

| Interface | Technical design objective | Evidence to require |
| --- | --- | --- |
| 18–22s (protected) | Freeze the user-liked native C++ field/look | Per-frame checksums at 18.0–22.0, frame-evaluation repeatability, short clip |
| 20s epoch boundary | No material pop or impossible white flash | 1–2 seconds contiguous frames, stable exposure, camera continuity |
| **50s inflation → plasma** | Smoothly broaden existing correlation field, increase optical thickness and correlated thermal emission without flattening to fog | 47–55s native clip + 65/85s stills; verify no near-black dip or screen-filling uniform haze |
| 90s → nucleosynthesis | Change scale and composition without unrelated cut | 88–93s consecutive native images, time-seek consistency |
| 130s → opaque plasma | Convey composition and thickening radiative medium | 127–133s native motion review and scene depth |
| 170–200s recombination/CMB | Opacity reduction, visible change in transport and sky representation | 168–202s sampled native frames and boundary clips |
| 200–240s dark ages | Subdued real structure with historically correct darkness | 198–242s native samples and no fake star points |
| 240–300s cosmic dawn → galaxies | Multiscale large-structure rendering, physically plausible age progression | 238–300s native samples, separate morphology review |

Require a compositing/grade pass so the collection looks like **one film**, not nine unrelated demonstrations. Objective diagnostics (pixel mean, near-black/near-white, frame delta) catch gross problems; they cannot certify photorealism, cosmological correctness or camera artistry. Every major scene receives human visual approval.

## Implementation strategy and responsibilities

- **Existing renderer** stays authoritative: C++17 / GLFW / GLAD / GLM, GLSL, HDR framebuffers, native frame capture, automated Mesa/Xvfb low-resolution C++ preview and FFmpeg encoding.
- **Blender** may produce art-direction previews, texture/geometry/volume assets and a camera/parameter interchange schema, but final native C++ code shades and renders the film. Imported geometry/assets are permitted; displaying Blender-rendered video through C++ is not.
- **GLUT single-file reference** informs scene inventory, narrative order, optional educational overlay content and educational demonstrations, **not** the rendering backend. Do not port deprecated `glBegin`/fixed-function material calls as the main engine.
- **New timeline interface:** `include/CinematicStory.hpp` is an explicit C++ contract for the eight nominal periods. It is a foundation for scene dispatch but does **not** mean the late-epoch renderers already exist. See `docs/DEVELOPMENT_ROADMAP.md` for native milestones.
- **Preview approvals:** 480×270 CPU CI is a debug baseline; final 4K/60fps quality/performance still unproven. Production requires 4K stress-test timings, consistent color/lighting, memory/storage estimates and specific owner approval.

## Concrete next engineering slices

1. **M1.3 visual recovery:** the native 50–90s prototype is still an overly dark/flat transition. Fix the 50–55s dip without altering the protected 18–22s pixels, add 65/85s rich depth/structure, and produce real C++ visual comparisons.
2. **M2 90–170s:** scene dispatch from the typed timeline; native microphysical artistic treatments for nucleosynthesis and optically thick medium; continuity checks at 90/130/170s.
3. **M3 170–300s:** gradual transparency/CMB, dark ages, physically plausible star ignition and emergent galaxies; continuous native previews at all important boundaries.
4. Optional educational mode **after** cinematic master stabilizes: tasteful short labels/captions/scale graph on a separate presentation-render layer, not in master frames.
5. Gate optional solar-system/Earth extension on a user-approved timeline decision.

**Decision record:** Owner wants *the reference film's complete narrative coverage* combined with the *native renderer's sophisticated visual-effects techniques*, with very realistic rather than diagrammatic presentation. No existing film duration, open PR, or production authorization is implicitly changed.
