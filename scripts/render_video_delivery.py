"""Stamp captioned sources once, concatenate groups, and export upload metadata.

Run prepare_video_delivery.py and render its HyperFrames PNG before this script.
Upload metadata is provisional until an uploader example schema is supplied.
"""
import argparse, concurrent.futures, hashlib, json, os, subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(command):
    p=subprocess.run(command,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr[-3000:])
    return p.stdout

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def save(path,obj):
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');temp.replace(path)

def probe(path):
    data=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    v=next(x for x in data['streams'] if x['codec_type']=='video')
    a=next(x for x in data['streams'] if x['codec_type']=='audio')
    return {'frames':int(v['nb_frames']),'duration':float(v['duration']),'container_duration':float(data['format']['duration']),'audio_duration':float(a['duration']),'width':v['width'],'height':v['height']}

def verify(path,frames,duration,dimensions,decode=False):
    info=probe(path)
    assert info['frames']==frames,(path,info,frames)
    assert abs(info['duration']-duration)<0.05,(path,info,duration)
    assert abs(info['audio_duration']-duration)<0.1,(path,info,duration)
    assert (info['width'],info['height'])==dimensions
    if decode:run(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-nostdin','-threads','2','-i',str(path),'-f','null','-'])
    return info

def stamp_source(record,work,png):
    src=ROOT/record['path'];folder=work/'stamped';folder.mkdir(exist_ok=True)
    dest=folder/f"{record['number']}.mp4";meta=dest.with_suffix('.json')
    fingerprint=sha(src)+sha(png)+'stamp-v2'
    if dest.exists() and meta.exists():
        data=json.loads(meta.read_text())
        if data.get('fingerprint')==fingerprint and data.get('sha256')==sha(dest):return record['number'],'cached'
    temp=dest.with_name(f'.{record["number"]}.{os.getpid()}.tmp.mp4')
    run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-filter_complex_threads','1','-i',str(src),'-i',str(png),'-filter_complex','[0:v][1:v]overlay=0:0:eof_action=repeat:repeatlast=1[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-preset','ultrafast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','copy','-t',str(record['duration']),'-movflags','+faststart',str(temp)])
    info=verify(temp,record['frames'],record['duration'],(record['width'],record['height']))
    temp.replace(dest);save(meta,{'source':record['path'],'source_sha256':sha(src),'fingerprint':fingerprint,'sha256':sha(dest),'verification':info})
    return record['number'],'stamped'

def bnnum(n):return str(n).translate(str.maketrans('0123456789','০১২৩৪৫৬৭৮৯'))

def metadata(group,records,plan,cfg,size):
    lessons=[records[n]['lesson'] for n in group['source_numbers']]
    language=plan['language'];bn=cfg['language_names_bn'][language];brand=cfg['brand_name_template'].format(language=language);handle=cfg['handle_template'].format(language=language)
    counts=Counter(l['topic'] for l in lessons)
    topics=[cfg['topic_names_bn'].get(t,f'{bn} কথোপকথন') for t,_ in counts.most_common()]
    topics=list(dict.fromkeys(topics));sentences=sum(len(l['sentences']) for l in lessons)
    short_topics=[cfg.get('topic_title_bn',{}).get(t,cfg['topic_names_bn'].get(t,'কথোপকথন')) for t,_ in counts.most_common(3)]
    short_topics=list(dict.fromkeys(short_topics))
    focus=topics[0] if len(topics)==1 else (', '.join(short_topics[:-1])+' ও '+short_topics[-1] if len(short_topics)>1 else short_topics[0])
    if len(focus)>45:focus=' ও '.join(short_topics[:2])
    part=bnnum(group['number']);title=f'{bn} শিখুন: {focus} | {bnnum(sentences)}টি বাক্য | পর্ব {part}'
    if len(title)>100:title=f'বাংলায় {bn} শিখুন | {bnnum(sentences)}টি দরকারি বাক্য | পর্ব {part}'
    lines=[f'{focus} নিয়ে {bnnum(sentences)}টি সহজ {bn} বাক্য শিখুন—বাংলা উচ্চারণ ও অর্থসহ।',f'এই সংকলনে আছে: {", ".join(topics)}।','',f'{brand} | Learn {language} easily through Bangla.','ভিডিও শুনুন, বাংলা উচ্চারণ দেখে বলুন এবং নিজে অনুশীলন করুন।','','এই ভিডিওর পাঠ:']
    offset=0;segments=[]
    for n,l in zip(group['source_numbers'],lessons):
        r=records[n];label=l.get('upload_title',f'{bn} পাঠ {bnnum(n)}')
        lines.append(f'{int(offset)//60:02d}:{int(offset)%60:02d} — {label}')
        segments.append({'source_number':n,'source_file':r['path'],'start_seconds':round(offset,6),'end_seconds':round(offset+r['duration'],6),'title':label,'sentences':l['sentences']})
        offset+=r['duration']
    hashtags=[f'#{handle.lstrip("@")}',f'#বাংলায়{bn}শেখা',f'#Learn{language}InBangla']
    lines+=['',f'আরও {bn} বাক্য শিখতে {brand} ফলো করুন।',' '.join(hashtags)]
    description='\n'.join(lines)
    caption=f'{focus} নিয়ে {bnnum(sentences)}টি {bn} বাক্য—বাংলা উচ্চারণ ও অর্থসহ।\nশুনে নিজে বলুন, অনুশীলনের জন্য সেভ করুন।\n\n'+ ' '.join(hashtags)
    tags=[brand,f'বাংলায় {bn} শেখা',f'বাংলা উচ্চারণে {bn}',f'learn {language} in Bangla',f'{language} for Bengali speakers',f'{bn} কথোপকথন']
    tags+= [f'{bn} {topic}' for topic in topics[:3]]
    return {'id':f'{plan["locale"]}-{size}-{group["number"]:03d}','project_title':f'{language} {size} {group["number"]:03d} — merged from video IDs '+', '.join(map(str,group['source_numbers'])),'file':f'{group["number"]}.mp4','title':title,'description':description,'caption':caption,'tags':tags,'hashtags':hashtags,'language':language,'audience_language':'bn-BD','brand_name':brand,'handle':handle,'stamp':plan['stamp_text'],'duration_seconds':group['duration'],'sentence_count':sentences,'source_video_numbers':group['source_numbers'],'segments':segments,'platforms':{'youtube':{'title':title,'description':description,'tags':tags},'facebook':{'title':title,'description':caption},'instagram':{'caption':caption}}}

def merge_group(size,group,records,work,base,cfg,plan):
    folder=base/cfg['outputs'][size]['folder'];folder.mkdir(exist_ok=True)
    dest=folder/f'{group["number"]}.mp4';meta=work/f'{size}-{group["number"]}.json'
    paths=[work/'stamped'/f'{n}.mp4' for n in group['source_numbers']]
    fingerprint=''.join(sha(p) for p in paths)+str(group['duration'])+'concat-v1'
    info=None
    if dest.exists() and meta.exists():
        previous=json.loads(meta.read_text())
        if previous.get('fingerprint')==fingerprint and previous.get('sha256')==sha(dest):info=previous['verification']
    if info is None:
        listing=work/f'{size}-{group["number"]}.ffconcat'
        def quoted(path):return "'"+str(path).replace("'", "'\\''")+"'"
        listing.write_text('ffconcat version 1.0\n'+''.join(f'file {quoted(p)}\nduration {records[n]["duration"]:.6f}\n' for p,n in zip(paths,group['source_numbers'])))
        temp=dest.with_name(f'.{group["number"]}.{os.getpid()}.tmp.mp4')
        run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af','aresample=async=1:first_pts=0','-c:a','aac','-b:a','192k','-threads','2','-t',str(group['duration']),'-movflags','+faststart',str(temp)])
        r=records[group['source_numbers'][0]]
        info=verify(temp,group['frames'],group['duration'],(r['width'],r['height']),decode=True)
        temp.replace(dest);save(meta,{'fingerprint':fingerprint,'sha256':sha(dest),'verification':info})
    item=metadata(group,records,plan,cfg,size);item['sha256']=sha(dest);item['verification']={**info,'full_decode_passed':True}
    return item

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--locale',default='hindi');parser.add_argument('--workers',type=int,default=3);parser.add_argument('--stamp-only',action='store_true');parser.add_argument('--limit',type=int);args=parser.parse_args()
    base=ROOT/args.locale;work=base/'.local/video-delivery';plan=json.loads((work/'plan.json').read_text());cfg=json.loads((ROOT/'video-delivery-template/settings.json').read_text())
    png=work/'stamp-png/frame_000001.png';assert png.exists(),f'Render HyperFrames stamp first: {png}'
    records={r['number']:r for r in plan['sources']};sources=list(records.values())
    if args.limit:sources=sources[:args.limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(stamp_source,r,work,png) for r in sources]
        for i,f in enumerate(concurrent.futures.as_completed(futures),1):
            n,state=f.result();print(f'Stamp {i}/{len(sources)}: {n} ({state})',flush=True)
    if args.stamp_only:return
    if args.limit:raise SystemExit('--limit requires --stamp-only')
    for size,groups in plan['groups'].items():
        items=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures=[pool.submit(merge_group,size,g,records,work,base,cfg,plan) for g in groups]
            for i,f in enumerate(concurrent.futures.as_completed(futures),1):
                item=f.result();items.append(item);print(f'Merge {size} {i}/{len(groups)}: {item["file"]}',flush=True)
        items.sort(key=lambda item:int(Path(item['file']).stem))
        assert [n for item in items for n in item['source_video_numbers']]==list(records)
        assert len({item['title'] for item in items})==len(items)
        payload={'schema_version':1,'schema_status':'provisional_awaiting_uploader_example','locale':args.locale,'brand_name':cfg['brand_name_template'].format(language=plan['language']),'handle':cfg['handle_template'].format(language=plan['language']),'stamp':plan['stamp_text'],'size':size,'clips_per_video':cfg['outputs'][size]['clips_per_video'],'grouping':cfg['grouping'],'remainder':cfg['remainder'],'path_base':'same folder as content.json','video_count':len(items),'videos':items}
        save(base/cfg['outputs'][size]['folder']/'content.json',payload)
    save(work/'verification.json',{'status':'verified','source_count':len(records),'groups':{k:len(v) for k,v in plan['groups'].items()},'stamp':plan['stamp_text'],'source_files_preserved':True})
    print('All delivery groups rendered and decoded successfully.',flush=True)
if __name__=='__main__':main()
