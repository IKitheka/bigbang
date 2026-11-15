#!/usr/bin/env python3
"""Checkpoint/resume acceptance tests; tiny RGB fixture is not a scene render.

Run: python3 -m unittest discover -s tests -p test_film_render.py -v
The integration tests use actual ffmpeg/ffprobe with a 32x18 synthetic native-CLI
fixture. They test the delivery pipeline, not OpenGL quality or scene content.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_film.py"
spec = importlib.util.spec_from_file_location("film_render_under_test", SCRIPT)
film = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = film
spec.loader.exec_module(film)


class FrameIdentityTests(unittest.TestCase):
    def test_full_film_has_no_repeated_or_skipped_boundary_frames(self):
        for fps in (30, 60):
            chunks = list(film.frame_chunks(1, 300 * fps + 1, fps * 10))
            ids = [frame for chunk in chunks for frame in range(chunk.first, chunk.stop)]
            self.assertEqual(ids, list(range(1, 300 * fps + 1)))
            self.assertEqual(len(chunks), 30)
            self.assertEqual((ids[-1] - 1) / fps, 300 - 1 / fps)

    def test_bounded_range_keeps_partial_last_chunk_and_single_frame(self):
        chunks = list(film.frame_chunks(48, 56, 3))
        self.assertEqual([(c.first, c.stop - 1) for c in chunks], [(48, 50), (51, 53), (54, 55)])
        self.assertEqual(sum(c.count for c in chunks), 8)
        self.assertEqual(next(film.frame_chunks(9000, 9001, 300)).count, 1)
        for args in ((0, 9, 3), (1, 1, 3), (1, 9, 0)):
            with self.assertRaises(film.RenderError):
                list(film.frame_chunks(*args))

    def test_cli_refuses_outside_film_and_odd_encoder_dimensions(self):
        for extra in (("--first-frame", "0"), ("--end-frame", "9001"), ("--width", "33")):
            with self.assertRaises(SystemExit):
                film.parse_args(["--output-dir", "unused", *extra])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe") and shutil.which("git"),
                     "Integration requires ffmpeg, ffprobe and git")
class DeliveryAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="native-film-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        (self.root / "build").mkdir()
        (self.root / "shaders").mkdir()
        (self.root / "src").mkdir()
        shutil.copy2(SCRIPT, self.root / "scripts" / "render_film.py")
        (self.root / "src" / "scene.cpp").write_text("// renderer identity fixture\n")
        (self.root / "shaders" / "scene.frag").write_text("// shader identity fixture\n")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "src", "shaders", "scripts"], check=True)
        self.binary = self.root / "build" / "bigbang"
        self.binary.write_text('''#!/usr/bin/env python3
import argparse, json, os, sys
from pathlib import Path
if "--renderer-info" in sys.argv:
    if os.environ.get("FIXTURE_BAD_INFO"):
        print("not a valid renderer identity")
    else:
        print("opengl_version=fixture OpenGL 3.3")
        print("renderer="+os.environ.get("FIXTURE_GL_RENDERER", "fixture renderer 1"))
        print("vendor=fixture vendor")
        print("shading_language_version=fixture GLSL 3.30")
    raise SystemExit(0)
p = argparse.ArgumentParser()
for name in ("start-frame", "end-frame", "fps", "width", "height"):
    p.add_argument("--"+name, type=int, required=True)
p.add_argument("--raw-video", required=True)
a = p.parse_args()
assert a.raw_video == "-"
with Path(__file__).with_name("invocations.jsonl").open("a") as handle:
    handle.write(json.dumps([a.start_frame, a.end_frame])+"\\n")
if os.environ.get("FIXTURE_FAIL_START") == str(a.start_frame):
    print("intentional fixture failure", file=sys.stderr)
    raise SystemExit(7)
for frame in range(a.start_frame, a.end_frame+1):
    pixel = bytes((frame*19 % 200, 48, 96))
    sys.stdout.buffer.write(pixel*(a.width*a.height))
''')
        self.binary.chmod(0o755)
        self.output = self.root / "output"

    def invoke(self, *extra, env=None, expected=0):
        command = [sys.executable, str(self.root / "scripts" / "render_film.py"),
                   "--output-dir", str(self.output), "--width", "32", "--height", "18",
                   "--first-frame", "2", "--end-frame", "7", "--chunk-frames", "3",
                   "--preset", "ultrafast", *extra]
        result = subprocess.run(command, cwd=self.root, env=dict(os.environ, **(env or {})),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        self.assertEqual(result.returncode, expected, result.stderr)
        # The pipeline must not mix binary video into its own output/log protocol.
        self.assertEqual(result.stdout, "")
        return result

    def invocations(self):
        path = self.binary.with_name("invocations.jsonl")
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def checkpoint(self):
        return json.loads((self.output / "checkpoint.json").read_text())

    def test_exact_native_ranges_verified_movie_and_idempotent_resume(self):
        self.invoke()
        self.assertEqual(self.invocations(), [[2, 4], [5, 7]])
        state = self.checkpoint()
        self.assertEqual(state["status"], "complete")
        self.assertEqual(state["final"]["frames"], 6)
        self.assertAlmostEqual(state["final"]["duration_seconds"], 0.2, places=3)
        self.assertTrue(state["final"]["decode_verified"])
        self.assertTrue(all(chunk["decode_verified"] for chunk in state["chunks"].values()))
        manifest = json.loads((self.output / "manifest.json").read_text())
        self.assertFalse(manifest["complete_300_second_range"])
        self.assertEqual(manifest["identity"]["renderer"]["renderer"], "fixture renderer 1")
        self.invoke("--resume")
        self.assertEqual(self.invocations(), [[2, 4], [5, 7]], "Resume unexpectedly rendered valid chunks")
        self.assertEqual(self.checkpoint()["final"]["sha256"], state["final"]["sha256"])

    def test_existing_output_requires_explicit_matching_resume(self):
        self.invoke()
        result = self.invoke(expected=1)
        self.assertIn("use --resume", result.stderr)
        result = self.invoke("--resume", "--width", "34", expected=1)
        self.assertIn("manifest differs", result.stderr)
        (self.root / "shaders" / "new_untracked.glsl").write_text("// a new render field\n")
        result = self.invoke("--resume", expected=1)
        self.assertIn("manifest differs", result.stderr)
        self.assertEqual(self.invocations(), [[2, 4], [5, 7]])

    def test_corrupt_chunk_is_rebuilt_and_final_corruption_is_not_reused(self):
        self.invoke()
        first_chunk = next(iter(sorted((self.output / "chunks").glob("*.mp4"))))
        first_chunk.write_bytes(b"not a playable MP4")
        (self.output / "film.mp4").write_bytes(b"corrupt final")
        result = self.invoke("--resume")
        self.assertIn("Rebuilding invalid chunk", result.stderr)
        self.assertEqual(self.invocations(), [[2, 4], [5, 7], [2, 4]])
        state = self.checkpoint()
        self.assertEqual(state["status"], "complete")
        self.assertEqual(len(state["invalidations"]), 1)
        self.assertTrue(state["final"]["decode_verified"])
        self.assertGreater((self.output / "film.mp4").stat().st_size, 100)

    def test_resume_refuses_changed_actual_driver_or_render_environment(self):
        self.invoke()
        original = self.checkpoint()
        for changed in ({"FIXTURE_GL_RENDERER": "different GL driver"},
                        {"GALLIUM_DRIVER": "different-environment-driver"}):
            result = self.invoke("--resume", env=changed, expected=1)
            self.assertIn("manifest differs", result.stderr)
            self.assertEqual(self.invocations(), [[2, 4], [5, 7]])
            self.assertEqual(self.checkpoint(), original)

    def test_missing_actual_driver_identity_cannot_create_checkpoint(self):
        result = self.invoke(env={"FIXTURE_BAD_INFO": "1"}, expected=1)
        self.assertIn("OpenGL identity", result.stderr)
        self.assertFalse((self.output / "manifest.json").exists())
        self.assertFalse((self.output / "checkpoint.json").exists())
        self.assertEqual(self.invocations(), [])

    def test_hash_alone_cannot_bless_bad_chunk_metadata(self):
        self.invoke()
        checkpoint = self.checkpoint()
        key = sorted(checkpoint["chunks"])[0]
        # Even if a corrupted checkpoint claims a matching content hash, a
        # wrong native range must not be reused as the requested frame range.
        checkpoint["chunks"][key]["first_frame"] = 1
        (self.output / "checkpoint.json").write_text(json.dumps(checkpoint))
        self.invoke("--resume")
        self.assertEqual(self.invocations(), [[2, 4], [5, 7], [2, 4]])

    def test_interrupted_batch_preserves_only_completed_chunks(self):
        result = self.invoke(env={"FIXTURE_FAIL_START": "5"}, expected=1)
        self.assertIn("renderer=7", result.stderr)
        state = self.checkpoint()
        self.assertEqual(state["status"], "failed")
        self.assertEqual(len(state["chunks"]), 1)
        self.assertNotIn("final", state)
        self.assertFalse((self.output / "film.mp4").exists())
        self.invoke("--resume")
        self.assertEqual(self.invocations(), [[2, 4], [5, 7], [5, 7]])
        self.assertEqual(self.checkpoint()["status"], "complete")

    def test_unmanaged_nonempty_output_is_not_overwritten(self):
        self.output.mkdir()
        keep = self.output / "unrelated.mp4"
        keep.write_bytes(b"keep this file")
        result = self.invoke(expected=1)
        self.assertIn("no matching manifest", result.stderr)
        self.assertEqual(keep.read_bytes(), b"keep this file")
        self.assertEqual(self.invocations(), [])


if __name__ == "__main__":
    unittest.main()
