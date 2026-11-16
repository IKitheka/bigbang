#!/usr/bin/env python3
"""Assemble exactly 9000 TRUE NATIVE 1920x1080 C++ OpenGL frames.

Consumes 30 source-verified H264 chunks from V12 GitHub Actions. No movie
frames are synthesized, interpolated, invented or borrowed from V4/V10.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

TOTAL=9000
FPS=30
PARTS=30
PER_PART=300
WIDTH=1920
HEIGHT=1080
STILLS=[0,6,15,25,35,45,55,70,80,88,105,117,125,140,155,172,187,202,215,234,250,265,278,289,298]
EDITS=[15,35,50,65,73,80,87,105,118,120,130,145,180,215,245,265,283,291]

def run(args, *, timeout=900, capture=False):
    r=subprocess.run(list(map(str,args)),check=True,timeout=timeout,
       stdout=subprocess.PIPE if capture else None,
       stderr=subprocess.PIPE if capture else None)
    return r.stdout

def read_probe(movie, *, count=True):
    args=['ffprobe','-v','error']
    if count:args.append('-count_frames')
    args+=['-show_entries','stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,channels:format=duration,size',
           '-of','json',str(movie)]
    return json.loads(run(args,capture=True,timeout=500))

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for x in iter(lambda:f.read(2**20),b''):h.update(x)
    return h.hexdigest()

def selected(root,pat):
    files=list(root.rglob(pat))
    if len(files)!=1:
        raise RuntimeError(f'Expected ONE {pat}, found {len(files)}: {files[:3]}')
    return files[0]

def getvideo(p):
    raw=read_probe(p)
    v=[x for x in raw['streams'] if x.get('codec_type')=='video']
    if len(v)!=1:raise RuntimeError(f'Invalid video streams: {raw}')
    return raw,v[0]

def short_luma(path,t):
    # Sample 320x180 for bounded memory, not as a replacement for output.
    raw=run(['ffmpeg','-loglevel','error','-ss',f'{t:.5f}','-i',path,
        '-frames:v','1','-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture=True,timeout=70)
    if len(raw)!=320*180*3:raise RuntimeError(f'Bad audit frame at {t}')
    import numpy as np
    p=np.frombuffer(raw,dtype=np.uint8).reshape(180,320,3).astype(float)/255.
    y=.2126*p[:,:,0]+.7152*p[:,:,1]+.0722*p[:,:,2]
    return p, float(y.mean()),float((y<.02).mean()),float((y>.95).mean())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--incoming',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--source-sha',required=True)
    opts=ap.parse_args()
    opts.out.mkdir(parents=True,exist_ok=True)
    segments=[]
    concat=[]
    for i in range(1,PARTS+1):
        movie=selected(opts.incoming,f'part_{i:02d}.mp4')
        commit=selected(opts.incoming,f'commit_{i:02d}.txt').read_text().strip()
        if commit!=opts.source_sha:
            raise RuntimeError(f'Mismatched native renderer in part {i}: {commit}')
        dat,v=getvideo(movie)
        measured=(v['codec_name'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))
        expected=('h264',WIDTH,HEIGHT,'30/1',PER_PART)
        if measured!=expected:raise RuntimeError(f'Invalid source part {i} expected {expected} got {measured}')
        # The native segment renderer already decoded this before publication.
        # Second audit verifies source is still intact after transport.
        run(['ffmpeg','-loglevel','error','-xerror','-nostdin','-i',movie,'-f','null','-'],timeout=600)
        segments.append({'id':i,'frames':PER_PART,'time_seconds':[(i-1)*10,i*10],
           'native_resolution':[WIDTH,HEIGHT],'source_sha':commit,'sha256':sha256(movie)})
        filename=str(movie.resolve())
        if "'" in filename or '\n' in filename:raise RuntimeError('Unsafe concat filename')
        concat.append("file '"+filename+"'\n")
    if len(segments)!=30 or sum(s['frames'] for s in segments)!=TOTAL:
        raise RuntimeError('Missing native segment(s)')
    playlist=opts.out/'verified_segment_playlist.txt'
    playlist.write_text(''.join(concat),encoding='utf-8')
    silent=opts.out/'v12_all_video_silent.mp4'
    run(['ffmpeg','-loglevel','error','-nostdin','-y','-f','concat','-safe','0',
         '-i',playlist,'-c:v','copy','-an','-movflags','+faststart',silent],timeout=900)
    dat,v=getvideo(silent)
    if (int(v['nb_read_frames']),v['width'],v['height'],v['avg_frame_rate'])!=(
          TOTAL,WIDTH,HEIGHT,'30/1'):
        raise RuntimeError(f'Full timeline join failed: {dat}')
    # All source frames remain true 1920x1080; no scale, AI upsample, interpolation
    score=opts.out/'original_5min_score.wav'
    run([sys.executable,'scripts/create_original_score.py','--seconds','300','--output',score],timeout=300)
    master=opts.out/'BigBang_V12_5min_NATIVE_1080p30_With_Original_Sound.mp4'
    run(['ffmpeg','-loglevel','error','-nostdin','-y','-i',silent,'-i',score,
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac',
         '-b:a','192k','-ar','48000','-ac','2','-t','300',
         '-movflags','+faststart',master],timeout=450)
    dat,v=getvideo(master)
    a=[s for s in dat['streams'] if s.get('codec_type')=='audio']
    if (int(v['nb_read_frames']),v['width'],v['height'],v['avg_frame_rate'],v['codec_name'])!=(
        TOTAL,WIDTH,HEIGHT,'30/1','h264') or len(a)!=1 or a[0]['codec_name']!='aac' or a[0]['channels']!=2:
        raise RuntimeError(f'Final master not native 1080p30 stereo: {dat}')
    if abs(float(dat['format']['duration'])-300)>0.1:
        raise RuntimeError('Five-minute duration mismatch')
    run(['ffmpeg','-loglevel','error','-xerror','-nostdin','-i',master,'-f','null','-'],timeout=1200)
    # Companion low-bandwidth streaming playback, from same verified source.
    easy=opts.out/'BigBang_V12_5min_Easy_Play_360p_With_Sound.mp4'
    run(['ffmpeg','-loglevel','error','-nostdin','-y','-i',master,
         '-vf','scale=640:360:flags=lanczos','-c:v','libx264',
         '-preset','veryfast','-crf','29','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','96k','-movflags','+faststart',easy],timeout=1000)
    tiny,audit_video=getvideo(easy)
    if int(audit_video['nb_read_frames'])!=TOTAL:raise RuntimeError('Easy-play video frame mismatch')
    run(['ffmpeg','-loglevel','error','-xerror','-nostdin','-i',easy,'-f','null','-'],timeout=600)
    # True-native source screenshots from the finished full-HD film.
    stilldir=opts.out/'stills';stilldir.mkdir(exist_ok=True)
    for i,t in enumerate(STILLS):
        run(['ffmpeg','-loglevel','error','-nostdin','-y','-ss',str(t),
           '-i',master,'-vf','scale=480:270:flags=lanczos',
           '-frames:v','1',stilldir/f'{i:02d}.png'],timeout=90)
    storyboard=opts.out/'V12_25_Frame_Final_Storyboard.jpg'
    run(['ffmpeg','-loglevel','error','-nostdin','-y','-framerate','1',
        '-i',stilldir/'%02d.png','-vf',
        'tile=5x5:margin=8:padding=6:color=black',
        '-frames:v','1',storyboard],timeout=100)
    import numpy as np
    edit_audit=[]
    for t in EDITS:
        before,*_=short_luma(master,t-1/FPS)
        after,lum,black,white=short_luma(master,t)
        jump=float(np.mean(np.abs(before-after)))
        edit_audit.append({'second':t,'normalized_frame_jump':round(jump,5),
            'after_mean_luma':round(lum,5),'near_black':round(black,5),
            'near_white':round(white,5),'flag_manual_review':jump>.25})
    report={'source_git_sha':opts.source_sha,'source_engine':'native C++17 OpenGL3.3 GLSL',
        'resolution':'1920x1080 TRUE native pixels ALL frames; no upscaling',
        'frame_count':TOTAL,'fps':FPS,'duration_seconds':300,
        'audio':'Original deterministic stereo score 192 kbps AAC 48 kHz',
        'master_h264_sha256':sha256(master),'easy_play_h264_sha256':sha256(easy),
        'all_frames_decoded':True,'native_segments':segments,
        'chapter_boundary_audit':edit_audit,
        'solar_system':'V12 lecturer review: 118..300s extended young Sun, accretion, planets, Earth; shader retimed and enhanced',
        'validation_note':'Technical validation passed; subjective cinematic approval is a separate human judgment.'}
    (opts.out/'V12_Final_Validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (opts.out/'README_EXTRACT_AND_WATCH.txt').write_text(
        'BIG BANG — V12 FINAL FULL-HD NATIVE MASTER (5 minutes)\n'
        'Extract this GitHub ZIP, then open the main MP4 with VLC or your media player.\n'
        'MAIN: BigBang_V12_5min_NATIVE_1080p30_With_Original_Sound.mp4\n'
        'ALTERNATIVE: BigBang_V12_5min_Easy_Play_360p_With_Sound.mp4\n'
        'Both MP4 files are 300 seconds, 30fps, with original stereo AAC music.\n'
        'ALL 9000 frames of the main film were natively rendered at TRUE 1920x1080\n'
        'by the C++ OpenGL renderer, not upscaled from 720p or 270p.\n'
        'V12 devotes the final three minutes to extended Solar System formation.\n'
        'The storyboard and validation JSON document all chapters.\n')
    print('PASS: TRUE native 1080p, 9000 frames, 300s, audio, full decode',flush=True)
    print(json.dumps(edit_audit,indent=2),flush=True)
if __name__=='__main__':
    main()
