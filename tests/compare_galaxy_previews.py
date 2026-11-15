#!/usr/bin/env python3
"""Analyze real native GLSL PNGs, never synthesize or recolor frames."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def rgb(path):
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
         "-i", str(path), "-frames:v", "1", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=20)
    data = result.stdout
    assert len(data) == 640 * 360 * 3, f"Invalid RGB frame: {path}"
    return data


def metrics(raw):
    luma = []
    bright = 0
    black = 0
    for i in range(0,len(raw),3):
        r,g,b=(raw[i]/255,raw[i+1]/255,raw[i+2]/255)
        y=0.2126*r+0.7152*g+0.0722*b
        luma.append(y)
        bright+=y>0.28
        black+=y<0.012
    luma.sort()
    n=len(luma)
    return {
        "mean_luma":round(sum(luma)/n,6),
        "p95_luma":round(luma[int(n*.95)],6),
        "p99_luma":round(luma[int(n*.99)],6),
        "fraction_above_0_28":round(bright/n,6),
        "fraction_below_0_012":round(black/n,6),
    }


def main(root):
    rows=[]
    for t in [18,20,22,240,250,260,270,290]:
        a=root/"baseline"/f"t{t}.png"
        b=root/"candidate"/f"t{t}.png"
        original=rgb(a)
        candidate=rgb(b)
        delta=sum(abs(x-y) for x,y in zip(original,candidate))/(len(original)*255)
        rows.append({"time":t,"identical":original==candidate,
                     "mean_abs_rgb_delta":round(delta,7),
                     "base":metrics(original),
                     "candidate":metrics(candidate),
                     "baseline_sha256":hashlib.sha256(a.read_bytes()).hexdigest(),
                     "candidate_sha256":hashlib.sha256(b.read_bytes()).hexdigest()})
    protected=[r for r in rows if r["time"]<=22]
    assert all(x["identical"] for x in protected), (
        "18/20/22s source regression: the liked opening has changed")
    late=[r for r in rows if r["time"]>=270]
    assert any(x["mean_abs_rgb_delta"]>0.0005 for x in late), (
        "Visual design iteration did not visibly change late galaxies")
    assert all(x["candidate"]["fraction_above_0_28"]<0.70 for x in rows), (
        "Too many high-luminance pixels; inspect white-out")
    motion=sorted((root/"motion").glob("frame_*.png"))
    assert len(motion)==21, "Expected 21 independently rendered native frames"
    first=rgb(motion[0]); last=rgb(motion[-1])
    interdelta=sum(abs(x-y) for x,y in zip(first,last))/(len(first)*255)
    assert interdelta>0.00001, "Motion appears static"
    result={"renderer":"Native C++17/OpenGL 3.3/GLSL",
            "baseline_commit":"83f2c6850158eb20622ce3965deaa247adc2bb06",
            "protected_opening_same_environment":True,
            "late_motion_first_last_delta":round(interdelta,8),
            "samples":rows,
            "visual_approval":"PENDING MANUAL REVIEW; diagnostics cannot judge cinematography"}
    (root/"measurements.json").write_text(json.dumps(result,indent=2)+"\n")
    for s in rows:
        print(f"t={s['time']:3d}s | absolute difference {s['mean_abs_rgb_delta']:.5f}"
              f" | mean luma {s['base']['mean_luma']:.4f}"
              f" -> {s['candidate']['mean_luma']:.4f}"
              f" | identical={s['identical']}")
    print("PASS: early scene protected, late visual change and non-static native clip")
    return 0


if __name__=="__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("output/galaxy_review")))
