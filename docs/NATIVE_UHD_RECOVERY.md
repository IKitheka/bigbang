# Native UHD production and recovery

This is continuation work for draft PR #24. The immutable renderer remains commit 461ed7c8f3b93428b2ed869e9238963cdef29f5e; no additional scene, camera, exposure, bloom, resolution or timing changes are introduced by this production workflow. V4–V11 history and the approved Solar System/Earth source remain preserved. This document is operational evidence, not final-film acceptance.

## Execution route

The local execution/file bridge reproduced the IPC decoder failure: unknown field result_buffered_for_ns, expected cell_id, content_items, error_text or code_mode_host_duration_ns. Even a minimal tool-discovery call failed. GitHub browser editing and GitHub Actions remained usable, so code and workflow changes were saved directly on release/native-4k-university-final.

The workflow native-4k-recoverable.yml builds the exact saved renderer once, records the source commit and a SHA-256-protected executable tarball, and distributes that same executable to every capture runner. Documentation/CI commits do not invalidate approved scene content. The absolute native checkout path is kept consistent because the binary embeds PROJECT_ROOT.

The 2026-11-15 runner reports OpenGL 4.5 Core, Mesa 25.2.8, LLVM 20.1.2 llvmpipe. A separate query with software overrides removed still reports llvmpipe. Repository Settings → Actions → Runners shows no self-hosted runners configured. Local GPU discovery remains blocked by the execution bridge. A GPU context has not been claimed. An existing authorized GPU environment can be benchmarked separately; its driver identity must not be silently mixed with CPU checkpoints.

## Continuous benchmark

[Run 43749106085](https://github.com/IKitheka/bigbang/actions/runs/43749106085) captures six 90-frame native 3840x2160 clips at 30 FPS. Each clip is three seconds of continuous playback. A native context renders 30 consecutive frames per checkpoint, compared with the earlier three single-frame pilots. The six part IDs are 002 (181–270), 010 (901–990), 016 (1441–1530), 063 (5671–5760), 083 (7471–7560) and 097 (8731–8820).

Measured completed samples at the time this document was prepared:

| Part | Global time interval | Three batch times | Mean seconds per frame |
|---|---|---|---|
| 063 | 189–192s | 78.282, 77.809, 77.654s | 2.597 |
| 083 | 249–252s | 119.908, 118.900, 118.688s | 3.972 |
| 097 | 291–294s | 15.693, 15.544, 15.783s | 0.522 |

Each completed clip passed decoded geometry, exact 90-frame count, exact 30 FPS, three-second duration, checksums and strict decode. A second --resume invocation revalidated all chunks and left their modification times unchanged. These are observed render-and-encode batch timings, not whole-film performance or subjective motion approval. The authoritative per-part JSON and logs in the linked run supersede this interim table.

## Full production contract

The production scope selects 100 disjoint parts: part i has inclusive frames 90*i+1 through 90*(i+1), with i=0..99. Each part checkpoints three batches of 30 frames. The union is exactly 1..9000; frame N samples (N-1)/30 seconds. The final sample is at 299.9666667 seconds and the playback duration is 300 seconds.

The production run restores completed pilot parts from the benchmark run. Both the executable archive and completed chunks are reused. Fresh batches use native dimensions 3840x2160, 30 FPS, libx264 fast / CRF 16 / yuv420p. Twelve jobs may run concurrently. A native batch has a 1,200-second timeout; the capture step has a 55-minute bound inside a 65-minute job. Verified earlier batches remain on disk and are uploaded even if a later batch fails.

Every part artifact contains manifest.json, checkpoint.json, ALL chunk MP4s, the assembled three-second MP4 when complete, renderer/encoder logs and measured timing JSON. This fixes the older production workflows' limitation of preserving a final part without all recoverable chunks. Actions artifacts have 90-day retention; they are recovery storage, not the durable final release.

## Recovery procedure

1. Preserve the original renderer commit, executable tarball and source/driver/encoder identity. Do not rebuild or edit manifest fields to make a mismatch pass.
2. For failed jobs in the same run, use GitHub Actions Re-run failed jobs. The workflow downloads its current-run part artifact, validates it through --resume, and renders only missing or invalid chunks. Recovered review images are safely recreated.
3. To continue in a new run, set recovery_run (or the push fallback RECOVERY_RUN in the workflow) to the latest run that contains the desired checkpoints and uhd-renderer artifact. Select production scope. If workflow_dispatch is unavailable because the workflow is not on the repository default branch, an explicitly reviewed commit to this workflow triggers the configured branch push event.
4. A new run lists that recovery run's unexpired part artifacts before building its matrix. Available parts are restored; absent parts are rendered. Restore/download failures stop the affected job. Identity mismatches stop capture instead of combining sources. A failed-job rerun uses current-run artifacts without first extracting an older copy over them.
5. Re-run the assembly job after all source parts pass. Assembly does not need to render approved frames again. Keep Actions artifacts until durable release upload and independent download checks finish.

A hard runner loss can still lose the active uncheckpointed batch; it cannot produce a falsely verified checkpoint. Normal timeout/failure paths preserve all previously verified chunks. No background service or local terminal is needed for a submitted Actions run to continue.

## Assembly and package gates

scripts/assemble_native_4k.py uses the original render_film validators and additionally requires exact 100-part coverage; unique aligned ranges; native geometry; matching source fingerprint, executable, driver/environment and encoder identity; matching checkpoint hashes; and fresh strict decoding after artifact transport. Pilot-only audit mode can validate a subset, but does not create a full film.

The production preflight uses an actual transported UHD pilot. It checks a valid 90-frame part and rejection of incomplete full-film coverage, a 1080p substitution, a wrong executable, a wrong source commit, corrupted chunk bytes and duplicate frame coverage. These preflight checks must pass before the production matrix starts; the Actions logs establish whether they actually passed.

Assembly stream-copies the verified native picture. The unchanged create_original_score.py regenerates the original seeded 300-second stereo score as 32 kHz, 16-bit PCM. Muxing encodes 48 kHz stereo AAC. Video essence hashes must match before/after audio muxing. Both streams must start at zero, last 300 seconds within codec tolerances, and pass strict decoding. The master must contain 9,000 UHD video frames at 30 FPS.

The 1080p and easy-play 360p editions are explicitly derived from that UHD master. Each receives a separate decoded-frame/geometry/rate/duration/stereo check and strict full decode. The package also extracts a 25-panel storyboard, eight native UHD stills, chapter-boundary screening metrics, source archives, checksums, technical Markdown report and the existing nine-stage documentation. ZIP archives are reopened and CRC checked; each archive has a checksum list for its own contents.

## Remaining acceptance

The CI assembly output is labelled technical screening. It must not be described as the completed university submission. Full-film viewing and listening, visual transition approval, any justified refinement, the finished presentation/report exports, durable final GitHub Release publication, and independent download/ZIP/media checks remain acceptance items. Numerical transition flags are screening aids, not artistic approval. The existing nine-stage document explicitly distinguishes implemented OpenGL stages from absent optional tessellation, geometry-shader and stencil operations.

No lower-resolution V11 frame is substituted for native UHD work. The existing single-frame RGB comparisons and earlier 1080p movie remain prior evidence with their original provenance.
