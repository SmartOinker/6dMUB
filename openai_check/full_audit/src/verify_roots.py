"""Independent Arb certificate for the serialized Root inequalities.

Reconstructs an inverse-like map from residual/Jacobian data; no source M
or numerical eigensolver output is assumed correct. Every norm certificate
uses ball arithmetic and a checked change-of-basis defect.
"""
from pathlib import Path
import sys,struct,json,hashlib,time,argparse
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'build/flint'))
import flint
from flint import arb,arb_mat,ctx
R=Path(__file__).resolve().parent.parent
ctx.prec=128
pi=arb.pi()
I=arb_mat(np.eye(36,dtype=int).tolist())
Pi=arb_mat(36,36,[arb(int(i==j))-arb(int(i//6==j//6))/6-arb(int(i%6==j%6))/6+arb(1)/36 for i in range(36) for j in range(36)])
edges=[(i,j) for i in range(6) for j in range(i) for _ in range(2)]
sgn=[[int(a==c)-int(a==d)-int(b==c)+int(b==d) for c,d in edges] for a,b in edges]
def upper(x):
 assert x.is_finite()
 return x.upper()
def frob(A):return upper(sum(upper(abs(x))**2 for x in A.entries()).sqrt())
def norm_from_gram(G):
 n=G.nrows();mid=np.array([float(x.mid()) for x in G.entries()]).reshape(n,n)
 _,q=np.linalg.eigh(mid);Q=arb_mat(q.tolist());one=arb_mat(np.eye(n,dtype=int).tolist())
 beta=frob(Q.transpose()*Q-one)
 assert beta<arb('0.01'),beta
 B=Q.transpose()*G*Q
 row=max(sum(upper(abs(B[i,j])) for j in range(n)) for i in range(n))
 return upper((row/(1-beta)).sqrt())
def records(path):
 b=path.read_bytes();n=struct.unpack_from('<Q',b)[0];off=8
 for ix in range(n):
  start=off;k=struct.unpack_from('<i',b,off)[0];off+=4
  v=struct.unpack_from('<'+'d'*(44+36*k),b,off);off+=8*(44+36*k)
  yield b[start:off],ix,k,v
 assert off==len(b)
def certify(k,v,transposed=False):
 p=v[:36];tv=list(v[36:36+36*k])
 if transposed:
  order=[6*j+i for i in range(6) for j in range(6)]
  p=[p[j] for j in order];tv=[tv[36*a+j] for a in range(k) for j in order]
 T=arb_mat(k,36,tv);C,n0,ident,ort,hor,mnorm,froot,r=v[-8:]
 H=[(2*pi*arb(x)).sin_cos() for x in p] # (sin, cos)
 L=[[arb(0) for _ in range(36)] for _ in range(30)];F2=arb(0);a=0
 for i in range(6):
  for j in range(i):
   sr=arb(0);si=arb(0)
   for g in range(6):
    sy,cy=H[6*i+g];sz,cz=H[6*j+g]
    re=cy*cz+sy*sz;im=sy*cz-cy*sz;sr+=re;si+=im
    L[a][6*i+g]=re;L[a][6*j+g]=-re
    L[a+1][6*i+g]=im;L[a+1][6*j+g]=-im
   F2+=sr*sr+si*si;a+=2
 f=upper(F2.sqrt()/(2*pi));assert f<=arb(froot),('froot',f,froot)
 if k:
  assert frob(T*T.transpose()-arb_mat(np.eye(k,dtype=int).tolist()))<=arb(ort),'ort'
  assert frob(T*(I-Pi))<=arb(hor),'hor'
 TT=T.transpose()*T
 J=arb_mat(L)
 PT=Pi*T.transpose()*(T*Pi*T.transpose()).inv()*T*Pi if k else arb_mat(36,36)
 QN=Pi-PT
 M=(QN*J.transpose()*J*QN+PT+I-Pi).inv()*QN*J.transpose()
 G=M.transpose()*M;mn=norm_from_gram(G)
 assert mn<=arb(mnorm),('mnorm',mn,mnorm)
 assert mn*f<=arb(n0),('n0',mn*f,n0)
 defect=frob(Pi-TT-M*J*Pi)
 assert defect<=arb(ident),('id',defect,ident)
 SG=arb_mat(30,30,[G[i,j]*sgn[i][j] for i in range(30) for j in range(30)])
 sn=norm_from_gram(SG)
 c=upper(pi*min(upper(arb(8).sqrt()*mn),upper(arb(6).sqrt()*sn)))
 assert c<=arb(C),('C',c,C)
 return [float(f),float(defect),float(mn),float(c)]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=0);args=parser.parse_args()
 files=[R/'upstream/saved-run/execution/data'/n for n in ['coarse0.bin','coarse1.bin','coarse2.bin','coarse3.bin','mid.bin','fine.bin','fb1.bin']]
 seen=set();checked=0;read=0;transposes=0;t=time.time()
 for path in files:
  for b,ix,k,v in records(path):
   read+=1;digest=hashlib.sha256(b[:-8]).digest() # Root identity independent of radius
   if digest in seen:continue
   try:
    try: vals=certify(k,v)
    except AssertionError:
     vals=certify(k,v,True);transposes+=1
   except Exception:
    print("FAILED",path.name,ix,k,flush=True);raise
   seen.add(digest);checked+=1
   if checked%100==0:print(checked,path.name,ix,round(time.time()-t,2),flush=True)
   if args.limit and checked>=args.limit:break
  if args.limit and checked>=args.limit:break
 out={'result':'PASS','scope':'All Root inequalities certified with a separately reconstructed inverse-like map and Arb enclosures' if not args.limit else 'bounded pilot only','precision_bits':ctx.prec,'python_flint':flint.__version__,'records_read':read,'unique_roots_checked':checked,'transposed_orientation_certificates':transposes,'seconds':time.time()-t,'files':[str(x.relative_to(R)) for x in files]}
 (R/'results'/('roots-pilot.json' if args.limit else 'roots-certified.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
