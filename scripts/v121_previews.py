#!/usr/bin/env python3
"""V12.1 native moving previews. Never renders or accepts a full film."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, shutil, subprocess, wave, zipfile
from fractions import Fraction
import numpy as np
import render_film as rf
P=pathlib.Path
ROOT=P(__file__).resolve().parents[1]
OUT=ROOT/'output/v121'
SHARED=ROOT/'output/v121_shared'
TRANSITIONS={'galaxy_cloud':112,'cloud_sun':136,'sun_disc':174,
             'disc_planetesimals':207,'embryos_planets':249,'system_earth':288}

def run(args,**kwargs):
    print('RUN',*[str(x) for x in args],flush=True)
    return subprocess.run([str(x) for x in args],check=True,**kwargs)
def sha(p):
    h=hashlib.sha256()
    with P(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,data):
    P(p).parent.mkdir(parents=True,exist_ok=True)
    P(p).write_text(json.dumps(data,indent=2)+'\n')
def head():
    return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def video(p,width,height,frames,audio=True):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
        '-show_streams','-show_format','-of','json',str(p)],text=True))
    vs=[s for s in data['streams'] if s['codec_type']=='video']
    aus=[s for s in data['streams'] if s['codec_type']=='audio']
    assert len(vs)==1 and len(aus)==int(audio),(p,'stream count')
    v=vs[0]
    assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'])==('h264',width,height,'yuv420p'),p
    assert int(v['nb_read_frames'])==frames and Fraction(v['avg_frame_rate'])==30,p
    assert abs(float(v.get('start_time',0)))<0.002,p
    assert abs(float(v['duration'])-frames/30)<0.01,p
    assert abs(float(data['format']['duration'])-frames/30)<0.04,p
    if audio:
        a=aus[0]
        assert a['codec_name']=='aac' and a['channels']==2 and int(a['sample_rate'])==48000,p
        assert abs(float(a.get('start_time',0)))<0.002,p
        assert abs(float(a['duration'])-frames/30)<0.04,p
    run(['ffmpeg','-nostdin','-v','error','-xerror','-i',p,'-map','0:v:0',
         *(['-map','0:a:0'] if audio else []),'-f','null','-'])
    return {'file':P(p).name,'width':width,'height':height,'frames':frames,'fps':30,
            'seconds':frames/30,'stereo_aac_48000':audio,'sha256':sha(p),'full_decode':True}

def temporal(p,frames):
    proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(p),
        '-an','-vf','scale=128:72:flags=area','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    previous=None; changes=[]; luma=[]; n=128*72*3
    while True:
        b=proc.stdout.read(n)
        if not b:break
        assert len(b)==n,'truncated decoded frame'
        f=np.frombuffer(b,np.uint8).astype(np.float32)/255
        luma.append(float(f.mean()))
        if previous is not None:changes.append(float(np.abs(f-previous).mean()))
        previous=f
    assert proc.wait()==0 and len(luma)==frames
    assert max(changes)<0.12,('severe frame jump',max(changes))
    assert max(np.abs(np.diff(luma)))<0.07,('exposure discontinuity',p)
    assert min(luma)>0.0005 and max(luma)<0.90,('blackout/whiteout',p)
    assert max(changes)>0.00001,('no motion detected',p)
    return {'decoded_frames':len(luma),'maximum_adjacent_rgb_mae':max(changes),
            'p99_adjacent_rgb_mae':float(np.percentile(changes,99)),
            'maximum_adjacent_luma_change':float(max(np.abs(np.diff(luma)))),
            'min_mean_rgb':min(luma),'max_mean_rgb':max(luma),
            'note':'Consecutive decoded frames checked; aesthetic approval remains pending.'}

def preflight():
    SHARED.mkdir(parents=True,exist_ok=True)
    identity=rf.source_fingerprint(ROOT)
    # Every invocation compiles and executes actual GLSL, in fresh GL contexts.
    # Capture out of order, then repeat; no frame may depend on previous frames.
    captures={}
    for t in [118,128,145,180,215,245,265,283]:
        for frame in [int(t*30)+2,int(t*30),int(t*30)+1,int(t*30)+1]:
            target=SHARED/f'frame_{frame}_{len(captures)}.png'
            run(['xvfb-run','-a','-s','-screen 0 1280x720x24',ROOT/'build/bigbang',
                 '--frame',frame,'--fps',30,'--width',160,'--height',90,'--output',target])
            digest=sha(target)
            if str(frame) in captures:assert captures[str(frame)]==digest,'non-deterministic native frame'
            captures[str(frame)]=digest
    run(['python3',ROOT/'scripts/create_original_score.py','--seconds',300,'--output',SHARED/'score.wav'])
    peak=0;boundary_jump=0;last=None
    with wave.open(str(SHARED/'score.wav'),'rb') as w:
        assert (w.getnchannels(),w.getframerate(),w.getnframes())==(2,32000,9600000)
        for sec in range(300):
            a=np.frombuffer(w.readframes(32000),dtype='<i2').reshape(-1,2).astype(np.int32)
            peak=max(peak,int(np.abs(a).max()))
            if last is not None:boundary_jump=max(boundary_jump,int(np.abs(a[0]-last).max()))
            last=a[-1]
    assert peak<32112 and boundary_jump<10000
    protected=subprocess.check_output(['git','rev-parse','refs/tags/native-4k-screening-43750776702^{commit}'],text=True).strip()
    assert protected=='461ed7c8f3b93428b2ed869e9238963cdef29f5e'
    run(['git','diff','--exit-code','5d7448b4bcd078baa2e889c38267deaedee642ce','HEAD','--',
         'shaders/postprocess/primordial_volume.frag','shaders/postprocess/nasa_origin.frag',
         'shaders/postprocess/cosmic_early.glsl','shaders/postprocess/cosmic_late.glsl',
         'shaders/postprocess/cosmic_evolution.frag','src/GalaxyCatalog.cpp'])
    save(SHARED/'Preflight.json',{'source_commit':head(),'source_fingerprint':identity['sha256'],
         'binary_sha256':sha(ROOT/'build/bigbang'),'repeat_frame_determinism':True,
         'out_of_order_frame_sha256':captures,'score_pcm_peak':peak/32767,
         'max_one_second_score_boundary_step':boundary_jump/32767,
         'protected_4k_renderer_commit':protected,'full_film_accepted':False})

def capture(folder,first,last):
    cmd=['xvfb-run','-a','-s','-screen 0 1280x720x24','python3',ROOT/'scripts/render_film.py',
         '--binary',ROOT/'build/bigbang','--output-dir',folder,'--first-frame',first,'--end-frame',last,
         '--width',960,'--height',540,'--fps',30,'--chunk-frames',60,'--chunk-timeout',900,
         '--preset','fast','--crf',18]
    if (folder/'manifest.json').exists():cmd.append('--resume')
    run(cmd)
    manifest=json.loads((folder/'manifest.json').read_text());state=json.loads((folder/'checkpoint.json').read_text())
    assert manifest['source']['git_head']==head() and state['status']=='complete'
    return manifest,state

def package(silent,start,frames,name,provenance):
    folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
    master=folder/(name+'.mp4');easy=folder/(name+'_Easy_Play.mp4')
    run(['ffmpeg','-nostdin','-v','error','-y','-i',silent,'-ss',start,'-i',SHARED/'score.wav',
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
         '-t',frames/30,'-movflags','+faststart',master])
    run(['ffmpeg','-nostdin','-v','error','-y','-i',master,'-vf','scale=640:360:flags=lanczos',
         '-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',
         '-ar','48000','-ac','2','-movflags','+faststart',easy])
    editions=[video(master,960,540,frames),video(easy,640,360,frames)]
    motion=temporal(master,frames)
    review_frames=[0,720,1800,2700,3600,4350,4800,5399] if frames==5400 else [0,60,120,180,240,359]
    select='+'.join(f'eq(n,{n})' for n in review_frames)
    run(['ffmpeg','-nostdin','-v','error','-y','-i',master,'-vf',
         "select='"+select+"',scale=320:180:flags=lanczos,tile="+str(len(review_frames))+'x1',
         '-frames:v','1',folder/'Contact.png'])
    run(['ffmpeg','-nostdin','-v','error','-y','-ss',(frames-1)/30,'-i',master,
         '-frames:v','1',folder/'Final_Frame.png'])
    # Animated review image supplements the packaged, fully decoded H264 video.
    if frames==360:
        run(['ffmpeg','-nostdin','-v','error','-y','-i',master,'-an','-filter_complex',
             '[0:v]fps=8,scale=480:270:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',folder/'Motion.gif'])
    report={'source_commit':head(),'native_resolution':[960,540],'global_start_seconds':start,
            'global_first_frame':start*30+1,'global_last_frame':start*30+frames,
            'editions':editions,'temporal':motion,'provenance':provenance,
            'technical_checks_passed':True,'visual_approval':'pending','full_film_accepted':False}
    save(folder/'Validation.json',report)
    shutil.copy(SHARED/'Preflight.json',folder/'Preflight.json')
    (folder/'Ubuntu_VLC.txt').write_text('V12.1 NATIVE MOVING PREVIEW — NOT A FULL FILM\n'
        'Extract this ZIP completely. In Ubuntu Files, right-click the MP4 and choose Open With VLC.\n'
        'If VLC is missing: sudo apt update && sudo apt install vlc\n'
        'Use the Easy_Play MP4 if playback stutters. Both editions include original stereo AAC audio.\n'
        '960x540 native OpenGL preview at 30 fps; Easy_Play is a 640x360 derivative.\n'
        'No upscaling, interpolation, N-body solver or physical collision simulation is claimed.\n'
        'Review cloud depth, accretion, lighting, camera motion and the final Earth approach.\n'
        'Full 1080p and revised 4K films require visual approval.\n')
    files=sorted(p for p in folder.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt')
    (folder/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in files))
    archive=OUT/(name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(folder.iterdir()):z.write(p,name+'/'+p.name)
    verify_archive(archive)
    print('VERIFIED ZIP',archive,sha(archive),flush=True)

def verify_archive(archive):
    import tempfile
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names=z.namelist();prefix=P(names[0]).parts[0]
        assert all(len(P(n).parts)==2 and P(n).parts[0]==prefix for n in names)
        for row in z.read(prefix+'/SHA256SUMS.txt').decode().splitlines():
            digest,name=row.split('  ',1)
            assert hashlib.sha256(z.read(prefix+'/'+name)).hexdigest()==digest
        report=json.loads(z.read(prefix+'/Validation.json'))
        with tempfile.TemporaryDirectory() as temp:
            for entry in report['editions']:
                p=P(temp)/entry['file'];p.write_bytes(z.read(prefix+'/'+entry['file']))
                assert sha(p)==entry['sha256']
                video(p,entry['width'],entry['height'],entry['frames'])
    return {'archive':P(archive).name,'sha256':sha(archive),'zip_crc':True,'internal_sha256':True,'downloaded_movies_fully_decoded':True}

def assemble(incoming):
    parts={}
    expected_fingerprint=rf.source_fingerprint(ROOT)['sha256']
    canonical=None
    for manifest_path in incoming.rglob('manifest.json'):
        manifest=json.loads(manifest_path.read_text());ident=manifest['identity']
        first=ident['first_frame'];last=ident['end_frame'];folder=manifest_path.parent
        assert first in range(3601,9001,300) and last==first+299 and first not in parts
        assert manifest['source']['git_head']==head() and ident['source_sha256']==expected_fingerprint
        assert ident['binary_sha256']==sha(ROOT/'build/bigbang')
        assert (ident['width'],ident['height'],ident['fps'])==(960,540,30)
        common={k:v for k,v in ident.items() if k not in ['first_frame','end_frame']}
        if canonical is None:canonical=common
        assert common==canonical,'mixed source, executable, GL driver or encoder'
        state=json.loads((folder/'checkpoint.json').read_text());assert state['identity']==ident and state['status']=='complete'
        assert sha(folder/'film.mp4')==state['final']['sha256']
        for chunk in state['chunks'].values():assert sha(folder/chunk['file'])==chunk['sha256']
        video(folder/'film.mp4',960,540,300,False)
        parts[first]=folder/'film.mp4'
    assert set(parts)==set(range(3601,9001,300)),('missing/duplicate native coverage',sorted(parts))
    concat=OUT/'parts.txt';OUT.mkdir(parents=True,exist_ok=True)
    concat.write_text(''.join("file '"+str(parts[n].resolve())+"'\n" for n in sorted(parts)))
    silent=OUT/'Planetary_Silent.mp4'
    run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',concat,'-an','-c:v','copy',silent])
    video(silent,960,540,5400,False)
    package(silent,120,5400,'V12_1_Planetary_180s',{'parts':18,'first_frame':3601,'last_frame':9000,'exact_coverage':True,'identity':canonical})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['preflight','transition','part','assemble','verify'])
    parser.add_argument('--id');parser.add_argument('--incoming',type=P)
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if args.command=='preflight':preflight()
    elif args.command=='transition':
        start=TRANSITIONS[args.id];folder=ROOT/('output/native_'+args.id)
        m,s=capture(folder,start*30+1,(start+12)*30)
        package(folder/'film.mp4',start,360,'V12_1_'+args.id,{'manifest':m,'checkpoint':s})
    elif args.command=='part':
        first=3601+int(args.id)*300
        capture(ROOT/('output/native_part_'+args.id),first,first+299)
    elif args.command=='assemble':assemble(args.incoming)
    else:
        reports=[verify_archive(p) for p in sorted(args.incoming.glob('*.zip'))]
        assert len(reports)==7
        save(args.incoming/'Release_Download_Verification.json',{'source_commit':head(),'archives':reports,'full_film_accepted':False})
if __name__=='__main__':main()
