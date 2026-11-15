#!/usr/bin/env python3
"""Heuristic search: which saved records lie near the Fourier matrix F6 (up to the Haagerup invariant)?
Assumption (checked empirically, NOT documented in VERIFY.md): p[36] are the 6x6 entry phases in TURNS
(H_jk = exp(2*pi*i*p[6j+k])).  For F6 every Haagerup product H_ij H_kl conj(H_il) conj(H_kj) is a 6th root
of unity, so the max distance (in turns) of these phase combinations from multiples of 1/6 measures closeness.
This is invariant under rephasing and row/col permutations, so it finds F6 'up to equivalence' - but also other
matrices whose products are all 6th roots (e.g. special members of other families).  Heuristic only.
usage: fourier_cell.py DATA_DIR
"""
import struct, sys, itertools
from pathlib import Path
D = Path(sys.argv[1])
def recs(path):
    d = path.read_bytes(); n = struct.unpack("<Q", d[:8])[0]; off = 8
    for i in range(n):
        k = struct.unpack("<i", d[off:off+4])[0]
        p = struct.unpack("<36d", d[off+4:off+4+288])
        sc = struct.unpack("<8d", d[off+4+288+288*k: off+4+288+288*k+64])
        off += 356 + 288*k
        yield i, k, p, sc
quads = [(i,k,j,l) for i,k in itertools.combinations(range(6),2) for j,l in itertools.combinations(range(6),2)]
def dev(p):
    m = 0.0
    for i,k,j,l in quads:
        t = p[6*i+j]+p[6*k+l]-p[6*i+l]-p[6*k+j]
        x = (t*6) % 1.0; x = min(x, 1-x)/6
        m = max(m, x)
    return m
for name in ["coarse0","coarse1","coarse2","coarse3","mid","fine","fb1"]:
    res = sorted((dev(p), i, k, sc[7]) for i,k,p,sc in recs(D/f"{name}.bin"))
    print(name, "n=%d"%len(res), "best 5 (maxdev turns, idx, rootdim k, radius):", [(round(a,4), i, k, round(r,4)) for a,i,k,r in res[:5]])
    print("   count with maxdev<0.02:", sum(1 for a,*_ in res if a<0.02), " <0.05:", sum(1 for a,*_ in res if a<0.05))
