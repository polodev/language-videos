"""Match the second Hindi sentence to saved offline Whisper word timings."""
import json,sqlite3,sys
from pathlib import Path
from rapidfuzz.fuzz import ratio
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sort_hindi import normalize
ROOT=Path(__file__).resolve().parents[1]
c=sqlite3.connect(ROOT/'hindi/library.sqlite3');c.row_factory=sqlite3.Row
lessons=json.loads((ROOT/'hindi/videos.json').read_text());plan=[]
for lesson in lessons:
 n=lesson['video_number'];a=c.execute('select * from assets where present=1 and prompt_id=?',(n,)).fetchone()
 words=[w for s in json.loads(a['transcript'])['segments'] for w in s.get('words',[])]
 target=normalize(lesson['sentences'][1]['hindi']);choices=[]
 for i,w in enumerate(words):
  if not 2.3<=w['start']<=7:continue
  for j in range(i+1,min(len(words),i+22)+1):
   heard=normalize(' '.join(x['word'] for x in words[i:j]));score=ratio(target,heard)
   # Prefer the intended ~5s handoff only to break near-ties, not to hide poor matches.
   adjusted=score-.75*abs(w['start']-5)
   choices.append((adjusted,score,w['start'],heard,words[j-1]['end']))
 choices.sort(reverse=True)
 best=choices[0] if choices else (0,0,5,'NO WORD MATCH',5)
 plan.append({'number':n,'asset_id':a['id'],'source_sha256':a['sha256'],'switch_seconds':round(best[2]*24)/24,'score':round(best[1],1),'heard':best[3],'expected':lesson['sentences'][1]['hindi'],'lesson':lesson})
overrides=json.loads((ROOT/'caption-template/hindi-timing-overrides.json').read_text())
for entry in plan:
 entry['timing_method']='Reviewed second-sentence match against offline Whisper-small word timestamps'
 for override in overrides:
  if entry['number']==override['number'] and entry['source_sha256']==override['source_sha256']:
   entry.update({k:override[k] for k in ('switch_seconds','timing_method')})
p=ROOT/'hindi/.local/caption-plan.json';p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
for x in plan:print(f"{x['number']:3} {x['switch_seconds']:4.2f} {x['score']:4.1f} {x['heard']}")
