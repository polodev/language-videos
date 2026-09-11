"""Prepare a reusable HyperFrames stamp and sequential delivery plan for a locale."""
import argparse, html, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def prepare(locale):
    cfg=json.loads((ROOT/'video-delivery-template/settings.json').read_text())
    language=cfg['locales'][locale]
    base=ROOT/locale
    files=sorted((base/cfg['source_folder']).glob('*.mp4'),key=lambda p:int(p.stem))
    if not files: raise SystemExit(f'No captioned videos in {base/cfg["source_folder"]}')
    work=base/'.local/video-delivery'; project=work/'stamp-project'
    (project/'assets').mkdir(parents=True,exist_ok=True)
    for source,name in [('devanagari.ttf','font.ttf'),('gsap.min.js','gsap.min.js')]:
        shutil.copy2(ROOT/'caption-template/assets'/source,project/'assets'/name)
    records=[]
    for path in files:
        side=json.loads(path.with_suffix('.json').read_text())
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
        video=next(x for x in probe['streams'] if x['codec_type']=='video')
        audio=next(x for x in probe['streams'] if x['codec_type']=='audio')
        records.append({'number':int(path.stem),'path':str(path.relative_to(ROOT)),
            'duration':float(video['duration']),'frames':int(video['nb_frames']),
            'width':video['width'],'height':video['height'],'fps':video['r_frame_rate'],
            'sample_rate':audio['sample_rate'],'channels':audio['channels'],
            'lesson':side['lesson']})
    signatures={(r['width'],r['height'],r['fps'],r['sample_rate'],r['channels']) for r in records}
    if len(signatures)!=1: raise SystemExit('Mixed source formats: normalize explicitly before merging')
    w,h=records[0]['width'],records[0]['height']; scale=w/720
    stamp=cfg['stamp'];text=stamp['text_template'].format(locale=language,language=language)
    markup='''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Brand stamp</title>
<script src="assets/gsap.min.js"></script><style>
@font-face{font-family:Brand;src:url('assets/font.ttf');font-weight:100 900;font-display:block}
*{box-sizing:border-box}html,body{margin:0;background:transparent}
#root{position:relative;width:WIDTHpx;height:HEIGHTpx;overflow:hidden;background:transparent}
#stamp{position:absolute;top:TOPpx;right:RIGHTpx;margin:0;font-family:Brand;font-weight:700;font-size:SIZEpx;line-height:1.5;white-space:nowrap;color:COLOR;-webkit-text-stroke:OUTLINEpx OUTLINECOLOR;paint-order:stroke fill;background:transparent}
</style></head><body><div id="root" data-composition-id="brand-stamp" data-width="WIDTH" data-height="HEIGHT" data-duration="1" data-fps="1"><p id="stamp" class="clip" data-start="0" data-duration="1">TEXT</p></div>
<script>document.fonts.ready.then(()=>{window.__timelines['brand-stamp']=gsap.timeline({paused:true});});</script></body></html>'''
    replacements={'WIDTH':str(w),'HEIGHT':str(h),'TOP':str(stamp['top_px_at_1280']*h/1280),
      'RIGHT':str(stamp['right_px_at_720']*scale),'SIZE':str(stamp['font_size_px_at_720']*scale),
      'OUTLINECOLOR':stamp['outline_color'],'OUTLINE':str(stamp['outline_px_at_720']*scale),
      'COLOR':stamp['color'],'TEXT':html.escape(text)}
    for key,value in replacements.items():markup=markup.replace(key,value)
    (project/'index.html').write_text(markup)
    (project/'hyperframes.json').write_text(json.dumps({'authoringSkill':'general-video'}))
    (project/'BRIEF.md').write_text(f'''# Delivery stamp
workflow: general-video
flow: automation
storyboard: no

Render a single transparent {w}x{h} brand stamp PNG: {text}, top right, white text with dark outline, no background. Reuse this unchanged over all captioned source clips, then concatenate complete clips with hard cuts into sequential groups of 3, 15 and 30. Keep final partial groups. No browser preview; exports already requested. Preserve original captioned sources and caption timing. No music, transitions or new narration.
''')
    plan={'locale':locale,'language':language,'stamp_text':text,'settings':cfg,'sources':records,'groups':{}}
    for size,setting in cfg['outputs'].items():
        (base/setting['folder']).mkdir(exist_ok=True)
        n=setting['clips_per_video']
        plan['groups'][size]=[{'number':i//n+1,'source_numbers':[r['number'] for r in records[i:i+n]],'duration':round(sum(r['duration'] for r in records[i:i+n]),6),'frames':sum(r['frames'] for r in records[i:i+n])} for i in range(0,len(records),n)]
    (work/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'source_count':len(records),'stamp':text,'groups':{k:len(v) for k,v in plan['groups'].items()},'project':str(project)}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--locale',default='hindi');prepare(parser.parse_args().locale)
