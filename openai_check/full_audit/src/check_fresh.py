"""Independent bookkeeping check of the newly generated complete pipeline."""
from pathlib import Path
import struct,re,json,math,hashlib
R=Path(__file__).resolve().parent.parent;F=R/'results/fresh'
def recs(p):
 b=p.read_bytes();assert len(b)>=8,p;n=struct.unpack_from('<Q',b)[0];assert n<=2000000
 off=8;out=[]
 for ix in range(n):
  start=off;k=struct.unpack_from('<i',b,off)[0];off+=4;assert 0<=k<=10
  m=44+36*k;v=struct.unpack_from('<'+'d'*m,b,off);off+=8*m
  assert all(math.isfinite(x) for x in v)
  assert all(abs(x)<=4 for x in v[:36]) and all(abs(x)<=1.01 for x in v[36:-8])
  C,n0,ident,ort,hor,mnorm,froot,r=v[-8:]
  assert 0<=C<20 and 0<=n0<1e-6 and 0<=froot<1e-6 and 0<=ident<1e-4
  assert 0<=ort<1e-5 and 0<=hor<1e-5 and 0<=mnorm<2 and 0<=r<=.126
  out.append(b[start:off])
 assert off==len(b),p
 return out
def stdout(key):return (F/(key+'.stdout')).read_text()
def cstage(key,inputn,bad):
 q=re.search(r'result done(\d+) bad(\d+) \(graph(\d+) cap(\d+) over(\d+) cluster(\d+)\)',stdout(key));assert q,key
 d,b,*cats=map(int,q.groups());assert d==inputn and b==len(bad) and sum(cats)==b,key
 assert commands[key]['returncode']==int(b>0),key
 return b
def ordered_subseq(bad,whole):
 i=0
 for r in whole:
  if i<len(bad) and bad[i]==r:i+=1
 assert i==len(bad)
def bstage(key,output,bad,parentn):
 q=re.search(r'result (\d+) bad (\d+) time [\d.]+ parent(\d+)',stdout(key));assert q,key
 n,b,p=map(int,q.groups());assert n==len(output) and b==len(bad)==0 and p==parentn,key
 assert commands[key]['returncode']==0
commands=json.loads((F/'commands.json').read_text());assert (F/'COMPLETE.json').exists(),'pipeline not complete'
lines=(F/'centers.txt').read_text().splitlines();grid,n=map(int,lines[0].split());assert grid==112 and n==len(lines)-1
for line in lines[1:]:
 vals=list(map(int,line.split()));assert len(vals)==10 and 0<=vals[5]<5
 assert all(0<=x<112 for i,x in enumerate(vals) if i!=5)
coarse=[]
for i in range(4):
 a=recs(F/f'coarse{i}.bin');coarse.extend(a)
 assert commands[f'A{i}']['command'][1:]==['centers.txt',str(i),'4',f'coarse{i}.bin',f'A-bad{i}.txt']
 q=re.search(r'total done(\d+).*global(\d+) failedBalls(\d+)',stdout(f'A{i}'));assert q
 done,g,bad=map(int,q.groups());assert done==(n-i+3)//4 and g==len(a) and bad==0
 assert (F/f'A-bad{i}.txt').read_bytes()==b'' and commands[f'A{i}']['returncode']==0
mid=recs(F/'mid.bin');fine=recs(F/'fine.bin')
bstage('Bmid',mid,recs(F/'midbad.bin'),len(coarse));bstage('Bfine',fine,recs(F/'finebad.bin'),len(mid))
assert commands['Bmid']['command'][1:]==['.07','.013','mid.bin','midbad.bin','-',*[f'coarse{i}.bin' for i in range(4)]]
assert commands['Bfine']['command'][1:]==['.016','.005','fine.bin','finebad.bin','batches/f','mid.bin']
nb,total=map(int,(F/'batches/fdone.txt').read_text().split());assert total==len(fine)
whole=[];failpaths=[];initial_bad=0
for j in range(nb):
 inp=recs(F/f'batches/f{j}.bin');bad=recs(F/f'batches/bad{j}.bin');assert 0<len(inp)<=256
 whole.extend(inp);ordered_subseq(bad,inp);initial_bad+=cstage(f'C{j}',len(inp),bad)
 assert commands[f'C{j}']['command'][1:]==['12','4','1','.042','1','1','5000000','0','1',f'batches/bad{j}.bin',f'batches/f{j}.bin']
 if bad:failpaths.append(f'batches/bad{j}.bin')
assert len(whole)==len(fine)
for enlarged,original in zip(whole,fine):
 assert enlarged[:-8]==original[:-8]
 assert struct.unpack('<d',enlarged[-8:])[0]==.016>=struct.unpack('<d',original[-8:])[0]
expected={'cover',*[f'A{i}' for i in range(4)],'Bmid','Bfine',*[f'C{j}' for j in range(nb)]}
fb=[]
if initial_bad:
 fb=recs(F/'fb.bin');bstage('Bfallback',fb,recs(F/'fbbad.bin'),initial_bad)
 expected.add('Bfallback')
 assert commands['Bfallback']['command'][1:6]==['.011','.0038','fb.bin','fbbad.bin','-']
 actual=commands['Bfallback']['command'][6:]
 assert actual==sorted(failpaths),(actual,sorted(failpaths))
 for i in range(4):
  bad=recs(F/f'finalbad{i}.bin');assert not bad
  cstage(f'Cfinal{i}',(len(fb)-i+3)//4,bad);expected.add(f'Cfinal{i}')
  assert commands[f'Cfinal{i}']['command'][1:]==['12','4','1','.042','1','1','5000000',str(i),'4',f'finalbad{i}.bin','fb.bin']
assert set(commands)==expected
assert commands['cover']['returncode']==0 and commands['cover']['command'][1:]==['centers.txt']
for key in commands:assert (F/(key+'.stderr')).read_bytes()==b''
comparisons={}
for name in ['centers.txt','coarse0.bin','coarse1.bin','coarse2.bin','coarse3.bin','mid.bin','fine.bin']+(['fb.bin'] if fb else []):
 comparisons[name]=hashlib.sha256((F/name).read_bytes()).hexdigest()==hashlib.sha256((R/'upstream/saved-run/execution/data'/('fb1.bin' if name=='fb.bin' else name)).read_bytes()).hexdigest()
out={'result':'PASS','children':len(commands),'centers':n,'coarse':len(coarse),'mid':len(mid),'fine':len(fine),'batches':nb,'initial_unresolved':initial_bad,'fallback':len(fb),'final_unresolved':0,'principal_files_match_released_sha256':comparisons,'scope':'Complete new-run parsing, stage counts, batch-root identity/radius enlargement, ordered failures, actual fallback operands and final modulo partition.'}
(R/'results/fresh-checked.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
