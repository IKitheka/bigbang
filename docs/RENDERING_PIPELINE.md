# Nine graphics-pipeline stages

The native application retains the nine required conceptual stages. A fullscreen triangle strip invokes a procedural volume shader: geometry is implicit rather than a collection of toy particles. A camera ray is reconstructed for each fragment, transported through world-space media, then composited through the existing HDR/bloom path.

| Stage | Implementation and role |
| --- | --- |
| 1. Scene/model definition | Deterministic global film time; `primordial_volume.frag` for the protected opening, then `cosmic_early.glsl` / `cosmic_late.glsl` for 3D radiation, gas and bounded galaxy distributions. |
| 2. Model/world transform | Density fields use world positions, coherent drift and galaxy-local tilted bases. Galaxy points and rays transform into local ellipsoidal coordinates. |
| 3. View transform | `PrimordialCamera.hpp` and `UniverseCamera.hpp`; `drawVolume` derives a world-space camera basis looking toward the shared origin. The original evaluation is preserved through 90 seconds. |
| 4. Lighting/shading | Fragment shaders integrate emission and transmittance. Local reaction enhancement, gas attenuation, stellar emission and galaxy dust are approximations in scene-linear HDR. |
| 5. Projection | Sensor width, lens and aspect determine ray directions; the fullscreen quad itself uses clip-space positions. |
| 6. Clipping | OpenGL clips the quad to the view; fixed ray depth windows and analytical ellipsoid intersections bound volume work and reject geometry behind the camera. |
| 7. Viewport mapping | `glViewport`, framebuffer dimensions and aspect map projected rays to actual output pixels; capture rejects mismatched dimensions. |
| 8. Rasterization | Native OpenGL rasterizes the quad into HDR fragments; ray integration supplies depth and material within each fragment. No Python image synthesis or existing movie playback occurs. |
| 9. Fragment/output processing | Original HDR target, bloom and SDR composite/exposure, then `glReadPixels`; C++ exports PNG or top-down RGB24, FFmpeg encodes the movie. |

The camera and shader are pure functions of global time. Smooth blends span 45–56 seconds and 164–176 seconds; stage coefficients change continuously at the other nominal chapter boundaries. No random reseeding per frame is used. Thin structures and coarse quadrature can still produce temporal aliasing; actual motion review is required beyond unit tests.

The postprocessing and protected opening shader are deliberately unchanged. This does not make the new radiation or galaxy transport physically calibrated: see the scientific limits in `NATIVE_FILM_REVIEW.md`.
