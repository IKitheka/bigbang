#!/usr/bin/env python3
"""Reassemble a source-proven 300-second native C++ V10 screening master.

Read twelve independently rendered H264 segment artifacts produced by native
OpenGL, enforce source SHA/range/codec/decoded-count, mix the exact original
300-second stereo score, then publish a single checked review MP4 + storyboard.
Can run locally from the downloaded CI segment ZIPs (recursive input layout).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SIZES=[600,900,960,1020,990,810,600,600,600,600,600,600]
BOUNDARIES=[20,50,82,116,149,176,196,216,240,260,280]
STILLS=[0,3,7,12,18,26,40,50,65,81,90,115,132,149,170,185,196,215,235,245,257,263,277,297]

def cmd(*args,timeout=1200,capture=False):
    proc=subprocess.run([str(a) for a in args],check=True,timeout=timeout,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None)
    return proc.stdout if capture else None

def probe(path,count=False):
    args=["ffprobe","-v","error"]
    if count: args+=["-count_frames"]
    args+=["-show_entries","stream=codec_type,codec_name,width,height,channels,avg_frame_rate,nb_read_frames:format=duration",
           "-of","json",str(path)]
    return json.loads(cmd(*args,timeout=450,capture=True))

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()

def only(root,pattern):
    matches=list(root.rglob(pattern))
    if len(matches)!=1: raise ValueError(f"Expected one {pattern} under {root}, found {len(matches)}: {matches[:4]}")
    return matches[0]

def video_info(p):
    data=probe(p,count=True)
    vs=[s for s in data["streams"] if s["codec_type"]=="video"]
    if len(vs)!=1: raise ValueError(f"Expected one video stream in {p}")
    return data,vs[0]

def single_rgb(mp4,t):
    w,h=480,270
    data=cmd("ffmpeg","-v","error","-ss",f"{t:.5f}","-i",mp4,
             "-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","pipe:1",
             timeout=90,capture=True)
    if len(data)!=w*h*3:raise ValueError(f"Missing frame at {t}: {len(data)} bytes")
    import numpy as np
    return np.frombuffer(data,dtype=np.uint8).reshape(h,w,3).astype(np.float32)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--incoming",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--expected-sha",required=True)
    opts=ap.parse_args()
    opts.out.mkdir(parents=True,exist_ok=True)
    records=[]
    concat=[]
    source_ranges=[]
    first=1
    for i,expected in enumerate(SIZES,1):
        movie=only(opts.incoming,f"part_{i:02d}.mp4")
        sha_path=only(opts.incoming,f"commit_{i:02d}.txt")
        commit=sha_path.read_text().strip()
        if commit!=opts.expected_sha:raise ValueError(f"Source mismatch in segment {i}: {commit}")
        data,v=video_info(movie)
        if (v["codec_name"],v["width"],v["height"],v["avg_frame_rate"],int(v["nb_read_frames"]))!=(
            "h264",480,270,"30/1",expected):
            raise ValueError(f"Unexpected frames/geometry for part {i}: {data}")
        cmd("ffmpeg","-v","error","-xerror","-nostdin","-i",movie,"-f","null","-",timeout=300)
        stop=first+expected-1
        records.append({"part":i,"first_frame":first,"last_frame":stop,"frames":expected,
                        "native_resolution":[480,270],"sha256":sha(movie),"relative_path":str(movie)})
        source_ranges.append([first,stop])
        first=stop+1
        path=str(movie.resolve())
        if "'" in path or "\n" in path:raise ValueError("Unsafe concat path")
        concat.append(f"file '{path}'\n")
    if first!=9001 or sum(SIZES)!=9000:raise ValueError("Missing full native timeline")
    playlist=opts.out/"segment_list.txt"
    playlist.write_text("".join(concat),encoding="utf8")
    master_video=opts.out/"all_native_video_silent.mp4"
    cmd("ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
        "-f","concat","-safe","0","-i",playlist,
        "-c:v","copy","-an","-movflags","+faststart",master_video,timeout=500)
    try:
        _,v=video_info(master_video)
        if int(v["nb_read_frames"])!=9000:raise ValueError("Joined clip's frames differ from 9000")
    except Exception:
        # Rare H264 stream-parameter changes across independently encoded
        # intervals are made safe with a single 480x270 CFR reencode.
        cmd("ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
            "-f","concat","-safe","0","-i",playlist,
            "-c:v","libx264","-preset","veryfast","-crf","18",
            "-r","30","-pix_fmt","yuv420p","-an",
            "-movflags","+faststart",master_video,timeout=1100)
    out=opts.out/"BigBang_V10_Integrated_5min_Native_480p30_With_Sound.mp4"
    score=opts.out/"original_score.wav"
    cmd(sys.executable,"scripts/create_original_score.py","--seconds","300","--output",score,timeout=300)
    cmd("ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
        "-i",master_video,"-i",score,"-map","0:v:0","-map","1:a:0",
        "-c:v","copy","-c:a","aac","-b:a","160k","-ar","48000","-ac","2",
        "-t","300","-movflags","+faststart",out,timeout=450)
    data,v=video_info(out)
    aud=[s for s in data["streams"] if s["codec_type"]=="audio"]
    assert len(aud)==1 and aud[0]["codec_name"]=="aac" and aud[0]["channels"]==2,aud
    assert (v["width"],v["height"],v["avg_frame_rate"],int(v["nb_read_frames"]))==(
        480,270,"30/1",9000),v
    assert abs(float(data["format"]["duration"])-300)<0.12,data
    cmd("ffmpeg","-v","error","-xerror","-nostdin","-i",out,"-f","null","-",timeout=900)
    stilldir=opts.out/"stills"
    stilldir.mkdir(exist_ok=True)
    for j,t in enumerate(STILLS):
        cmd("ffmpeg","-v","error","-nostdin","-y","-ss",str(t),"-i",out,
            "-frames:v","1",stilldir/f"frame_{j:02d}.png",timeout=70)
    storyboard=opts.out/"V10_24_Frame_Storyboard.jpg"
    cmd("ffmpeg","-v","error","-nostdin","-y","-framerate","1",
        "-i",stilldir/"frame_%02d.png","-vf",
        "tile=4x6:margin=5:padding=5:color=black",
        "-frames:v","1",storyboard,timeout=80)
    import numpy as np
    joins=[]
    # This is a diagnostic, not a ban on intentional chapter edits.
    for t in BOUNDARIES:
        before=single_rgb(out,max(0,t-1/30))
        after=single_rgb(out,t)
        jump=float(np.mean(np.abs(after-before))/255.0)
        luma=float(np.mean(.2126*after[:,:,0]+.7152*after[:,:,1]+.0722*after[:,:,2])/255.)
        joins.append({"second":t,"mean_frame_jump":round(jump,5),
                      "sdr_luma_after":round(luma,5),
                      "needs_art_review":jump>0.27})
    report={"source_git_sha":opts.expected_sha,"native_source":"C++17 OpenGL GLSL",
            "master":{"duration_seconds":300,"frames":9000,"fps":30,"resolution":[480,270],
                      "codec":"H264","audio":"original deterministic stereo AAC","full_decode_verified":True,
                      "sha256":sha(out)},"segments":records,"chapter_joins":joins,
            "protected_solar_system":"260-300s native V9 shader unchanged",
            "status":"screening cut; not final 1080p production master",
            "visual_discussion":"Frame-jump numbers flag likely cuts only; human review required."}
    (opts.out/"V10_Validation_and_Transition_Audit.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf8")
    (opts.out/"README_WATCH.txt").write_text(
        "Big Bang V10: FULL 300-second native C++ screening cut.\n"
        "This ZIP includes H264 480x270/30fps five-minute film and ORIGINAL stereo AAC soundtrack.\n"
        "For Ubuntu: extract ZIP; open BigBang_V10_Integrated_5min_Native_480p30_With_Sound.mp4 in VLC.\n"
        "Review: 24-frame storyboard; validation/transition report.\n"
        "This screening cut is intentionally low resolution. Approved solar-system finale is unchanged.\n"
        "Do NOT call this the final native-1080p release.\n",encoding="utf8")
    print("PASS: 9000 native C++ frames / 300 seconds / 30 FPS / original stereo score")
    print("Transition diagnostics:",joins)
    print("Master:",out,flush=True)
if __name__=="__main__":main()
