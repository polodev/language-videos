"""Build outlined three-line HyperFrames caption samples for Hindi prompt 1."""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hindi/caption-project'
OUTPUT = ROOT / 'hindi/caption-videos'
STYLES = [(row['name'], row['css']) for row in json.loads((ROOT/'caption-template/variants.json').read_text())]

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
.caption{position:absolute;left:46px;right:70px;top:834px;z-index:2;text-align:center;padding:0 16px;background:transparent}
.line{margin:0;font-family:Bangla,sans-serif;font-size:34px;font-weight:600;line-height:1.6;white-space:nowrap;-webkit-text-stroke:3.5px #111;paint-order:stroke fill;background:transparent}
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
  (OUTPUT/f'variant-{n}.json').write_text(json.dumps({'variant':n,'style':name,'source_prompt':'prompt_1','source_video':'../Videos/1.mp4','caption_switch_seconds':boundary,'word_highlighting':False,'caption_background':False,'outline':True,'lesson':lesson},ensure_ascii=False,indent=2)+'\n')
 (PROJECT/'index.html').write_text((PROJECT/'variants/variant-4.html').read_text())
 (PROJECT/'BRIEF.md').write_text('''---
workflow: embedded-captions
flow: automation
storyboard: no
language: Hindi and Bengali
aspect: 9:16
---

Create only ten rendered style variants of prompt 1 for user selection. Use the same original footage and audio, and three unlabeled lines per sentence: Hindi, Hindi pronunciation in Bengali script, Bangla meaning. No word highlighting, animation, subject matting or embedded text. Switch the entire block at the second Hindi sentence, using the existing offline Whisper-small transcript for timing. The explicit three-line, sentence-only brief overrides the workflow's two-line and animated verbatim defaults. User authorized ten test renders and wants to select multiple variants. Variant 4 is the first choice, saved at root caption-template; full-collection rendering awaits the final style choices.

The original remains in Videos; the samples go to caption-videos. Typography uses local Noto Sans Devanagari and Noto Sans Bengali. Five outlined-text treatments: all white, yellow pronunciation, yellow Hindi, three colors, and bold white. Captions must NEVER have any background, box, panel, band or scrim. Only glyph outlines provide contrast. No browser previews; export MP4 files directly. Native 720×1280, 24fps, 10 seconds. All font files and GSAP are local at render time.
''')
 print('Built',len(STYLES),'styles with caption boundary',boundary)

if __name__=='__main__':build()
