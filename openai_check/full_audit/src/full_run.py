"""Fresh, conservative native execution of every stage. No saved centers used.
Run from the repository root. Writes command records immediately on completion.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib,json,os,struct,subprocess,time,threading
ROOT=Path(__file__).resolve().parent.parent
RUN=Path(os.environ.get('MUB6_FRESH_DIR',ROOT/'results/fresh')).resolve();RUN.mkdir(parents=True,exist_ok=True)
if (RUN/'commands.json').exists() or (RUN/'centers.txt').exists():raise SystemExit('Existing run; choose a fresh MUB6_FRESH_DIR')
(RUN/'batches').mkdir(exist_ok=True)
lock=threading.Lock();records={}
def count(path):
 b=Path(path).read_bytes();return struct.unpack('<Q',b[:8])[0]
def invoke(key,exe,args,allow=(0,)):
 cmd=[str(ROOT/'build'/exe),*map(str,args)]
 t=time.time()
 with (RUN/f'{key}.stdout').open('w') as out,(RUN/f'{key}.stderr').open('w') as err:
  p=subprocess.run(cmd,cwd=RUN,stdout=out,stderr=err,env={**os.environ,'LC_ALL':'C'})
 row={'command':cmd,'returncode':p.returncode,'started_utc':datetime.fromtimestamp(t,timezone.utc).isoformat(),'seconds':time.time()-t}
 with lock:
  records[key]=row;(RUN/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
 print(key,p.returncode,round(row['seconds'],2),flush=True)
 assert p.returncode in allow,(key,p.returncode)
 assert (RUN/f'{key}.stderr').stat().st_size==0,key
 return row
def main():
 invoke('cover','covrun',['centers.txt'])
 with ThreadPoolExecutor(max_workers=4) as pool:
  list(pool.map(lambda i:invoke(f'A{i}','arun',['centers.txt',i,4,f'coarse{i}.bin',f'A-bad{i}.txt']),range(4)))
 assert all((RUN/f'A-bad{i}.txt').stat().st_size==0 for i in range(4))
 invoke('Bmid','brun',['.07','.013','mid.bin','midbad.bin','-',*[f'coarse{i}.bin' for i in range(4)]])
 assert count(RUN/'midbad.bin')==0
 invoke('Bfine','brun',['.016','.005','fine.bin','finebad.bin','batches/f','mid.bin'])
 assert count(RUN/'finebad.bin')==0
 n,total=map(int,(RUN/'batches/fdone.txt').read_text().split())
 assert sum(count(RUN/f'batches/f{i}.bin') for i in range(n))==total==count(RUN/'fine.bin')
 with ThreadPoolExecutor(max_workers=8) as pool:
  list(pool.map(lambda i:invoke(f'C{i}','crun',['12','4','1','.042','1','1','5000000',0,1,f'batches/bad{i}.bin',f'batches/f{i}.bin'],allow=(0,1)),range(n)))
 bad=sorted(p for p in (RUN/'batches').glob('bad*.bin') if count(p)>0)
 if bad:
  invoke('Bfallback','brun',['.011','.0038','fb.bin','fbbad.bin','-',*[p.relative_to(RUN) for p in bad]])
  assert count(RUN/'fbbad.bin')==0
  with ThreadPoolExecutor(max_workers=4) as pool:
   list(pool.map(lambda i:invoke(f'Cfinal{i}','crun',['12','4','1','.042','1','1','5000000',i,4,f'finalbad{i}.bin','fb.bin']),range(4)))
  assert all(count(RUN/f'finalbad{i}.bin')==0 for i in range(4))
 output={'result':'complete native pipeline with zero final unresolved records','commands':len(records),'fine':total,'initial_bad':sum(count(p) for p in bad),'fallback':count(RUN/'fb.bin') if bad else 0,'files':{}}
 for p in sorted(RUN.rglob('*')):
  if p.is_file():output['files'][str(p.relative_to(RUN))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (RUN/'COMPLETE.json').write_text(json.dumps(output,indent=2)+'\n');print(output['result'],flush=True)
if __name__=='__main__':main()
