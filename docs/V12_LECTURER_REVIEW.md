# V12 — Lecturer review: planetary formation takes the lead

## Status and provenance
V12 is an IN-DEVELOPMENT revision of the source-verified V11 native 1920x1080 / 30 FPS / 300-second movie. It is kept on a separate feature branch so the successful V11 film and original 40-second finale are recoverable.

**Do not submit or describe V12 as completed until all 9,000 native frames have been rendered and the film, original soundtrack and transitions have passed full assembly/decode and human viewing checks.** The V11 master is still the submission fallback.

The lecturer requested less darkness and cosmic formation and more of the actual development of planets. V12 therefore keeps a 300-second cinematic structure but assigns approximately 180 seconds to the solar nebula and planets.

## New 300-second presentation timeline

| Film time | Stage | What is visible |
|---|---|---|
| 00:00–00:15 | Origin and ignition | Compact luminous origin, bright violet-white expansion |
| 00:15–00:35 | Inflation/expansion | Correlated flowing radiation structures |
| 00:35–00:50 | Quark–gluon era | Dense, energetic plasma visual metaphor |
| 00:50–01:05 | Primordial nucleosynthesis | Evolving radiant hot matter |
| 01:05–01:13 | Opaque plasma | Scattered, opaque radiation |
| 01:13–01:20 | Recombination/CMB | Radiative opacity drops |
| 01:20–01:27 | Dark ages | Brief subdued, neutral medium |
| 01:27–01:45 | Cosmic dawn | First stars and young galaxies |
| 01:45–02:00 | Galaxy-to-molecular-cloud | Dusty camera passage toward star-forming material |
| 02:00–02:25 | Molecular cloud / protostar | Central young Sun emerges from dust |
| 02:25–03:00 | Rotating protoplanetary disk | Differential rotation and disk structure |
| 03:00–03:35 | Condensations/planetesimals | Local disk clumps and separately shaded rocky bodies |
| 03:35–04:05 | Developing planetary embryos | Sun grows and recognizable planet bodies enlarge |
| 04:05–04:25 | Eight-planet growth | Distinct colors, rings and emerging orbits |
| 04:25–04:43 | Clear, mature Solar System | Full, spatially coherent system |
| 04:43–05:00 | Earth close-up | Camera approaches procedural blue Earth |

The finer formation intervals are artistic pacing, not physical epochs or an exact simulation of accretion.

## Implementation
- `include/CinematicTimeline.hpp`: `legacySceneTime()` compresses the original early scenes into the first ~130 seconds. `solarSceneTime()` continuously maps 118–300 seconds to the original 259–300-second GLSL evolution.
- `src/main.cpp`: 118–132-second crossfade overlaps the galaxy/molecular-cloud scene and young Sun; the GL draw and HDR/bloom/SDR pipeline stay native.
- `shaders/postprocess/solar_system.frag`: receives distinct film time and solar scene time, ray-intersects additional world-space accreting bodies and preserves eight mature planets, Saturn rings and the Earth fly-in.
- `shaders/postprocess/protoplanetary.glsl`: adds seeded evolving disk condensations before recognizable planets appear; the original rotating multi-layer disc remains.
- `scripts/create_original_score.py`: deterministic original stereo music is retimed for the shortened cosmic introduction and longer solar-development arc.
- `tests/test_native_m0.cpp`: verifies chapter boundaries, continuity, and monotonic solar time evaluation.
- `.github/workflows/v12-planetary-preview.yml`: clean Ubuntu build, native tests, soundtrack generation, real native stills and short moving previews.

## Scientific boundaries
This is a cinematic illustration of solar-nebula and accretion concepts, not an N-body, fluid dynamics, SPH, gas-chemistry, radiative-transfer or physically scaled orbital simulation. The planetesimals and light are procedural teaching devices. The Big Bang was not a fireball exploding into already existing empty space. Planetary orbital speeds/sizes and the 4.6-billion-year solar system history are greatly condensed. There is no acoustic sound in a vacuum; music is an original artistic score.

## Required acceptance before calling it final
1. Successful CMake Release compile, native CTest and Python test suite.
2. Scene previews at 6, 22, 44, 84, 112, 132, 165, 204, 253, 289 and 297 seconds; consecutive clips around 125, 177, 222 and 286 seconds.
3. Human review of clarity of proto-Sun, disk, accreting embryos, all eight planets and final Earth framing.
4. Genuine native 1920x1080 30 FPS, all 9000 frames, fully verified video and newly synchronized stereo score.
5. Revised technical documentation, sequence storyboard, accessible downloadable master and updated university presentation.
