import os; HERE = os.path.dirname(os.path.abspath(__file__)) + os.sep   # data files live next to this script
import numpy as np, json, time, sys
from flint import arb, acb, ctx
ctx.prec = 80
V=np.load(HERE+'vecs.npy'); B=json.load(open(HERE+'bases.json'))
P2=np.abs(V.conj()@V.T)**2
pairs=set()
for b in B:
    D=np.abs(P2[b,:]-10); am=D.argmax(axis=0)
    for v in range(len(V)): pairs.add((b[am[v]], v))
print('distinct (u,v) pairs', len(pairs), flush=True)
rad=arb(0, 1e-15)
A=[[acb(arb(float(z.real))+rad, arb(float(z.imag))+rad) for z in row] for row in V]
Ac=[[c.conjugate() for c in row] for row in A]
t=time.time(); lo=arb(100); n=0
ten=arb(10)
for (u,v) in pairs:
    ip=sum((Ac[u][k]*A[v][k] for k in range(10)), acb(0))
    dfc=abs(abs(ip)**2-ten)
    if dfc.lower() < lo.lower(): lo=arb(dfc.lower())
    n+=1
    if n%500000==0: print(n, time.time()-t, lo, flush=True)
print('certified lower bound on margin:', lo.str(10), 'time', time.time()-t)
