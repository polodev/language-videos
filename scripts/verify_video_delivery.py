"""Verify compilation ordering against encoded source packets; refresh metadata."""
import argparse, concurrent.futures, json
from pathlib import Path
from render_video_delivery import ROOT, run, sha, save, metadata, export_delivery

def packet_hashes(path):
    data=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=flags,data_hash','-of','json',str(path)]))
    # Concat may add SPS/PPS to keyframes. All other packets must match byte for byte.
    return [p['data_hash'] for p in data['packets'] if 'K' not in p['flags']]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--locale',default='hindi');args=parser.parse_args()
    base=ROOT/args.locale;work=base/'.local/video-delivery'
    plan=json.loads((work/'plan.json').read_text());cfg=json.loads((ROOT/'video-delivery-template/settings.json').read_text())
    records={r['number']:r for r in plan['sources']}
    def source(r):
        path=work/'stamped'/f'{r["number"]}.mp4';side=json.loads(path.with_suffix('.json').read_text())
        assert sha(ROOT/r['path'])==side['source_sha256'],f'Source changed: {r["number"]}'
        assert sha(path)==side['sha256'],f'Stamped file changed: {r["number"]}'
        return r['number'],packet_hashes(path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:hashes=dict(pool.map(source,records.values()))
    report=[]
    for size,groups in plan['groups'].items():
        folder=base/cfg['outputs'][size]['folder'];content=json.loads((work/f'{size}-content-manifest.json').read_text())
        assert content['video_count']==len(groups)
        old={int(Path(v['file']).stem):v for v in content['videos']}
        def check(group):
            item=old[group['number']];path=folder/item['file']
            assert path.is_file() and sha(path)==item['sha256']
            expected=[h for n in group['source_numbers'] for h in hashes[n]]
            assert packet_hashes(path)==expected,f'Wrong packet order: {path}'
            assert item['source_video_numbers']==group['source_numbers']
            assert item['verification']['full_decode_passed']
            updated=metadata(group,records,plan,cfg,size)
            updated['sha256']=item['sha256'];updated['verification']={**item['verification'],'non_keyframe_packets_match_sources_in_order':True,'source_files_unchanged':True}
            return updated
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:items=list(pool.map(check,groups))
        assert sum(x['sentence_count'] for x in items)==sum(len(r['lesson']['sentences']) for r in records.values())
        assert [n for x in items for n in x['source_video_numbers']]==list(records)
        assert len(set(x['title'] for x in items))==len(items)
        assert all(x['project_title'] and len(x['title'])<=100 and len(x['description'])<=5000 for x in items)
        assert {p.name for p in folder.iterdir() if p.suffix=='.mp4'}=={x['file'] for x in items}
        content['videos']=items;export_delivery(folder,work,size,content)
        report.append({'size':size,'count':len(items),'packet_order_verified':True,'source_files_unchanged':True,'full_decode_passed':True,'total_duration_seconds':sum(x['duration_seconds'] for x in items)})
        print(f'Verified {size}: {len(items)} outputs; refreshed public titles and project_title.',flush=True)
    save(work/'verification.json',{'status':'verified','locale':args.locale,'source_count':len(records),'stamp':plan['stamp_text'],'groups':report,'upload_schema_status':'numbered_project_title_title_content'})
if __name__=='__main__':main()
