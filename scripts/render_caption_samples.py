"""Render the authorized sample styles with HyperFrames, validating each first."""
import argparse,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'hindi/caption-project'
OUTPUT=ROOT/'hindi/caption-videos'
p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=5);args=p.parse_args()
for n in range(args.start,args.end+1):
 work=ROOT/'hindi/.local/caption-renders'/f'variant-{n}';work.mkdir(parents=True,exist_ok=True)
 shutil.copy2(PROJECT/'variants'/f'variant-{n}.html',work/'index.html')
 for name in ('hyperframes.json','package.json','BRIEF.md'):shutil.copy2(PROJECT/name,work/name)
 if not (work/'assets').exists():(work/'assets').symlink_to(PROJECT/'assets',target_is_directory=True)
 for action,options in [('check',['--at','1,4.9,5,8','--snapshots']),('render',['--quality','high','--fps','24','--workers','2','--output',str(OUTPUT/f'variant-{n}.mp4')])]:
  print(f'Variant {n}: {action}',flush=True)
  with (ROOT/f'hindi/.local/caption-{action}-{n}.log').open('w') as log:
   subprocess.run(['npx','--yes','hyperframes@0.8.34',action,*options],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(f'Variant {n}: complete',flush=True)
