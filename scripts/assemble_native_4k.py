#!/usr/bin/env python3
"""Audit recoverable UHD parts; assemble only exact, verified 1..9000 coverage.

The renderer checkout and executable must be the immutable versions that made
these parts. --audit-only permits pilot subsets but never creates a full film.
The original render_film validation is reused, without changing its identity or
resume rules. Full audiovisual screening remains a separate acceptance step.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import wave
import zipfile

TOTAL = 9000
PART_FRAMES = 90
STILLS = [0,3,6,11,18,25,38,48,50,60,82,95,115,135,149,170,184,196,212,235,250,258,267,285,296]
EDITS = [18,20,50,82,116,149,176,196,220,240,260,280,292]


def command(args, timeout=1800, capture=False):
    result = subprocess.run(list(map(str,args)), check=True, timeout=timeout,
        stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None)
    return result.stdout


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.partial')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    os.replace(temporary, path)


def audit_parts(incoming, native, source_sha, *, require_full=True):
    sys.path.insert(0, str(native/'scripts'))
    import render_film as rf
    manifests = sorted(incoming.rglob('manifest.json'))
    require(bool(manifests), 'No native part manifests found')
    found = {}
    for path in manifests:
        m = rf.read_json(path)
        first = m['identity']['first_frame']
        require(type(first) is int and first in range(1,TOTAL+1,PART_FRAMES), 'Misaligned part range')
        require(first not in found, f'Duplicate part starting at {first}')
        found[first] = (path.parent, m)
    expected = set(range(1,TOTAL+1,PART_FRAMES))
    if require_full:
        require(set(found) == expected, f'Incomplete 9000-frame coverage; missing {sorted(expected-set(found))}; unexpected {sorted(set(found)-expected)}')
    source = rf.source_fingerprint(native)
    require(source['git_head'] == source_sha, 'Renderer checkout does not match requested immutable commit')
    binary_hash = rf.file_sha256(native/'build/bigbang')
    canonical = None
    parts = []
    for first,(folder,m) in sorted(found.items()):
        identity = m['identity']
        require(m['source']['git_head'] == source_sha, f'Wrong source commit at frame {first}')
        require(m['source']['sha256'] == source['sha256'] == identity['source_sha256'], 'Source fingerprint mismatch')
        require(identity['binary_sha256'] == binary_hash, 'Native executable checksum mismatch')
        contract = (identity['width'],identity['height'],identity['fps'],identity['first_frame'],identity['end_frame'],identity['chunk_frames'])
        require(contract == (3840,2160,30,first,first+89,30), f'Wrong native contract: {contract}')
        require(identity['encoder'] == {'codec':'libx264','crf':16,'preset':'fast','pixel_format':'yuv420p'}, 'Unexpected encoding settings')
        common = {k:v for k,v in identity.items() if k not in ('first_frame','end_frame')}
        if canonical is None:
            canonical = common
        require(common == canonical, 'Mixed binary, driver, environment, or codec identity')
        s = rf.read_json(folder/'checkpoint.json')
        require(s['identity'] == identity and s['status'] == 'complete', f'Incomplete checkpoint at {first}')
        chunks = list(rf.frame_chunks(first,first+90,30))
        require(set(s['chunks']) == {c.name for c in chunks}, 'Missing or unexpected checkpoint chunks')
        for chunk in chunks:
            saved = s['chunks'][chunk.name]
            require((saved['first_frame'],saved['end_frame'],saved['frames']) == (chunk.first,chunk.stop-1,30), 'Chunk chronology mismatch')
            path = folder/'chunks'/chunk.name
            require(rf.file_sha256(path) == saved['sha256'], f'Transport corruption: {path}')
            rf.probe_video(path,width=3840,height=2160,fps=30,frames=30,ffprobe='ffprobe',ffmpeg='ffmpeg')
        film = folder/'film.mp4'
        require(rf.file_sha256(film) == s['final']['sha256'], 'Part movie checksum mismatch')
        result = rf.probe_video(film,width=3840,height=2160,fps=30,frames=90,ffprobe='ffprobe',ffmpeg='ffmpeg')
        parts.append({'first_frame':first,'end_frame':first+89,'file':str(film.resolve()),
            'sha256':result['sha256'],'frames':90,'native_size':[3840,2160],
            'render_encode_seconds':sum(c['render_and_encode_wall_seconds'] for c in s['chunks'].values())})
        print(f'Verified native UHD frames {first}..{first+89}', flush=True)
    return {'source_commit':source_sha,'source_sha256':source['sha256'],'identity':canonical,
        'parts':parts,'verified_frames':len(parts)*90,'coverage_complete':set(found)==expected,
        'full_film_accepted':False}


def verify_av(path, size):
    raw = json.loads(command(['ffprobe','-v','error','-count_frames','-show_entries',
        'stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,channels,sample_rate,start_time,duration:format=duration',
        '-of','json',path],capture=True))
    streams = raw['streams']
    v = [s for s in streams if s['codec_type']=='video']
    a = [s for s in streams if s['codec_type']=='audio']
    require(len(streams)==2 and len(v)==len(a)==1, 'Expected one video and one audio stream')
    v,a = v[0],a[0]
    require((v['codec_name'],v['width'],v['height'],int(v['nb_read_frames']),Fraction(v['avg_frame_rate'])) == ('h264',*size,9000,Fraction(30)), 'Picture format or decoded frame count mismatch')
    require((a['codec_name'],a['channels'],int(a['sample_rate'])) == ('aac',2,48000), 'Sound is not stereo 48 kHz AAC')
    require(abs(float(v['start_time']))<.001 and abs(float(a['start_time']))<.001, 'A/V start offset')
    require(abs(float(v['duration'])-300)<.003 and abs(float(a['duration'])-300)<.025, 'A/V duration mismatch')
    require(abs(float(raw['format']['duration'])-300)<.025, 'Container duration mismatch')
    command(['ffmpeg','-nostdin','-v','error','-xerror','-i',path,'-map','0:v:0','-map','0:a:0','-f','null','-'])
    return raw


def essence_hash(path):
    return command(['ffmpeg','-nostdin','-v','error','-i',path,'-map','0:v:0',
        '-c:v','copy','-f','hash','-hash','sha256','-'],capture=True).decode().strip()


def create_review_assets(master, out):
    import numpy as np
    images = out/'storyboard-frames'
    images.mkdir(exist_ok=True)
    for i,t in enumerate(STILLS):
        command(['ffmpeg','-nostdin','-v','error','-y','-ss',t,'-i',master,
            '-vf','scale=480:270:flags=lanczos','-frames:v','1',images/f'{i:02d}.png'],timeout=120)
    command(['ffmpeg','-nostdin','-v','error','-y','-framerate','1','-i',images/'%02d.png',
        '-vf','tile=5x5:margin=8:padding=6:color=black','-frames:v','1',out/'Storyboard.jpg'])
    (out/'Storyboard.md').write_text('# Big Bang storyboard\n\nImages follow row-major order in Storyboard.jpg. Each image is extracted from the assembled UHD movie and reduced only for the storyboard.\n\n'+
        '| Panel | Global seconds |\n|---|---|\n'+''.join(f'| {i+1} | {t} |\n' for i,t in enumerate(STILLS)))
    proof = out/'native-4k-stills'
    proof.mkdir(exist_ok=True)
    for t in (6,30,50,82,149,196,250,292):
        command(['ffmpeg','-nostdin','-v','error','-y','-ss',t,'-i',master,'-frames:v','1',proof/f'{t:03d}s.png'],timeout=120)
    def rgb(t):
        data = command(['ffmpeg','-nostdin','-v','error','-ss',f'{t:.8f}','-i',master,
            '-vf','scale=320:180','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'],capture=True,timeout=120)
        require(len(data)==320*180*3, 'Invalid transition audit sample')
        return np.frombuffer(data,dtype=np.uint8).reshape(180,320,3).astype(float)/255
    audit = []
    for t in EDITS:
        before,after = rgb(t-1/30),rgb(t)
        jump = float(np.mean(np.abs(after-before)))
        luma = .2126*after[:,:,0]+.7152*after[:,:,1]+.0722*after[:,:,2]
        audit.append({'seconds':t,'mean_absolute_rgb_jump':jump,'after_mean_luma':float(luma.mean()),
            'after_near_white_fraction':float((luma>.95).mean()),'after_near_black_fraction':float((luma<.02).mean()),
            'flag_manual_review':jump>.25,'subjective_review':'pending'})
    return audit


def assemble(opts):
    out = opts.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    report = audit_parts(opts.incoming,opts.native_root.resolve(),opts.source_sha,require_full=not opts.audit_only)
    write_json(out/'Native_Part_Audit.json',report)
    if opts.audit_only:
        print('Pilot audit only; no complete movie or release acceptance.', flush=True)
        return
    sys.path.insert(0,str(opts.native_root.resolve()/'scripts'))
    import render_film as rf
    playlist = out/'verified-parts.txt'
    require(all("'" not in p['file'] and '\n' not in p['file'] for p in report['parts']), 'Unsafe concat path')
    playlist.write_text(''.join("file '"+p['file']+"'\n" for p in report['parts']))
    silent = out/'picture-4k-silent.mp4'
    command(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',playlist,'-an','-c:v','copy','-movflags','+faststart',silent])
    rf.probe_video(silent,width=3840,height=2160,fps=30,frames=9000,ffprobe='ffprobe',ffmpeg='ffmpeg')
    score = out/'Original_Stereo_Score_32kHz.wav'
    score_script = opts.native_root.resolve()/'scripts/create_original_score.py'
    command([sys.executable,score_script,'--seconds','300','--output',score],timeout=300)
    with wave.open(str(score),'rb') as w:
        require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(2,2,32000,9600000), 'Original score PCM contract mismatch')
    master = out/'BigBang_300s_NATIVE_4K30_Stereo.mp4'
    command(['ffmpeg','-nostdin','-v','error','-y','-i',silent,'-i',score,'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','300','-movflags','+faststart',master])
    master_probe = verify_av(master,(3840,2160))
    require(essence_hash(silent)==essence_hash(master), 'Mux changed encoded native picture essence')
    videos = [{'file':master.name,'sha256':rf.file_sha256(master),'probe':master_probe,'native':True}]
    for name,size,crf,bitrate in [('BigBang_300s_1080p30_Stereo.mp4',(1920,1080),18,'192k'),('BigBang_300s_Easy_Play_360p30_Stereo.mp4',(640,360),27,'96k')]:
        path = out/name
        command(['ffmpeg','-nostdin','-v','error','-y','-i',master,'-vf',f'scale={size[0]}:{size[1]}:flags=lanczos',
            '-c:v','libx264','-preset','fast','-crf',crf,'-pix_fmt','yuv420p','-c:a','aac','-b:a',bitrate,'-ar','48000','-ac','2','-movflags','+faststart',path],timeout=3600)
        videos.append({'file':name,'sha256':rf.file_sha256(path),'probe':verify_av(path,size),'native':False,'derived_from_native_4k':True})
    report.update({'technical_validation_passed':True,'videos':videos,'soundtrack_sha256':rf.file_sha256(score),
        'soundtrack_source_sha256':rf.file_sha256(score_script),'transitions':create_review_assets(master,out),
        'visual_transition_review':'pending','complete_viewing_and_listening':'pending','full_film_accepted':False,
        'release_download_verification':'pending','native_picture_essence_preserved_during_mux':True})
    write_json(out/'Validation_Report.json',report)
    evidence = out/'documentation'
    shutil.copytree(opts.native_root.resolve()/'docs',evidence,dirs_exist_ok=True)
    (out/'Technical_Report.md').write_text('# Big Bang native UHD technical report\n\n'
        'Technical assembly checks passed. Full audiovisual screening, transition approval, presentation export, and release download verification remain pending; this is not final submission acceptance.\n\n'
        f'Renderer commit: {opts.source_sha}\n\n'
        'C++17 / OpenGL / GLSL natively rendered 9,000 frames at 3840x2160, 30 FPS, with frame N sampling (N-1)/30 seconds. The 300-second picture was stream-copied from 100 independently validated 90-frame parts. Every 30-frame checkpoint and every part was rehashed and strictly decoded after transport. Binary, source, driver, environment and codec identities were checked across all parts. The stereo score is regenerated using the unchanged original source and seed, retained as 32 kHz PCM, and encoded as 48 kHz stereo AAC. The encoded native picture essence was unchanged by audio muxing. The 1080p and 360p editions are derivatives of the UHD master.\n\n'
        'See Validation_Report.json for measured media metadata, per-part times and transition screening flags. See documentation/RENDERING_PIPELINE.md for the nine conceptual stages and explicit optional-stage limits. The film is an educational artistic compression, not a calibrated cosmological simulation.\n')
    (out/'README_EXTRACT_AND_WATCH.txt').write_text('BIG BANG NATIVE UHD TECHNICAL SCREENING PACKAGE\n'
        'Extract the ZIP, then open BigBang_300s_NATIVE_4K30_Stereo.mp4. All 9,000 master frames are native UHD.\n'
        'The 1080p and easy-play 360p editions come from this master. Original stereo music is included.\n'
        'Validation_Report.json records exact geometry, frame counts, durations, decode results and provenance.\n'
        'Visual approval, full viewing/listening, presentation export and release download checks are pending.\n')
    hashes = {str(p.relative_to(out)):rf.file_sha256(p) for p in sorted(out.rglob('*')) if p.is_file() and p.suffix!='.zip' and p.name!='SHA256SUMS.txt'}
    (out/'SHA256SUMS.txt').write_text(''.join(f'{h}  {n}\n' for n,h in hashes.items()))
    for label,names in [('Native_4K',[master.name,'Original_Stereo_Score_32kHz.wav','Validation_Report.json','README_EXTRACT_AND_WATCH.txt']),
        ('1080p',['BigBang_300s_1080p30_Stereo.mp4','Validation_Report.json','README_EXTRACT_AND_WATCH.txt']),
        ('Easy_Play',['BigBang_300s_Easy_Play_360p30_Stereo.mp4','README_EXTRACT_AND_WATCH.txt']),
        ('Evidence',[n for n in hashes if not n.endswith(('.mp4','.wav'))])]:
        archive = out/f'BigBang_{label}.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
            for name in names:
                z.write(out/name,'BigBang/'+name)
            z.writestr('BigBang/SHA256SUMS.txt',''.join(f'{hashes[n]}  {n}\n' for n in names))
        with zipfile.ZipFile(archive) as z:
            require(z.testzip() is None,'Archive CRC failed')
    print('PASS: 9000 native UHD frames, 300 seconds, stereo, derivatives and archives; final audiovisual acceptance pending.',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--incoming',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--native-root',type=Path,required=True)
    parser.add_argument('--source-sha',required=True)
    parser.add_argument('--audit-only',action='store_true')
    assemble(parser.parse_args())


if __name__=='__main__':
    main()
