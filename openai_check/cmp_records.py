#!/usr/bin/env python3 -I
"""Compare two record files (.bin) written by saveRecords: sha256, record counts, differing records, max abs diff.
Record layout: u64 count; per record: i32 k, 36 f64 p, k*36 f64 T (T[k][36]), 8 f64 values."""
import struct, sys, hashlib
def h(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def parse(p):
    b=open(p,'rb').read(); n=struct.unpack_from('<Q',b,0)[0]; o=8; recs=[]
    for _ in range(n):
        k=struct.unpack_from('<i',b,o)[0]; o+=4
        m=36+36*k+8
        # note: assumes no padding; sizeof(r.T[0]) is 36 doubles (checked by total length)
        recs.append(struct.unpack_from('<%dd'%m,b,o)); o+=8*m
    assert o==len(b),(o,len(b)); return recs
a,b=sys.argv[1],sys.argv[2]
ha,hb=h(a),h(b); print(a,ha); print(b,hb); print('SHA256', 'IDENTICAL' if ha==hb else 'DIFFERENT')
if ha!=hb:
    try:
        A,B=parse(a),parse(b); print('counts',len(A),len(B))
        nd=0;mx=0
        for x,y in zip(A,B):
            if x!=y:
                nd+=1
                if len(x)==len(y): mx=max(mx,max(abs(u-v) for u,v in zip(x,y)))
        print('differing records',nd,'max abs diff',mx)
    except Exception as e: print('parse failed',e)
