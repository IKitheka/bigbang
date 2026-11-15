#!/usr/bin/env python3
"""Inspect genuine C++ PNG scene samples. No pixels are generated here.

SDR luma/contrast are diagnostic, not subjective cinematic approval.
"""
from pathlib import Path
import json
import re
import struct
import sys
import zlib

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path("output/scene_review")
W,H=480,270
def rgb_from_native_png(path):
    p=path.read_bytes()
    if not p.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not PNG: {path}")
    offset=8; packed=bytearray(); size=None
    while offset+12<=len(p):
        n=struct.unpack_from(">I",p,offset)[0]
        typ=p[offset+4:offset+8]
        chunk=p[offset+8:offset+8+n]
        if offset+12+n>len(p):
            raise ValueError(f"Truncated PNG: {path}")
        expect=struct.unpack_from(">I",p,offset+8+n)[0]
        if zlib.crc32(typ+chunk)!=expect:
            raise ValueError(f"PNG CRC mismatch: {path}")
        offset+=12+n
        if typ==b"IHDR":
            w,h,depth,color,*_=struct.unpack(">IIBBBBB",chunk)
            if (w,h,depth,color)!=(W,H,8,2):
                raise ValueError(f"Unexpected RGB PNG: {path}")
            size=(w,h)
        elif typ==b"IDAT":
            packed.extend(chunk)
        elif typ==b"IEND":
            break
    if size is None:
        raise ValueError(f"Missing PNG header: {path}")
    raw=zlib.decompress(packed)
    stride=W*3+1
    if len(raw)!=H*stride:
        raise ValueError(f"Unexpected uncompressed bytes: {path}")
    for y in range(H):
        if raw[y*stride]!=0:
            raise ValueError(f"Expected native PNG scanline filter 0: {path}")
    return b"".join(raw[y*stride+1:(y+1)*stride] for y in range(H))

def sample(path):
    raw=rgb_from_native_png(path)
    n=len(raw)//3
    mean=0.0; mean_sq=0.0; blacks=0; whites=0
    for k in range(0,len(raw),3):
        v=(0.2126*raw[k]+0.7152*raw[k+1]+0.0722*raw[k+2])/255.0
        mean+=v;mean_sq+=v*v
        blacks+=(v<0.02);whites+=(v>0.95)
    mean/=n
    contrast=max(0.,mean_sq/n-mean*mean)**0.5
    return {"mean_sdr_luma":round(mean,5),
            "sdr_luma_stddev":round(contrast,5),
            "near_black_fraction":round(blacks/n,5),
            "near_white_fraction":round(whites/n,5)}

def main():
    photos=sorted((ROOT/"stills").glob("scene_*.png"))
    assert len(photos)==32, f"Expected 32 native C++ stills; found {len(photos)}"
    clips=sorted((ROOT/"clips").glob("*.mp4"))
    assert len(clips)==8, f"Expected 8 native C++ clips; got {len(clips)}"
    records=[]
    for file in photos:
        match=re.fullmatch(r"scene_(\d\d)_(\d\d)_t(\d+)\.png",file.name)
        assert match,f"Unexpected native still filename: {file.name}"
        scene,position,second=map(int,match.groups())
        records.append({"chapter":scene,"sample_index":position,
                        "time_seconds":second,"image":file.name,
                        **sample(file)})
    for scene in range(8):
        assert sum(x["chapter"]==scene for x in records)==4
    summary={"source":"actual PNGs rendered by C++/OpenGL", "dimensions":[W,H],
             "scene_stills":32,"native_clips":8,
             "summary_by_scene":[],
             "all_samples":records,
             "limits":"Technical sampling only; subjective/physical review required."}
    for scene in range(8):
        group=[x for x in records if x["chapter"]==scene]
        summary["summary_by_scene"].append({
            "chapter":scene,
            "mean_luma":round(sum(x["mean_sdr_luma"] for x in group)/4,5),
            "mean_contrast":round(sum(x["sdr_luma_stddev"] for x in group)/4,5),
            "mean_near_black":round(sum(x["near_black_fraction"] for x in group)/4,5),
            "max_near_white":max(x["near_white_fraction"] for x in group)})
    (ROOT/"scene_metrics.json").write_text(json.dumps(summary,indent=2)+"\n")
    # Hard engineering gate only: guard against the near-total whiteout
    # caught during the first QGP design review. Film/art approval is human.
    plasma=[x for x in records if x["chapter"]==2 and
            x["time_seconds"] in (65,75,85)]
    assert len(plasma)==3
    for x in plasma:
        assert x["near_white_fraction"]<0.10 and x["mean_sdr_luma"]<0.76, (
            f"QGP preview overexposed at {x['time_seconds']}s: "
            f"mean={x['mean_sdr_luma']}, white={x['near_white_fraction']}")
    print(json.dumps(summary["summary_by_scene"],indent=2))
    print("PASS: 32 actual native C++ PNGs parsed and 8 preview clips present")

if __name__=="__main__":
    main()
