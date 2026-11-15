# V3 final film: native 1080p, Solar System ending and original sound

## Owner-approved direction

The owner watched and approved the November 15 NASA-inspired purple-white ignition and long reveal of thousands of varied galaxies. The next request is **full HD 1080p**, a **better explosion**, **less repetitive darkness and gas**, **the Sun and all eight planets at the ending**, and **original cinematic sound**. Keep the total university film **5:00**.

Do not import or play NASA's actual source movie; this project still renders all final pixels in C++17/OpenGL 3.3/GLSL. The comparison is to NASA Goddard SVS #10128 (2007), *The Big Bang*, artist Dana Berry.

## New 300-second storyboard

| New film time | Epoch | Old shader narrative sampled |
| --- | --- | --- |
| 0–20s | Origin: strengthened violet pinpoint, expanding filaments and brief bright flash | 0–20s |
| 20–50s | Inflation | 20–50s |
| 50–82s | Turbulent QGP | 50–90s |
| 82–116s | Nucleosynthesis, reaction-front visualization | 90–130s |
| 116–149s | Opaque radiation-filled plasma | 130–170s |
| 149–176s | Recombination and gradual clearing | 170–200s |
| 176–196s | **Shortened** dark ages (20s, previously 40s) | 200–240s |
| 196–260s | First stars, galaxy assembly and dense cosmic field | 240–300s |
| 260–300s | **NEW Solar System**: Sun and Mercury/Venus/Earth/Mars/Jupiter/Saturn/Uranus/Neptune, Earth fly-in | Native ray geometry |

The scene-time map is continuous and monotonic. Time compression is a *cinematic edit*, not a cosmological scale model or claim about real epoch duration. Frame numbers remain 1–9000 at 30fps, total 300.000s.

## Solar System implementation

`shaders/postprocess/solar_system.frag` analytically intersects a world-space sphere for the Sun and every planet, colors each surface from its local 3D normal and procedural deterministic noise, uses Sun-relative illumination with visible dark hemispheres, adds Earth blue oceans/continents/clouds, Jupiter's bands/spot and ray-plane Saturn rings. A camera dolly slowly reveals the entire orbital arrangement then moves toward Earth. Motion and shading are generated independently for every frame in native C++/GLSL. **Relative distances, planet diameters and orbital velocities are deliberately not to scale.** This is a clear educational/cinematic view, not a numerical N-body model. Existing galaxy HDR and bloom composite remain in place.

## Audio provenance

`scripts/create_original_score.py` synthesizes a deterministic original stereo WAV, using NumPy for oscillator layers, synthesized timpani/bass impacts, synthetic airflow, fading harmonies and an uplifting original finale. No music library, copyrighted sample, NASA audio, commercial recording or artist imitation. Film music is an editorial device: sound is not represented as traveling in space. Source score: 32,000Hz two-channel PCM; final output: AAC 48,000Hz stereo.

## Verification / source control

- Prior true 720p complete film passed: [workflow 43704434207](https://github.com/IKitheka/bigbang/actions/runs/43704434207), 9,000 frames, 1920×1080 is *not* that render; it is 1280×720. Retain as fallback.
- [V3 preview workflow 43707292084](https://github.com/IKitheka/bigbang/actions/runs/43707292084) passed. [Artifact 14159276158](https://github.com/IKitheka/bigbang/actions/runs/43707292084/artifacts/14159276158) contains 24 native C++ scene stills, real **1920×1080** PNGs at 265/284/298 seconds, 2s 640×360 Solar System motion and a 30s original stereo audio sample.
- [**V3 full 1920×1080, 30fps render 43707574746**](https://github.com/IKitheka/bigbang/actions/runs/43707574746) is explicitly invoked through a one-time workflow change, using **12 independent frame-accurate native-C++ job segments**; a dependent final job must verify every part and join exactly 9,000 frames, synthesize and mux the original complete 300s score, verify H264/AAC streams and perform full decode. Only when **all jobs succeed** is it correct to call the new film complete.
- Destination artifact name `bigbang-v3-1080p-5min-solar-sound-43707574746`. File `BigBang_300s_1080p_Cinematic_Solar_Audio.mp4`, `BigBang_300s_Browser_With_Sound.mp4`, verification JSON and 18-scene storyboard.
- Branch `feature/cinematic-1080p-solar-audio-v3`, draft PR #16. All existing PRs remain unmerged; no 4K render, paid GPU, or overwrites of approved cut.

## Submission notes for Computer Graphics class

The code exercises native vertex attributes, homogeneous view/projection transformations, triangle-strip rasterization, interpolated texture coordinates and 3D model-space normal lighting, fragment shading, ray/sphere and ring-plane intersections, HDR framebuffer, bloom and tone mapping. The nine rendering pipeline stages can be demonstrated in the attached source and course report. The final science visuals are **artistically interpreted**—no claim of literal filming, hydrodynamic simulation, or physically accurate size/orbit ratios.

If the 1080p job runs out of hosted CPU time, use the original 720p full film for an emergency submission or selectively rerun/checkpoint only the missing 1080p segments. Do not claim final delivery before inspecting a verified assembled MP4 with actual audio.
