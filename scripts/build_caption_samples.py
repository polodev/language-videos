"""Build five static three-line HyperFrames caption samples for Hindi prompt 1."""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hindi/caption-project'
OUTPUT = ROOT / 'hindi/caption-videos'
STYLES = [
 ('dark-card', '.caption{background:#142020;border-radius:22px;padding:24px 22px;box-shadow:0 8px 25px #0005}.hi{color:#fff}.pron{color:#f8da82}.meaning{color:#fff}'),
 ('light-card', '.caption{background:#fffaf0;border:2px solid #ddd2bc;border-radius:18px;padding:24px 22px;box-shadow:0 8px 25px #0004}.hi{color:#172525}.pron{color:#675025}.meaning{color:#172525}'),
 ('outlined', '.caption{padding:24px 22px;background:#101820d9;border-radius:8px}.line{color:#fff;-webkit-text-stroke:1px #000;paint-order:stroke fill;text-shadow:0 2px 3px #000}.pron{color:#ffe28b}'),
 ('line-bands', '.caption{display:flex;flex-direction:column;align-items:center;gap:8px;padding:0}.line{background:#132c31;border-radius:8px;padding:8px 22px;align-self:center}.hi{color:#fff}.pron{background:#f8df9c;color:#2f2715}.meaning{background:#fffaf0;color:#172525}'),
 ('left-panel', '.caption{background:#142020;border-left:6px solid #f1d182;border-radius:0 16px 16px 0;padding:24px 28px;text-align:left}.hi{color:#fff}.pron{color:#f8da82}.meaning{color:#fff}'),
]

def build():
 PROJECT.mkdir(exist_ok=True);OUTPUT.mkdir(exist_ok=True)
 shutil.copy2(ROOT/'hindi/Videos/1.mp4',PROJECT/'assets/source.mp4')
 (PROJECT/'variants').mkdir(exist_ok=True)
 lesson=json.loads((ROOT/'hindi/videos.json').read_text())[0]
 # The second Hindi sentence starts at 4.94 s in the reviewed local Whisper-small transcript.
 # Snap to the nearest source frame (24 fps), retaining the first block during its Bangla meaning.
 boundary=119/24
 blocks=[]
 for index,(start,end) in enumerate([(0,boundary),(boundary,10)]):
  s=lesson['sentences'][index]
  rows=''.join(f'<p class="line {cls}" lang="{lang}">{html.escape(s[key])}</p>' for cls,lang,key in [('hi','hi','hindi'),('pron','bn','bangla_pronunciation'),('meaning','bn','bangla_meaning')])
  blocks.append(f'<section id="sentence-{index+1}" class="clip caption" data-caption-layer="fg" data-start="{start}" data-duration="{end-start}" data-track-index="2">{rows}</section>')
 base='''<!doctype html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=720,height=1280"><title>Hindi captions — STYLE</title>
<script src="assets/gsap.min.js"></script><style>
@font-face{font-family:Bangla;src:url('assets/bengali.ttf') format('truetype');font-weight:100 900;font-display:block}
@font-face{font-family:Hindi;src:url('assets/devanagari.ttf') format('truetype');font-weight:100 900;font-display:block}
*{box-sizing:border-box}body{margin:0;background:#000}#root{width:720px;height:1280px;position:relative;overflow:hidden}
video{position:absolute;inset:0;width:720px;height:1280px;object-fit:contain}
.caption{position:absolute;left:46px;right:70px;top:810px;z-index:2;text-align:center}
.line{margin:0;font-family:Bangla,sans-serif;font-size:34px;font-weight:600;line-height:1.5;white-space:nowrap}
.hi{font-family:Hindi,sans-serif;font-size:39px;font-weight:700;line-height:1.5}
STYLECSS
</style></head><body><div id="root" data-composition-id="hindi-caption" data-width="720" data-height="1280" data-duration="10" data-fps="24">
<video id="source-video" class="clip" src="assets/source.mp4" data-start="0" data-duration="10" data-track-index="0" muted playsinline></video>
<audio id="source-audio" src="assets/source.mp4" data-start="0" data-duration="10" data-track-index="1" data-volume="1"></audio>
BLOCKS
</div><script>document.fonts.ready.then(()=>{window.__timelines["hindi-caption"]=gsap.timeline({paused:true});});</script></body></html>'''
 for n,(name,css) in enumerate(STYLES,1):
  content=base.replace('STYLECSS',css).replace('STYLE',name).replace('BLOCKS','\n'.join(blocks))
  (PROJECT/'variants'/f'variant-{n}.html').write_text(content)
  (OUTPUT/f'variant-{n}.json').write_text(json.dumps({'variant':n,'style':name,'source_prompt':'prompt_1','source_video':'../Videos/1.mp4','caption_switch_seconds':boundary,'word_highlighting':False,'lesson':lesson},ensure_ascii=False,indent=2)+'\n')
 (PROJECT/'index.html').write_text((PROJECT/'variants/variant-1.html').read_text())
 (PROJECT/'BRIEF.md').write_text('''---
workflow: embedded-captions
flow: automation
storyboard: no
language: Hindi and Bengali
aspect: 9:16
---

Create only five rendered style variants of prompt 1 for user selection. Use the same original footage and audio, and three unlabeled lines per sentence: Hindi, Hindi pronunciation in Bengali script, Bangla meaning. No word highlighting, animation, subject matting or embedded text. Switch the entire block at the second Hindi sentence, using the existing offline Whisper-small transcript for timing. The explicit three-line, sentence-only brief overrides the workflow's two-line and animated verbatim defaults. User explicitly authorized five test renders; full-collection rendering awaits their chosen variant.

The original remains in Videos; the five samples go to caption-videos. Typography uses local Noto Sans Devanagari and Noto Sans Bengali. Five static treatments: dark card, light card, outlined, line bands, left panel. Native 720×1280, 24fps, 10 seconds. All font files and GSAP are local at render time.
''')
 print('Built five styles with caption boundary',boundary)

if __name__=='__main__':build()
