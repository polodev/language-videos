"""Run the installed imagegen CLI using a key loaded privately from the requested env file."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
CLI=Path.home()/'.codex/skills/.system/imagegen/scripts/image_gen.py'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--asset',choices=['logo','facebook-cover'],required=True);args=parser.parse_args()
    spec_path=ROOT/'channel informations/assets/hindi/image-prompts.json'
    spec=json.loads(spec_path.read_text());asset=next(a for a in spec['assets'] if a['key']==args.asset)
    key=dotenv_values(Path.home()/'sites/phrase/.env').get('OPENAI_API_KEY')
    if not key:raise SystemExit('OPENAI_API_KEY is missing from the requested local env file.')
    env=os.environ.copy();env['OPENAI_API_KEY']=key;env.pop('OPENAI_BASE_URL',None)
    out=ROOT/asset['output'];out.parent.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(CLI),'edit' if 'reference' in asset else 'generate','--model',spec['model'],'--quality',spec['quality'],'--size',asset['size'],'--prompt-file',str(spec_path.parent/(args.asset+'-prompt.txt')),'--no-augment','--out',str(out)]
    if 'reference' in asset:command+=['--image',str(out.parent/asset['reference'])]
    process=subprocess.run(command,env=env,capture_output=True,text=True)
    # Never propagate the secret into logs, including error output.
    message=(process.stdout+'\n'+process.stderr).replace(key,'[REDACTED]')
    print(message.strip(),flush=True)
    raise SystemExit(process.returncode)
if __name__=='__main__':main()
