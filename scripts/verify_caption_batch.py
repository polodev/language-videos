"""Verify media, hashes, and caption pixels immediately around every sentence switch."""
import concurrent.futures,hashlib,json,sqlite3,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'hindi';OUT=H/'caption-videos';LOCAL=H/'.local'
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify(n):
 meta=json.loads((OUT/f'{n}.json').read_text());video=OUT/f'{n}.mp4'
 assert digest(video)==meta['output_sha256'],f'{n}: output checksum'
 assert digest(H/f'Videos/{n}.mp4')==meta['source_sha256'],f'{n}: source checksum'
 switch=round(meta['switch_seconds']*24);errors=[];bad_frames=[]
 wanted=[24,switch-1,switch,192]
 expression="select='"+'+'.join(f'eq(n,{n})' for n in wanted)+"'"
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(video),'-vf',expression,'-vsync','0','-pix_fmt','rgb24','-threads','1','-f','rawvideo','-'],stderr=subprocess.PIPE)
 decoded=np.frombuffer(raw,dtype=np.uint8).reshape((-1,1280,720,3));assert len(decoded)==4,n
 layers=[np.array(Image.open(LOCAL/f'caption-pngs/frame_{(n-1)*2+i+1:06}.png')) for i in range(2)]
 comparison=(layers[0][:,:,3]==255)&(layers[1][:,:,3]==255)&(np.max(np.abs(layers[0][:,:,:3].astype(float)-layers[1][:,:,:3].astype(float)),axis=2)>30)
 assert comparison.sum()>100,(n,'Not enough distinctive caption pixels')
 for position,(index,frame) in enumerate([(0,24),(0,switch-1),(1,switch),(1,192)]):
  p=LOCAL/f'caption-pngs/frame_{(n-1)*2+index+1:06}.png'
  image=np.array(Image.open(p));mask=image[:,:,3]==255
  rgb=decoded[position]
  error=float(np.abs(rgb[mask].astype(float)-image[:,:,:3][mask].astype(float)).mean());errors.append(round(error,3))
  distances=[float(np.abs(rgb[comparison].astype(float)-layer[:,:,:3][comparison].astype(float)).mean()) for layer in layers]
  if error>=10 or distances[index]>=distances[1-index]:bad_frames.append({'frame':frame,'error':error,'sentence_distances':distances})
 def audio_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'])
 assert audio_hash(H/f'Videos/{n}.mp4')==audio_hash(video),f'{n}: audio stream changed'
 return {'number':n,'caption_pixel_errors':errors,'bad_frames':bad_frames,'source_unchanged':True,'audio_stream_unchanged':True,'output_checksum_valid':True}
def safe_verify(n):
 try:return verify(n)
 except Exception as error:return {'number':n,'caption_pixel_errors':[],'bad_frames':[],'error':str(error)}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--numbers',help='Comma-separated prompt numbers to verify');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=250);args=p.parse_args()
 numbers=list(map(int,args.numbers.split(','))) if args.numbers else list(range(args.start,args.end+1))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  results=[]
  for result in pool.map(safe_verify,numbers):
   results.append(result)
   if len(results)%25==0:print('Checked',len(results),'videos',flush=True)
 report=LOCAL/'caption-final-verification.json'
 previous=json.loads(report.read_text()) if (args.start>1 or args.numbers) and report.exists() else []
 combined={x['number']:x for x in previous+results}
 report.write_text(json.dumps([combined[n] for n in sorted(combined)],indent=2))
 print('Checked',len(results),'videos, both captions, frame-exact handoffs, original hashes and export hashes.')
 print('Maximum mean caption pixel error:',max([max(x['caption_pixel_errors']) for x in results if x['caption_pixel_errors']] or [0]))

 if any(x['bad_frames'] or x.get('error') for x in results):
  print('Needs correction:',[x['number'] for x in results if x['bad_frames'] or x.get('error')]);raise SystemExit(1)
