"""Bernstein-Kushnirenko bound for cyclic 6-roots: number of isolated roots in (C*)^6 <= mixed volume
of the Newton polytopes.  (All roots have prod z = 1, hence lie in the torus.)
MV = sum_{S nonempty} (-1)^{6-|S|} Vol_6(sum_{i in S} P_i),   Vol = Euclidean volume.
Volumes via qhull (floating point); each should be a multiple of 1/720, and the final MV an
integer -- both checked.  This is floating-point hull volume, NOT an exact computation."""
import itertools, json, sys, time
import numpy as np
from scipy.spatial import ConvexHull
N = 6
polys = []
for m in range(1, N):
    pts = []
    for k in range(N):
        v = np.zeros(N, int)
        for i in range(m): v[(k+i) % N] = 1
        pts.append(v)
    polys.append(np.array(pts))
polys.append(np.array([np.zeros(N, int), np.ones(N, int)]))

def minkowski(A, B):
    S = {tuple(a+b) for a in A for b in B}
    return np.array(sorted(S))

def hull_vertices_only(P):
    # prune interior points with qhull (keeps sums small)
    if len(P) <= N or np.linalg.matrix_rank(P[1:]-P[0]) < N: return P
    h = ConvexHull(P.astype(float))
    return P[h.vertices]

if __name__ == '__main__':
    t = time.time()
    total = 0.0; vols = {}
    for r in range(1, N+1):
        for S in itertools.combinations(range(N), r):
            P = polys[S[0]]
            for i in S[1:]:
                P = hull_vertices_only(minkowski(P, polys[i]))
            if np.linalg.matrix_rank(P[1:]-P[0]) < N:
                vol = 0.0
            else:
                vol = ConvexHull(P.astype(float)).volume
            vols[S] = vol
            total += (-1)**(N-r)*vol
        print('size', r, 'done', time.time()-t, flush=True)
    print('MV =', total)
    res = dict(mixed_volume_float=total, mixed_volume_rounded=int(round(total)),
               integrality_error=abs(total-round(total)),
               max_volume_times_720_rounding_error=max(abs(v*720-round(v*720)) for v in vols.values()),
               method='qhull floating point volumes, inclusion-exclusion', seconds=time.time()-t)
    json.dump(res, open('/home/claude/mub6/results/fourier/bound_cyclic6.json', 'w'), indent=1)
    print(res)
