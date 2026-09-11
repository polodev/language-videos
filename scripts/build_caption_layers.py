"""Build a HyperFrames PNG-sequence project: one frame per sentence caption."""
import html,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'hindi/.local/caption-layers'
WORK.mkdir(parents=True,exist_ok=True)
(WORK/'assets').mkdir(exist_ok=True)
for f in (ROOT/'caption-template/assets').iterdir():shutil.copy2(f,WORK/'assets'/f.name)
plan=json.loads((ROOT/'hindi/.local/caption-plan.json').read_text())
metrics=json.loads((ROOT/'hindi/.local/caption-text-fit.json').read_text())
lookup={(x['number'],x['sentence'],x['key']):x for x in metrics}
blocks=[];sizes=[]
for entry in plan:
 for si,s in enumerate(entry['lesson']['sentences']):
  frame=(entry['number']-1)*2+si;lines=[]
  for k,cls,lang,base in [('hindi','hi','hi',39),('bangla_pronunciation','pron','bn',34),('bangla_meaning','meaning','bn',34)]:
   metric=lookup[entry['number'],si+1,k]
   # Text width + 44px pill padding + 4px breathing room must fit the 604px caption column.
   size=min(base,int(base*556/(metric['width']+1)*10)/10)
   sizes.append({'number':entry['number'],'sentence':si+1,'key':k,'font_size':size,'text':s[k]})
   lines.append(f'<p class="line {cls}" lang="{lang}" style="font-size:{size}px">{html.escape(s[k])}</p>')
  blocks.append(f'<section id="caption-{entry["number"]}-{si+1}" class="clip caption" data-start="{frame}" data-duration="1" data-track-index="1">'+''.join(lines)+'</section>')
content='''<!doctype html><html lang="bn"><head><meta charset="utf-8"><title>Hindi caption layers</title><script src="assets/gsap.min.js"></script><style>
@font-face{font-family:Bangla;src:url('assets/bengali.ttf');font-weight:100 900;font-display:block}
@font-face{font-family:Hindi;src:url('assets/devanagari.ttf');font-weight:100 900;font-display:block}
*{box-sizing:border-box}html,body{margin:0;background:transparent}#root{width:720px;height:1280px;position:relative;overflow:hidden;background:transparent}
.caption{position:absolute;left:46px;right:70px;top:810px;display:flex;flex-direction:column;align-items:center;gap:8px;padding:0;background:transparent;text-align:center}
.line{margin:0;white-space:nowrap;font-family:Bangla;font-weight:600;line-height:1.5;border-radius:8px;padding:8px 22px;align-self:center}
.hi{font-family:Hindi;font-weight:700;color:#fff;background:#132c31}.pron{color:#2f2715;background:#f8df9c}.meaning{color:#172525;background:#fffaf0}
</style></head><body><div id="root" data-composition-id="caption-layers" data-width="720" data-height="1280" data-duration="500" data-fps="1">BLOCKS</div>
<script>document.fonts.ready.then(()=>{window.__timelines['caption-layers']=gsap.timeline({paused:true});});</script></body></html>'''.replace('BLOCKS','\n'.join(blocks))
(WORK/'index.html').write_text(content)
(WORK/'hyperframes.json').write_text(json.dumps({'authoringSkill':'embedded-captions'}))
(WORK/'package.json').write_text(json.dumps({'name':'caption-layers','private':True,'scripts':{'check':'npx --yes hyperframes@0.8.34 check','render':'npx --yes hyperframes@0.8.34 render'}}))
(WORK/'BRIEF.md').write_text('Render exactly 500 transparent PNG caption layers with HyperFrames, one per Hindi sentence. User selected the ORIGINAL variant 4 with individual backgrounds behind each of three lines. These layers are held over original footage with FFmpeg at reviewed per-video sentence boundaries. No word highlighting, animation, or browser preview. Full batch of 250 captioned videos explicitly authorized. Preserve source files and audio.\n')
(ROOT/'hindi/.local/caption-fitted-lines.json').write_text(json.dumps(sizes,ensure_ascii=False,indent=2))
print('500 caption layers built; minimum font size',min(x['font_size'] for x in sizes))
