from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,os,struct,json,time,threading
R=Path(__file__).resolve().parent.parent;D=R/'upstream/saved-run/execution/data';O=Path(os.environ.get('MUB6_REPLAY_DIR',R/'results/replay')).resolve();O.mkdir(parents=True,exist_ok=True)
if (O/'commands.json').exists():raise SystemExit('Existing run; choose a fresh MUB6_REPLAY_DIR')
rows={};lock=threading.Lock()
def count(p):return struct.unpack('<Q',p.read_bytes()[:8])[0]
def run(key,exe,args,allowed=(0,)):
 t=time.time();cmd=[str(R/'build'/exe),*map(str,args)]
 with (O/(key+'.stdout')).open('w') as out,(O/(key+'.stderr')).open('w') as err:p=subprocess.run(cmd,stdout=out,stderr=err,env={**os.environ,'LC_ALL':'C'})
 with lock:
  rows[key]={'command':cmd,'returncode':p.returncode,'seconds':time.time()-t};(O/'commands.json').write_text(json.dumps(rows,indent=2))
 assert p.returncode in allowed,(key,p.returncode)
 assert (O/(key+'.stderr')).stat().st_size==0
 print(key,p.returncode,flush=True)
N,total=map(int,(D/'batches/fdone.txt').read_text().split())
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda i:run('C'+str(i),'crun',['12','4','1','.042','1','1','5000000','0','1',O/('bad'+str(i)+'.bin'),D/('batches/f'+str(i)+'.bin')],(0,1)),range(N)))
bad=sorted(p for p in O.glob('bad*.bin') if count(p)>0)
if bad:
 run('Bfallback','brun',['.011','.0038',O/'fb.bin',O/'fbbad.bin','-',*bad]);assert count(O/'fbbad.bin')==0
 with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda i:run('Final'+str(i),'crun',['12','4','1','.042','1','1','5000000',i,4,O/('finalbad'+str(i)+'.bin'),O/'fb.bin']),range(4)))
 assert all(count(O/('finalbad'+str(i)+'.bin'))==0 for i in range(4))
result={'result':'PASS: all fine records resolved by fresh Stage C and actual-failure fallback','fine_records':total,'batches':N,'initial_unresolved':sum(count(p) for p in bad),'fallback_records':count(O/'fb.bin') if bad else 0,'final_unresolved':0,'invocations':len(rows)}
(O/'COMPLETE.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
