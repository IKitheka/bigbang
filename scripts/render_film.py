#!/usr/bin/env python3
"""Render a native film in verified, restartable chunks; never starts by default.

Example bounded check:
  python3 scripts/render_film.py --output-dir output/check --first-frame 1 --end-frame 60
Full film (explicit invocation):
  python3 scripts/render_film.py --output-dir output/film
Resume only with the same renderer/source/settings:
  python3 scripts/render_film.py --output-dir output/film --resume

The native executable must emit top-down RGB24 frames on stdout and all logs on
stderr. Frame IDs are one-based; frame N samples time (N-1)/fps. Each inclusive
native batch uses one GL context. Only verified chunks enter checkpoint.json.
The final film.mp4 is atomically published after exact frame count, dimensions,
rate, and a full bounded decode pass. A bounded range produces a shorter movie.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 2
DURATION_SECONDS = 300
RENDER_ENVIRONMENT_KEYS = (
    "LIBGL_ALWAYS_SOFTWARE", "MESA_LOADER_DRIVER_OVERRIDE", "GALLIUM_DRIVER",
    "EGL_PLATFORM", "LIBGL_DRIVERS_PATH", "MESA_GL_VERSION_OVERRIDE",
    "MESA_GLSL_VERSION_OVERRIDE",
)


class RenderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Chunk:
    first: int
    stop: int  # Exclusive internally; the native CLI receives stop-1.

    @property
    def count(self) -> int:
        return self.stop - self.first

    @property
    def name(self) -> str:
        return f"frames_{self.first:06d}_{self.stop - 1:06d}.mp4"


def frame_chunks(first: int, stop: int, size: int) -> Iterator[Chunk]:
    if first < 1 or stop <= first or size < 1:
        raise RenderError("Invalid one-based frame range or chunk size")
    for start in range(first, stop, size):
        yield Chunk(start, min(start + size, stop))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("expected JSON object")
        return value
    except (OSError, ValueError) as exc:
        raise RenderError(f"Cannot read {path.name}: {exc}") from exc


def checked_command(command: list[str], *, timeout: float, **kwargs) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, check=True, timeout=timeout, **kwargs)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        diagnostic = getattr(exc, "stderr", None)
        if isinstance(diagnostic, bytes):
            diagnostic = diagnostic.decode("utf-8", errors="replace")
        raise RenderError(f"{Path(command[0]).name} failed: {exc}"
                          + (f"\n{diagnostic[-2000:]}" if diagnostic else "")) from exc


def source_fingerprint(root: Path) -> dict:
    # Include tracked code, local modifications, and new unignored renderer
    # files. New shaders must never silently bypass checkpoint invalidation.
    result = checked_command(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        timeout=15, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    selected = set()
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        name = os.fsdecode(raw)
        if name.startswith(("src/", "include/", "shaders/", "cmake/")) or name in {
            "CMakeLists.txt", "scripts/render_film.py"
        }:
            selected.add(name)
    if not selected:
        raise RenderError("No renderer sources found in Git checkout")
    entries = []
    for name in sorted(selected):
        path = root / name
        if not path.is_file():
            # A tracked deletion changes identity just as a content edit does.
            entries.append({"path": name, "sha256": "DELETED"})
        else:
            entries.append({"path": name, "sha256": file_sha256(path)})
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, timeout=15)
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "files": entries,
            "git_head": head.stdout.strip() if head.returncode == 0 else None}


def tool_version(executable: str) -> str:
    result = checked_command([executable, "-version"], timeout=15,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.splitlines()[0]


def renderer_identity(binary: Path) -> dict:
    """Query the actual hidden GL context without rendering scene pixels."""
    result = checked_command(
        [str(binary), "--renderer-info", "--width", "16", "--height", "16"],
        timeout=30, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    expected = {"opengl_version", "renderer", "vendor", "shading_language_version"}
    identity = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        if not separator or key not in expected or key in identity or not value.strip():
            raise RenderError("Native renderer returned malformed OpenGL identity")
        identity[key] = value.strip()
    if set(identity) != expected:
        raise RenderError("Native renderer returned incomplete OpenGL identity")
    return identity


def probe_video(path: Path, *, width: int, height: int, fps: int,
                frames: int, ffprobe: str, ffmpeg: str) -> dict:
    # Count decoded frames rather than trusting a container's optional nb_frames.
    # A separate strict decode catches truncation, corrupt packets and bad tails.
    timeout = max(30.0, min(1800.0, frames / fps * 4.0 + 30.0))
    result = checked_command(
        [ffprobe, "-v", "error", "-count_frames", "-show_entries",
         "stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames:format=duration",
         "-of", "json", str(path)], timeout=timeout,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        data = json.loads(result.stdout)
        streams = data["streams"]
        video = streams[0]
        actual_frames = int(video["nb_read_frames"])
        actual_rate = Fraction(video["avg_frame_rate"])
        duration = float(data["format"]["duration"])
        valid = (len(streams) == 1 and video["codec_type"] == "video"
                 and video["codec_name"] == "h264"
                 and (video["width"], video["height"]) == (width, height)
                 and actual_rate == Fraction(fps, 1) and actual_frames == frames
                 and abs(duration - frames / fps) <= max(0.003, 0.1 / fps))
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as exc:
        raise RenderError(f"Invalid video metadata: {path.name}: {exc}") from exc
    if not valid:
        raise RenderError(f"Video metadata mismatch for {path.name}: expected "
                          f"{width}x{height}, {fps} fps, {frames} frames; got {data}")
    # No shell, no unbounded stderr capture; -xerror fails on decoding errors.
    decoded = checked_command(
        [ffmpeg, "-nostdin", "-v", "error", "-xerror", "-i", str(path),
         "-map", "0:v:0", "-f", "null", "-"], timeout=timeout,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if decoded.stderr.strip():
        raise RenderError(f"Decode diagnostics for {path.name}: {decoded.stderr[-2000:]}")
    return {"width": width, "height": height, "fps": fps, "frames": frames,
            "duration_seconds": duration, "sha256": file_sha256(path),
            "decode_verified": True, "decode_timeout_seconds": timeout}


def stop_process(process: subprocess.Popen | None) -> None:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def encode_chunk(chunk: Chunk, options, output: Path, ffmpeg: str) -> dict:
    destination = output / "chunks" / chunk.name
    partial = destination.with_name(destination.stem + ".partial.mp4")
    renderer_log = output / "logs" / (destination.stem + ".renderer.log")
    encoder_log = output / "logs" / (destination.stem + ".encoder.log")
    render_command = [str(options.binary), "--start-frame", str(chunk.first),
                      "--end-frame", str(chunk.stop - 1), "--fps", str(options.fps),
                      "--width", str(options.width), "--height", str(options.height),
                      "--raw-video", "-"]
    encode_command = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "warning", "-y",
                      "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size",
                      f"{options.width}x{options.height}", "-framerate", str(options.fps),
                      "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", options.preset,
                      "-crf", str(options.crf), "-pix_fmt", "yuv420p",
                      "-movflags", "+faststart", str(partial)]
    start = time.monotonic()
    producer = consumer = None
    try:
        with renderer_log.open("wb") as native_log, encoder_log.open("wb") as codec_log:
            producer = subprocess.Popen(render_command, stdout=subprocess.PIPE, stderr=native_log,
                                        cwd=ROOT)
            consumer = subprocess.Popen(encode_command, stdin=producer.stdout,
                                        stdout=subprocess.DEVNULL, stderr=codec_log)
            # Let an encoder failure close the producer's pipe instead of hanging.
            assert producer.stdout is not None
            producer.stdout.close()
            producer_status = producer.wait(timeout=options.chunk_timeout)
            consumer_status = consumer.wait(timeout=60)
            if producer_status != 0 or consumer_status != 0:
                raise RenderError(f"Frames {chunk.first}..{chunk.stop - 1} failed "
                                  f"(renderer={producer_status}, encoder={consumer_status}); "
                                  f"inspect {renderer_log.name} and {encoder_log.name}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RenderError(f"Chunk {chunk.name} failed: {exc}") from exc
    finally:
        stop_process(producer)
        stop_process(consumer)
    return {"partial": partial, "destination": destination,
            "render_command": render_command, "encode_command": encode_command,
            "render_and_encode_wall_seconds": time.monotonic() - start,
            "renderer_log": str(renderer_log.relative_to(output)),
            "encoder_log": str(encoder_log.relative_to(output))}


def _run_locked(options, *, root: Path = ROOT) -> dict:
    output = options.output_dir.resolve()
    options.binary = options.binary.resolve()
    if not options.binary.is_file() or not os.access(options.binary, os.X_OK):
        raise RenderError(f"Native executable missing or not executable: {options.binary}")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RenderError("ffmpeg and ffprobe must both be installed")
    source = source_fingerprint(root)
    render_environment = {key: os.environ[key] for key in RENDER_ENVIRONMENT_KEYS
                          if key in os.environ}
    identity = {"schema": SCHEMA, "source_sha256": source["sha256"],
                "binary_sha256": file_sha256(options.binary),
                "renderer": renderer_identity(options.binary),
                "render_environment": render_environment,
                "width": options.width, "height": options.height, "fps": options.fps,
                "first_frame": options.first_frame, "end_frame": options.end_frame,
                "chunk_frames": options.chunk_frames,
                "encoder": {"codec": "libx264", "crf": options.crf,
                            "preset": options.preset, "pixel_format": "yuv420p"},
                "ffmpeg": tool_version(ffmpeg), "ffprobe": tool_version(ffprobe)}
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "manifest.json"
    checkpoint_path = output / "checkpoint.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if manifest.get("identity") != identity:
            raise RenderError("Existing output manifest differs from current source, binary, "
                              "OpenGL driver/environment or render settings; choose a new output directory")
        if not options.resume:
            raise RenderError("Output manifest exists; use --resume to revalidate and continue")
        state = read_json(checkpoint_path) if checkpoint_path.exists() else {
            "schema": SCHEMA, "identity": identity, "chunks": {}, "invalidations": []}
        if state.get("schema") != SCHEMA or state.get("identity") != identity:
            raise RenderError("Checkpoint identity differs from output manifest")
        if not isinstance(state.get("chunks"), dict):
            raise RenderError("Checkpoint chunks must be a JSON object")
    else:
        if any(path.name != ".render.lock" for path in output.iterdir()):
            raise RenderError("Output directory is not empty and has no matching manifest")
        manifest = {"schema": SCHEMA, "identity": identity, "source": source,
                    "created_utc": utc_now(), "native_binary": str(options.binary),
                    "frame_semantics": "one-based; time_seconds=(frame-1)/fps; inclusive CLI endpoints",
                    "expected_frames": options.end_frame - options.first_frame + 1,
                    "expected_duration_seconds":
                        (options.end_frame - options.first_frame + 1) / options.fps,
                    "complete_300_second_range": options.first_frame == 1 and
                        options.end_frame == DURATION_SECONDS * options.fps,
                    "host": {"platform": platform.platform(), "python": platform.python_version()},
                    "render_environment": render_environment,
                    "renderer": identity["renderer"],
                    "verification": "sha256 + ffprobe decoded frame count/rate/size + strict full decode"}
        atomic_json(manifest_path, manifest)
        state = {"schema": SCHEMA, "identity": identity, "chunks": {}, "invalidations": []}
    (output / "chunks").mkdir(exist_ok=True)
    (output / "logs").mkdir(exist_ok=True)
    state["status"] = "rendering"
    state.pop("last_error", None)
    state["updated_utc"] = utc_now()
    atomic_json(checkpoint_path, state)
    started = time.monotonic()
    try:
        chunks = list(frame_chunks(options.first_frame, options.end_frame + 1,
                                   options.chunk_frames))
        for index, chunk in enumerate(chunks, 1):
            path = output / "chunks" / chunk.name
            previous = state["chunks"].get(chunk.name)
            if previous is not None:
                try:
                    if previous.get("first_frame") != chunk.first or previous.get("end_frame") != chunk.stop - 1:
                        raise RenderError("Saved chunk frame range differs")
                    if not path.is_file() or file_sha256(path) != previous.get("sha256"):
                        raise RenderError("Saved chunk missing or checksum differs")
                    probe_video(path, width=options.width, height=options.height,
                                fps=options.fps, frames=chunk.count,
                                ffprobe=ffprobe, ffmpeg=ffmpeg)
                    print(f"Verified chunk {index}/{len(chunks)}: frames {chunk.first}..{chunk.stop-1}",
                          file=sys.stderr, flush=True)
                    continue
                except RenderError as exc:
                    state["chunks"].pop(chunk.name)
                    state.setdefault("invalidations", []).append({"file": chunk.name,
                        "reason": str(exc), "utc": utc_now()})
                    state.pop("final", None)
                    atomic_json(checkpoint_path, state)
                    print(f"Rebuilding invalid chunk {chunk.name}: {exc}", file=sys.stderr, flush=True)
            print(f"Rendering chunk {index}/{len(chunks)}: frames {chunk.first}..{chunk.stop-1}",
                  file=sys.stderr, flush=True)
            details = encode_chunk(chunk, options, output, ffmpeg)
            metadata = probe_video(details["partial"], width=options.width,
                                   height=options.height, fps=options.fps,
                                   frames=chunk.count, ffprobe=ffprobe, ffmpeg=ffmpeg)
            # A code edit while a long job runs must never bless mixed sources.
            if source_fingerprint(root)["sha256"] != identity["source_sha256"] or \
                    file_sha256(options.binary) != identity["binary_sha256"]:
                raise RenderError("Renderer source or binary changed during rendering; "
                                  "partial chunk was not checkpointed")
            os.replace(details.pop("partial"), details.pop("destination"))
            metadata.update(details)
            metadata.update({"first_frame": chunk.first, "end_frame": chunk.stop - 1,
                             "file": f"chunks/{chunk.name}", "verified_utc": utc_now(),
                             "frame_count": chunk.count})
            state["chunks"][chunk.name] = metadata
            state["updated_utc"] = utc_now()
            atomic_json(checkpoint_path, state)
        # Concat uses only generated relative names, never user-provided paths.
        concat_path = output / "concat.txt"
        concat_path.write_text("".join(f"file 'chunks/{chunk.name}'\n" for chunk in chunks),
                               encoding="utf-8")
        final_path = output / "film.mp4"
        temporary = output / "film.partial.mp4"
        expected = options.end_frame - options.first_frame + 1
        final_valid = False
        if options.resume and state.get("final") and final_path.is_file():
            try:
                if file_sha256(final_path) != state["final"].get("sha256"):
                    raise RenderError("Final movie checksum differs")
                final_metadata = probe_video(final_path, width=options.width, height=options.height,
                    fps=options.fps, frames=expected, ffprobe=ffprobe, ffmpeg=ffmpeg)
                final_valid = True
            except RenderError:
                state.pop("final", None)
        if not final_valid:
            checked_command([ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "1", "-i", str(concat_path), "-an", "-c:v", "copy",
                "-movflags", "+faststart", str(temporary)], timeout=300,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            final_metadata = probe_video(temporary, width=options.width, height=options.height,
                fps=options.fps, frames=expected, ffprobe=ffprobe, ffmpeg=ffmpeg)
            os.replace(temporary, final_path)
        state["final"] = dict(final_metadata, file="film.mp4", verified_utc=utc_now())
        state["status"] = "complete"
        state["updated_utc"] = utc_now()
        state["last_invocation_wall_seconds"] = time.monotonic() - started
        state["completed_chunks_render_encode_wall_seconds"] = sum(
            part.get("render_and_encode_wall_seconds", 0.0) for part in state["chunks"].values())
        atomic_json(checkpoint_path, state)
        print(f"Verified movie: {final_path} ({expected} frames, {expected/options.fps:.3f} seconds)",
              file=sys.stderr, flush=True)
        return state
    except BaseException as exc:
        state["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        state["last_error"] = str(exc) or type(exc).__name__
        state["updated_utc"] = utc_now()
        state["last_invocation_wall_seconds"] = time.monotonic() - started
        atomic_json(checkpoint_path, state)
        raise


def run(options, *, root: Path = ROOT) -> dict:
    # The advisory lock is released by the OS after a crash. Its empty file may
    # remain, but a second live renderer may not mutate this output directory.
    output = options.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".render.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RenderError("Another render already owns this output directory") from exc
        return _run_locked(options, root=root)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--binary", type=Path, default=ROOT / "build" / "bigbang")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, choices=(30, 60), default=30)
    parser.add_argument("--chunk-frames", type=int, default=300,
                        help="Frames per checkpoint (300 = 10 seconds at 30 fps)")
    parser.add_argument("--first-frame", type=int, default=1)
    parser.add_argument("--end-frame", type=int)
    parser.add_argument("--crf", type=int, choices=(16, 18), default=18)
    parser.add_argument("--preset", choices=("ultrafast", "fast", "medium", "slow"), default="medium")
    parser.add_argument("--chunk-timeout", type=float, default=1800,
                        help="Maximum native render seconds per chunk; completed chunks survive timeout")
    parser.add_argument("--resume", action="store_true")
    options = parser.parse_args(argv)
    if options.end_frame is None:
        options.end_frame = DURATION_SECONDS * options.fps
    if options.width < 2 or options.height < 2 or options.width % 2 or options.height % 2:
        parser.error("width and height must be positive even numbers for yuv420p")
    if not 1 <= options.first_frame <= options.end_frame <= DURATION_SECONDS * options.fps:
        parser.error("frame range must lie inside the one-based 300-second film")
    if options.chunk_frames < 1 or options.chunk_timeout <= 0:
        parser.error("chunk size and timeout must be positive")
    return options


def main(argv=None) -> int:
    try:
        run(parse_args(argv))
        return 0
    except (RenderError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Render failed: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Render interrupted; verified chunks remain available for --resume", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
