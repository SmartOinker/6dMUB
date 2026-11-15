"""Own random-start search for vectors unbiased to I and the Fourier basis (batched Levenberg-Marquardt on phases).
Counts distinct solutions (x_0 = 1) and, for d = 10, compares with the certified list."""
import sys, time, numpy as np
from scipy.spatial import cKDTree
d = int(sys.argv[1]); nb = int(sys.argv[2]); B = int(sys.argv[3]); seed = int(sys.argv[4])
rng = np.random.default_rng(seed)
W = np.exp(-2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)          # W[k, j]
def resjac(th):                                                         # th: B x (d-1)
    x = np.concatenate([np.ones((th.shape[0],1)), np.exp(1j*th)], axis=1)   # B x d
    X = x @ W.T                                                         # B x d (index k)
    r = np.abs(X)**2 - d
    # d|X_k|^2/dth_m = -2 Im( conj(X_k) x_m W[k,m] )
    Jm = -2*np.imag(np.conj(X)[:, :, None] * x[:, None, 1:] * W[None, :, 1:])   # B x d x (d-1)
    return r, Jm
found = []; t0 = time.time(); conv = 0; total = 0
for b in range(nb):
    th = rng.uniform(0, 2*np.pi, size=(B, d-1)); lam = np.full(B, 1e-2)
    r, Jm = resjac(th); f = (r**2).sum(1)
    for it in range(400):
        A = np.einsum('bki,bkj->bij', Jm, Jm); g = np.einsum('bki,bk->bi', Jm, r)
        A = A + lam[:, None, None]*np.eye(d-1)[None]
        step = -np.linalg.solve(A, g[..., None])[..., 0]
        th2 = th + step; r2, J2 = resjac(th2); f2 = (r2**2).sum(1)
        acc = f2 < f
        th = np.where(acc[:, None], th2, th); r = np.where(acc[:, None], r2, r); Jm = np.where(acc[:, None, None], J2, Jm)
        f = np.where(acc, f2, f); lam = np.where(acc, lam*0.3, lam*4.0); lam = np.clip(lam, 1e-12, 1e8)
        if (f < 1e-22).mean() > 0.999: break
    good = f < 1e-18
    conv += int(good.sum()); total += B
    x = np.exp(1j*th[good]); found.append(x)
    print(f"batch {b+1}/{nb}: converged {int(good.sum())}/{B}  [{time.time()-t0:.0f}s]", flush=True)
x = np.concatenate(found); pts = np.concatenate([x.real, x.imag], axis=1)
# distinct solutions
order = np.lexsort(np.round(pts, 6).T[::-1]); pts = pts[order]
tree = cKDTree(pts); groups = tree.query_ball_point(pts, 1e-6)
rep = np.array([min(g) for g in groups]); distinct = np.unique(rep)
print(f"d={d}: {conv}/{total} starts converged; distinct solutions: {len(distinct)}")
counts = np.bincount(rep, minlength=len(pts))[distinct]
print("  hits per solution: min %d, median %d, max %d" % (counts.min(), np.median(counts), counts.max()))
if d == 10:
    L = np.load("/home/claude/work/d10/vecs.npy")[:, 1:]; Lp = np.concatenate([L.real, L.imag], axis=1)
    dist, idx = cKDTree(Lp).query(pts[distinct])
    print("  solutions not within 1e-6 of the certified list of 3,040:", int((dist > 1e-6).sum()), "; list members found:", len(np.unique(idx[dist <= 1e-6])), "of", len(Lp))
    print("  largest distance to the list among matches: %.1e" % dist[dist <= 1e-6].max())
