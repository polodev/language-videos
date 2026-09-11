"""Composite HyperFrames-rendered static caption layers onto all numbered Hindi videos."""
import argparse,concurrent.futures,hashlib,json,os,sqlite3,subprocess,time
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];HINDI=ROOT/'hindi';OUTPUT=HINDI/'caption-videos';LOCAL=HINDI/'.local'

def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write_json(p,obj):
 temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');temp.replace(p)
def render(entry,force=False):
 n=entry['number'];source=HINDI/f'Videos/{n}.mp4';dest=OUTPUT/f'{n}.mp4';side=OUTPUT/f'{n}.json'
 frames=[LOCAL/f'caption-pngs/frame_{(n-1)*2+i+1:06}.png' for i in range(2)]
 fingerprint=digest(source)+''.join(digest(f) for f in frames)+str(entry['switch_seconds'])
 if not force and dest.exists() and side.exists() and json.loads(side.read_text()).get('fingerprint')==fingerprint:return n,'cached'
 assert digest(source)==entry['source_sha256'],f'Source changed: {n}'
 tmp=OUTPUT/f'.{n}.{os.getpid()}.rendering.mp4';switch=(round(entry['switch_seconds']*24)-0.5)/24  # threshold between frames avoids floating-point boundary delays
 graph=f"[0:v][1:v]overlay=0:0:enable='lt(t,{switch})':eof_action=repeat:repeatlast=1[v1];[v1][2:v]overlay=0:0:enable='gte(t,{switch})':eof_action=repeat:repeatlast=1[v]"
 command=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-filter_complex_threads','1','-i',str(source)]
 for f in frames:command+=['-i',str(f)]
 command+=['-filter_complex',graph,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','copy','-t','10','-movflags','+faststart',str(tmp)]
 result=subprocess.run(command,capture_output=True,text=True)
 if result.returncode:raise RuntimeError(f'Video {n}: {result.stderr}')
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(tmp)]))
 stream=next(s for s in info['streams'] if s['codec_type']=='video')
 assert abs(float(info['format']['duration'])-10)<.06 and int(stream['nb_frames'])==240 and (stream['width'],stream['height'])==(720,1280),n
 assert any(s['codec_type']=='audio' for s in info['streams']),n
 tmp.replace(dest)
 payload={**entry,'variant':4,'style':'original individual line backgrounds','approved_variants':[4,9],'caption_background':'individual-lines','word_highlighting':False,'output':dest.name,'source':f'../Videos/{n}.mp4','caption_engine':'HyperFrames 0.8.34 transparent PNG sequence','compositing':'FFmpeg; source audio stream copied','fingerprint':fingerprint,'output_sha256':digest(dest),'verification':{'frames':240,'dimensions':[720,1280],'duration':float(info['format']['duration']),'audio_present':True}}
 write_json(side,payload)
 return n,'rendered'

def main():
 p=argparse.ArgumentParser();p.add_argument('--numbers',help='Comma-separated prompt numbers to render');p.add_argument('--force',action='store_true');p.add_argument('--workers',type=int,default=3);p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=250);args=p.parse_args()
 OUTPUT.mkdir(exist_ok=True);plan=json.loads((LOCAL/'caption-plan.json').read_text());plan=[r for r in plan if args.start<=r['number']<=args.end]
 if args.numbers:plan=[r for r in plan if r['number'] in set(map(int,args.numbers.split(',')))]
 for f in (LOCAL/'caption-pngs').glob('*.png'):
  with Image.open(f) as im:assert im.mode=='RGBA' and im.getpixel((0,0))[3]==0
 c=sqlite3.connect(HINDI/'library.sqlite3')
 c.execute('CREATE TABLE IF NOT EXISTS caption_renders(prompt_id INTEGER PRIMARY KEY,asset_id INTEGER,variant INTEGER,output_path TEXT,output_sha256 TEXT,switch_seconds REAL,status TEXT,updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
 failures=[];done=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  futures={pool.submit(render,e,args.force):e for e in plan}
  for f in concurrent.futures.as_completed(futures):
   e=futures[f]
   try:
    n,status=f.result();side=json.loads((OUTPUT/f'{n}.json').read_text())
    c.execute("INSERT INTO caption_renders(prompt_id,asset_id,variant,output_path,output_sha256,switch_seconds,status) VALUES(?,?,?,?,?,?,?) ON CONFLICT(prompt_id) DO UPDATE SET asset_id=excluded.asset_id,variant=excluded.variant,output_path=excluded.output_path,output_sha256=excluded.output_sha256,switch_seconds=excluded.switch_seconds,status=excluded.status,updated_at=CURRENT_TIMESTAMP",(n,e['asset_id'],4,f'caption-videos/{n}.mp4',side['output_sha256'],e['switch_seconds'],'complete'));c.commit();done+=1
    print(f'{done}/{len(plan)} complete: {n}.mp4 ({status})',flush=True)
   except Exception as exc:failures.append({'number':e['number'],'error':str(exc)});print('FAILED',e['number'],exc,flush=True)
   write_json(LOCAL/'caption-progress.json',{'completed_this_run':done,'planned':len(plan),'failures':failures})
 if failures:raise SystemExit(1)
 print('All requested renders complete.',flush=True)

if __name__=='__main__':main()
