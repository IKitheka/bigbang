#!/usr/bin/env python3
"""Render/compare the protected interval on one driver; no image synthesis."""
import argparse, hashlib, json, os, subprocess
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-binary',type=Path,required=True)
    p.add_argument('--candidate-binary',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    historic=json.loads((Path(__file__).parent/'data/protected_opening_sha256.json').read_text())
    capture={}
    for label,binary in [('base',a.base_binary.resolve()),('candidate',a.candidate_binary.resolve())]:
        target=out/label; target.mkdir(exist_ok=True)
        rows=[]
        for i in range(41):
            t=f'{18+i/10:.3f}'; path=target/f'frame_{i:04}.png'
            command=[str(binary),'--time',t,'--fps','30','--width','480','--height','270','--output',str(path)]
            run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=45)
            (target/f'frame_{i:04}.log').write_text(run.stdout)
            if run.returncode: raise RuntimeError(run.stdout)
            rows.append({'time_seconds':float(t),'sha256':sha(path)})
        capture[label]=rows
    exact=sum(x['sha256']==y['sha256'] for x,y in zip(capture['base'],capture['candidate']))
    historic_rows=historic['samples']
    previous=sum(x['sha256']==y['sha256'] for x,y in zip(historic_rows,capture['candidate']))
    report={'same_environment_base_commit':'e6d299579a1b06d3d9dcb2e79bddafb8784d0a7e',
            'historical_artifact':14129433323,'same_environment_exact_frames':exact,
            'historical_exact_frames':previous,'expected_frames':41,
            'source_regression_passed':exact==41,'historical_exact_passed':previous==41,
            'samples':capture,
            'limits':'Historical byte identity can depend on Mesa/LLVM. Same-environment differences fail this test. Artistic approval is separate.'}
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
    return 0 if exact==41 else 1

if __name__=='__main__':
    raise SystemExit(main())
