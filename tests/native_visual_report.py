#!/usr/bin/env python3
"""Analyze native C++ RGB8 PNGs. Never creates or substitutes render pixels.

Quantitative flags are diagnostic, NOT cinematic-quality approvals.
"""
import hashlib
import html
import json
import struct
import sys
import zlib
from pathlib import Path

def decode_png(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not PNG: {path}")
    offset, compressed, dims = 8, bytearray(), None
    while offset + 12 <= len(data):
        n = struct.unpack(">I", data[offset:offset+4])[0]
        kind = data[offset+4:offset+8]
        chunk = data[offset+8:offset+8+n]
        assert offset+12+n <= len(data), f"PNG truncated: {path}"
        crc, = struct.unpack(">I", data[offset+8+n:offset+12+n])
        assert zlib.crc32(kind+chunk) == crc, f"Bad CRC: {path}"
        if kind == b"IHDR":
            w, h, depth, color, *_ = struct.unpack(">IIBBBBB",chunk)
            assert (depth,color) == (8,2), f"Expected RGB8: {path}"
            dims = (w,h)
        if kind == b"IDAT":
            compressed.extend(chunk)
        offset += 12+n
        if kind == b"IEND": break
    assert dims is not None
    w,h = dims
    raw = zlib.decompress(compressed)
    rowlen = 1+w*3
    assert len(raw) == rowlen*h
    pixels=bytearray()
    for y in range(h):
        row=raw[y*rowlen:(y+1)*rowlen]
        assert row[0] == 0, f"Unknown PNG filter at {path}"
        pixels.extend(row[1:])
    return (w,h),pixels,hashlib.sha256(data).hexdigest()

def measure(pixels):
    # gamma-encoded SDR approximate Rec.709 luma: diagnostic only.
    n=len(pixels)//3
    hist=[0]*256
    for i in range(0,len(pixels),3):
        l=int(round(.2126*pixels[i]+.7152*pixels[i+1]+.0722*pixels[i+2]))
        hist[l]+=1
    def quantile(p):
        cutoff=n*p
        total=0
        for i,v in enumerate(hist):
            total+=v
            if total>=cutoff:return round(i/255,4)
        return 1.0
    return {
        "mean_sdr_luma":round(sum(i*v for i,v in enumerate(hist))/(255*n),5),
        "near_black_fraction":round(sum(hist[:11])/n,5),
        "near_white_fraction":round(sum(hist[245:])/n,5),
        "p05":quantile(.05),"p50":quantile(.5),"p95":quantile(.95)
    }

def main():
    root=Path(sys.argv[1])
    start=float(sys.argv[2]) if len(sys.argv)>2 else 18.0
    rate=float(sys.argv[3]) if len(sys.argv)>3 else 10.0
    assert rate>0 and 0 <= start < 300
    frames=sorted(root.glob("frame_*.png"))
    assert len(frames)==41, f"Need 41 frames, got {len(frames)}"
    report=[]
    previous=None
    for i,p in enumerate(frames):
        assert p.name == f"frame_{i:04d}.png"
        dims,pixels,sha=decode_png(p)
        assert dims==(480,270),f"Unexpected size: {p}"
        m=measure(pixels)
        delta=None if previous is None else sum(abs(a-b) for a,b in zip(pixels,previous)) / (255*len(pixels))
        m.update(time_seconds=round(start+i/rate,3),png=p.name,sha256=sha,
                 mean_absolute_frame_delta=None if delta is None else round(delta,6))
        report.append(m)
        previous=pixels
    moving=sum(row["mean_absolute_frame_delta"]>0 for row in report[1:])
    assert moving>0,"All native motion frames are identical"
    result={"renderer":"C++/OpenGL native pixels, Python analysis only",
            "fps_motion_review":rate,"times_seconds":[start,start+40/rate],
            "resolution":[480,270],"frames":41,
            "source":"GitHub workflow provenance in output/native/provenance.txt",
            "visual_approval":False,"sampled_frames":report,
            "caveat":"Mean SDR luma and frame deltas cannot judge depth or cinematic quality."}
    out=Path("output/native")
    out.mkdir(parents=True,exist_ok=True)
    (out/"motion_metrics.json").write_text(json.dumps(result,indent=2))
    rows="\n".join(
        f"<tr><td>{r['time_seconds']:.1f}</td><td>{r['mean_sdr_luma']:.5f}</td>"
        f"<td>{r['near_black_fraction']:.3f}</td>"
        f"<td>{r['p95']:.3f}</td>"
        f"<td>{r['mean_absolute_frame_delta']}</td></tr>" for r in report)
    page=f"""<!doctype html><html><head><meta charset="utf-8"><title>Native M1.2 motion audit</title>
    <style>body{{background:#111722;color:#e9edf4;font:15px system-ui;padding:24px}}
    table{{border-collapse:collapse}}td,th{{border-bottom:1px solid #445;padding:5px 12px}}
    a{{color:#9dd}}img{{max-width:100%}}</style></head><body>
    <h1>Native C++ inflation motion diagnostic</h1>
    <p>41 frames from {start:g}–{start+40/rate:g} seconds at {rate:g} fps; 480×270. Not a full-rate motion test.</p>
    <p><strong>CI passed is not artistic approval.</strong> Review the actual MP4 and image.</p>
    <img src="contact_motion.png" alt="Nine sampled C++ frames">
    <table><tr><th>Time</th><th>Mean luma</th><th>Near black</th><th>P95</th><th>Frame delta</th></tr>{rows}</table></body></html>"""
    (out/"visual_review.html").write_text(page)
    print("PASS: 41 native C++ frames, valid PNGs, nonidentical temporal samples.")
    print(f"Mean luma: {min(x['mean_sdr_luma'] for x in report):.4f}.."
          f"{max(x['mean_sdr_luma'] for x in report):.4f}")
    print("Cinematic visual approval: NOT AUTOMATED")

if __name__=="__main__":
    main()
