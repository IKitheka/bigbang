#!/usr/bin/env python3
"""Inspect PNGs actually rendered by the C++ executable; never generates images."""
import argparse
import hashlib
import struct
import zlib
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"

def inspect(path: Path, width: int, height: int, allow_flat: bool = False):
    payload = path.read_bytes()
    assert payload.startswith(SIGNATURE), f"not a PNG: {path}"
    offset = 8
    data = bytearray()
    actual = None
    end_found = False
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset:offset + 4])[0]
        kind = payload[offset + 4:offset + 8]
        body = payload[offset + 8:offset + 8 + length]
        end = offset + 12 + length
        assert end <= len(payload), f"truncated PNG chunk in {path}"
        crc = struct.unpack(">I", payload[offset + 8 + length:end])[0]
        assert crc == zlib.crc32(kind + body), f"bad PNG CRC: {path}"
        if kind == b"IHDR":
            w, h, bits, color, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", body)
            assert (bits, color, compression, filtering, interlace) == (8, 2, 0, 0, 0)
            actual = (w, h)
        if kind == b"IDAT":
            data.extend(body)
        if kind == b"IEND":
            end_found = True
            break
        offset = end
    assert end_found and actual == (width, height), f"wrong size/invalid PNG {path}: {actual}"
    raw = zlib.decompress(data)
    stride = 1 + 3 * width
    assert len(raw) == height * stride, f"wrong decompressed length {path}"
    assert all(raw[i] == 0 for i in range(0, len(raw), stride)), "expected filter 0"
    pixels = bytearray()
    for y in range(height):
        pixels.extend(raw[y * stride + 1:(y + 1) * stride])
    if not allow_flat:
        assert max(pixels) > min(pixels), f"all pixels appear flat: {path}"
    sha = hashlib.sha256(payload).hexdigest()
    print(f"PASS {path}: {width}x{height}, RGB8, full PNG CRC/zlib, pixel range "
          f"{min(pixels)}..{max(pixels)}, sha256={sha}")
    return sha

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("images", nargs="+", type=Path)
    cli.add_argument("--width", type=int, default=480)
    cli.add_argument("--height", type=int, default=270)
    cli.add_argument("--allow-flat", action="store_true", help="Accept intentionally dark frames")
    args = cli.parse_args()
    for image in args.images:
        inspect(image, args.width, args.height, allow_flat=args.allow_flat)
