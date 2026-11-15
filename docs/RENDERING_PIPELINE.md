# Graphics rendering pipeline: implementation evidence

## Scope and course model

The existing project used these nine conceptual stages: scene/model definition, model/world transform, view transform, lighting/shading, projection, clipping, viewport mapping, rasterization and fragment/output processing. This document retains that model and adds an explicit mapping to programmable OpenGL stages. The lecturer's separate rubric has not been supplied, so conformance to a different nine-stage numbering is unverified.

The film uses OpenGL 3.3 Core with GLSL 330. Most scene geometry is implicit: a screen quad generates fragments, then each fragment reconstructs a camera ray and shades a procedural 3D scene. Ray marching executes *inside the fragment shader*. It does not replace OpenGL input assembly, vertex shading, clipping, rasterization or framebuffer output.

## The repository's nine conceptual stages

| Stage | Implementation evidence | Demonstration |
| --- | --- | --- |
| 1. Scene/model definition | [CinematicStory.hpp](../include/CinematicStory.hpp), [CinematicTimeline.hpp](../include/CinematicTimeline.hpp), scene program selection in [main.cpp](../src/main.cpp#L155) | Seek to expansion, cosmic dawn and the Solar System; relate the selected global time to the scene programs. |
| 2. Model/world transform | [drawVolume](../src/main.cpp#L29) supplies world-space camera vectors; [GalaxyCatalog.hpp](../include/GalaxyCatalog.hpp) defines procedural catalogue geometry; [cosmic_evolution.frag](../shaders/postprocess/cosmic_evolution.frag) and its sibling modules evaluate implicit fields | Explain the distinction between world-space density and the screen quad's clip-space geometry. |
| 3. View transform | [PrimordialCamera.hpp](../include/PrimordialCamera.hpp), [UniverseCamera.hpp](../include/UniverseCamera.hpp), forward/right/up basis in [drawVolume](../src/main.cpp#L29) | Show the camera and moving look-at target; camera unit assertions test anchors and boundary continuity. |
| 4. Lighting/shading | Scene programs loaded in [main.cpp](../src/main.cpp#L117): primordial_volume.frag, nasa_origin.frag, cosmic_evolution.frag, galaxy_to_solar_bridge.frag and solar_system.frag | Explain integrated emission/attenuation, stellar glow and planet illumination as artistic approximations rather than calibrated cosmology. |
| 5. Projection | [verticalTanHalfFov](../include/PrimordialCamera.hpp) derives lens/aspect parameters; [drawVolume](../src/main.cpp#L38) supplies uAspect and uTanHalfFovY; [screen.vert](../shaders/postprocess/screen.vert) writes clip-space gl_Position | Changing aspect affects the reconstructed camera rays; the carrier quad remains in clip space. |
| 6. Clipping | gl_Position from [screen.vert](../shaders/postprocess/screen.vert) undergoes fixed OpenGL clipping. Scene ray bounds/intersections additionally limit implicit geometry | Explain that ray bounds are fragment-shader scene traversal and are distinct from fixed-function homogeneous clipping. |
| 7. Viewport mapping | [glViewport](../src/main.cpp#L149), glfwGetFramebufferSize and the capture dimension check in [main.cpp](../src/main.cpp#L142) | Request 3840 x 2160 and compare the manifest, framebuffer size and decoded dimensions. Metadata alone is insufficient evidence of native rendering; preserve the actual render command/source. |
| 8. Rasterization | [glDrawArrays(GL_TRIANGLE_STRIP,0,4)](../src/main.cpp#L50) rasterizes the four-vertex carrier geometry. Interpolated texture coordinates reach the fragment shader | Show the quad vertex input and the fragment shader that turns its coverage into a scene image. |
| 9. Fragment/output processing | [HDRFramebuffer.cpp](../src/HDRFramebuffer.cpp) allocates GL_RGBA16F and checks completeness; [BloomEffect.cpp](../src/BloomEffect.cpp) performs bloom; [main.cpp](../src/main.cpp#L201) composites, then captures via glReadPixels | Trace scene-linear HDR through bloom, display composition and native RGB24 readback, then FFmpeg encoding. |

## Mapping to the supplied programmable-pipeline example

| Example stage | Actual status and relevant calls |
| --- | --- |
| Vertex specification/input assembly | Implemented: glGenVertexArrays, glGenBuffers, glBufferData, glEnableVertexAttribArray and glVertexAttribPointer in [main.cpp](../src/main.cpp#L128). Positions and UVs have a four-float stride. |
| Vertex shader processing | Implemented: [screen.vert](../shaders/postprocess/screen.vert) copies UVs and sets gl_Position. [Shader.cpp](../src/Shader.cpp) creates, compiles and links GL_VERTEX_SHADER and GL_FRAGMENT_SHADER programs, checking both status and logs. |
| Tessellation processing | **Not implemented in the current film.** The requested context is OpenGL 3.3, and the inspected Shader class creates no tessellation control/evaluation stages. Do not claim this stage from an implicit surface or a dense ray march. |
| Geometry shader processing | **Not implemented by the inspected Shader class.** There is no geometry-stage compilation in that class. A procedural galaxy catalogue is not itself evidence of a geometry shader. |
| Primitive assembly/clipping | Implemented through GL_TRIANGLE_STRIP draw submission and OpenGL's clip-space pipeline. No custom clipping shader is required for the carrier quad. |
| Rasterization | Implemented by OpenGL for the carrier quad and catalogue draw calls. The fragment shader evaluates implicit objects after rasterization. |
| Fragment shader processing | Implemented by the loaded GLSL scene and postprocess programs. It includes procedural ray construction/traversal and surface/volume shading. |
| Per-fragment operations | Blending is explicitly configured: GL_SRC_ALPHA/GL_ONE_MINUS_SRC_ALPHA for overlays and GL_SRC_ALPHA/GL_ONE for additive contributions in [main.cpp](../src/main.cpp#L163). Depth testing is disabled in the main screen-volume path at [line 111](../src/main.cpp#L111). The HDR framebuffer allocates GL_DEPTH24_STENCIL8, but allocation does **not** demonstrate depth/stencil testing; stencil operations are not established by this code. |
| Framebuffer output/post-processing | Implemented: HDR FBO attachment, completeness checks, bloom, composite draw and glReadPixels. The capture code rejects mismatched dimensions and separates diagnostics from the raw byte stream. |

Tessellation and geometry shaders are optional OpenGL stages. Whether this course requires a separate demonstration of either remains unresolved. If the actual rubric requires them, implement and test a separate demonstration with a suitable context; do not alter the approved film merely to imply support.

## Reproducible demonstration

Build and test using the [README](../README.md). Run the application on a working display. Capture a known scene at an exact time, show its C++ program selection and associated GLSL source, then compare the native capture manifest against FFprobe output. For headless checks use the [bounded native UHD workflow](../.github/workflows/native-4k-validation.yml).

At 30 FPS, one-based frame N samples (N-1)/30 seconds. The final range 1–9000 represents 300 seconds of playback. The native tests cover film timing, camera anchors/continuity, capture arguments, UHD acceptance, oversized rejection and PNG headers. The Python suite covers supervised capture/checkpoint and validation behavior. Passing these tests does not prove that the entire final film is visually accepted.

## Limits of the evidence

A successful C++ build does not prove GLSL compilation. Successful native scene capture exercises actual shader loading/compilation/linking and framebuffer setup, but short clips cannot prove full-film temporal consistency. Every final segment and the assembled audiovisual film still require decoded-frame validation, transition inspection and complete viewing/listening.

No final 4K acceptance, lecturer-rubric confirmation, tessellation implementation, geometry-stage implementation or stencil demonstration is claimed by this document. Scientific time, colors, scales and optical effects are compressed and art-directed; this is an educational visualization, not a quantitative simulation.
