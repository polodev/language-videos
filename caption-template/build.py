#!/usr/bin/env python3
"""Build a reusable HyperFrames project with the chosen outlined caption style."""
import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def build(number, switch, output, variant=None):
 config=json.loads((HERE/'template.json').read_text())
 variant=variant or config['preferred_variant']
 preset=next(x for x in json.loads((HERE/'variants.json').read_text()) if x['variant']==variant)
 lesson=next(x for x in json.loads((ROOT/'hindi/videos.json').read_text()) if x['video_number']==number)
 video=ROOT/f'hindi/Videos/{number}.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
 stream=next(x for x in probe['streams'] if x['codec_type']=='video')
 width,height,duration=stream['width'],stream['height'],float(stream['duration'])
 fps=stream['avg_frame_rate'];num,den=map(int,fps.split('/'));rate=num/den
 switch=round(switch*rate)/rate
 if not 0 < switch < duration:raise ValueError('Sentence switch must be inside the video.')
 if len(lesson['sentences'])!=2:raise ValueError('This template expects exactly two sentences.')
 output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
 assets=output/'assets';assets.mkdir(exist_ok=True)
 for source in (HERE/'assets').iterdir():shutil.copy2(source,assets/source.name)
 shutil.copy2(video,assets/'source.mp4')
 scale=width/720;layout=config['layout'];blocks=[];css=[]
 for index,line in enumerate(config['lines']):
  css.append(f'.line-{index}{{font-family:{line["font"]};color:{line["color"]};font-size:{line["size_at_720"]*scale}px;font-weight:{line["weight"]};line-height:{line["line_height"]}}}')
 for n,(start,end) in enumerate([(0,switch),(switch,duration)]):
  text=''.join(f'<p class="line line-{i} {("hi","pron","meaning")[i]}" lang="{line["language"]}">{html.escape(lesson["sentences"][n][line["key"]])}</p>' for i,line in enumerate(config['lines']))
  blocks.append(f'<section id="sentence-{n+1}" class="clip caption" data-caption-layer="fg" data-start="{start}" data-duration="{end-start}" data-track-index="2">{text}</section>')
 content=f'''<!doctype html><html lang="bn"><head><meta charset="utf-8"><title>Hindi {number} — outlined captions</title><script src="assets/gsap.min.js"></script><style>
 @font-face{{font-family:Bangla;src:url('assets/bengali.ttf');font-weight:100 900;font-display:block}}
 @font-face{{font-family:Hindi;src:url('assets/devanagari.ttf');font-weight:100 900;font-display:block}}
 *{{box-sizing:border-box}}body{{margin:0}}#root{{width:{width}px;height:{height}px;position:relative;overflow:hidden}}
 video{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}}
 .caption{{position:absolute;left:{width*layout['left_fraction']}px;right:{width*layout['right_fraction']}px;top:{height*layout['top_fraction']}px;padding:0 {width*layout['horizontal_padding_fraction']}px;text-align:center;z-index:2;background:transparent}}
 .line{{margin:0;white-space:nowrap;background:transparent;-webkit-text-stroke:{config['outline']['width_at_720']*scale}px {config['outline']['color']};paint-order:stroke fill}}
 {''.join(css)}
 {preset['css']}</style></head><body><div id="root" data-composition-id="hindi-caption" data-width="{width}" data-height="{height}" data-duration="{duration}" data-fps="{fps}">
 <video id="source-video" class="clip" src="assets/source.mp4" data-start="0" data-duration="{duration}" data-track-index="0" muted playsinline></video>
 <audio id="source-audio" src="assets/source.mp4" data-start="0" data-duration="{duration}" data-track-index="1"></audio>
 {''.join(blocks)}</div><script>document.fonts.ready.then(()=>{{window.__timelines["hindi-caption"]=gsap.timeline({{paused:true}});}});</script></body></html>'''
 (output/'index.html').write_text(content)
 (output/'hyperframes.json').write_text(json.dumps({'authoringSkill':'embedded-captions','media':{'autoProxy':True}},indent=2))
 (output/'package.json').write_text(json.dumps({'name':'outlined-caption','private':True,'scripts':{'check':'npx --yes hyperframes@0.8.34 check','render':'npx --yes hyperframes@0.8.34 render'}},indent=2))
 (output/'caption.json').write_text(json.dumps({'prompt_number':number,'template':config,'variant':variant,'variant_name':preset['name'],'switch_seconds':switch,'lesson':lesson},ensure_ascii=False,indent=2))
 print(output)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--variant',type=int,choices=range(1,11),help='Default: the preferred variant in template.json')
 parser.add_argument('--number',type=int,required=True)
 parser.add_argument('--switch',type=float,required=True,help='Reviewed start of the second Hindi sentence, in seconds')
 parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();build(args.number,args.switch,args.output,args.variant)
