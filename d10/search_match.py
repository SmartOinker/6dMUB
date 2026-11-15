"""Large random-start search at d = 10; every converged end point is matched directly against the certified list."""
import sys, time, numpy as np
from scipy.spatial import cKDTree
d = 10; nb = int(sys.argv[1]); B = 20000; seed = int(sys.argv[2])
rng = np.random.default_rng(seed)
W = np.exp(-2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)
def resjac(th):
    x = np.concatenate([np.ones((th.shape[0],1)), np.exp(1j*th)], axis=1); X = x @ W.T
    return np.abs(X)**2 - d, -2*np.imag(np.conj(X)[:, :, None] * x[:, None, 1:] * W[None, :, 1:])
L = np.load("/home/claude/work/d10/vecs.npy")[:, 1:]; tree = cKDTree(np.concatenate([L.real, L.imag], axis=1))
hits = np.zeros(len(L), int); conv = 0; total = 0; unmatched = 0; worst = 0.0; t0 = time.time()
for b in range(nb):
    th = rng.uniform(0, 2*np.pi, size=(B, d-1)); lam = np.full(B, 1e-2)
    r, Jm = resjac(th); f = (r**2).sum(1)
    for it in range(400):
        A = np.einsum('bki,bkj->bij', Jm, Jm) + lam[:, None, None]*np.eye(d-1)[None]
        step = -np.linalg.solve(A, np.einsum('bki,bk->bi', Jm, r)[..., None])[..., 0]
        r2, J2 = resjac(th + step); f2 = (r2**2).sum(1); acc = f2 < f
        th = np.where(acc[:, None], th + step, th); r = np.where(acc[:, None], r2, r); Jm = np.where(acc[:, None, None], J2, Jm)
        f = np.where(acc, f2, f); lam = np.clip(np.where(acc, lam*0.3, lam*4.0), 1e-12, 1e8)
        if (f < 1e-22).mean() > 0.999: break
    good = f < 1e-18; x = np.exp(1j*th[good]); dist, idx = tree.query(np.concatenate([x.real, x.imag], axis=1))
    ok = dist < 1e-6; unmatched += int((~ok).sum()); worst = max(worst, float(dist[ok].max())); np.add.at(hits, idx[ok], 1)
    conv += int(good.sum()); total += B
print(f"starts {total}, converged {conv}, end points not on the certified list: {unmatched}, list members hit: {(hits>0).sum()}/3040, "
      f"min hits {hits.min()}, median {int(np.median(hits))}, max {hits.max()}, worst match distance {worst:.1e}, {time.time()-t0:.0f}s")
