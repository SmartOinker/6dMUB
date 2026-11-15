"""Shared helpers: game value formulas, MUB constructions, unitary parametrisation + gradients.
Conventions: a basis is a d x d unitary whose COLUMNS are the basis vectors."""
import numpy as np
from itertools import combinations

OUT = "/home/claude/mub6/results/visibility"
P_MUB_D6 = 0.704124            # cited MUB value 1/2+1/(2 sqrt6)

def pair_sum_abs(A, B):
    return np.abs(A.conj().T @ B).sum()

def P_pair(A, B):
    d = A.shape[0]
    return 0.5 + pair_sum_abs(A, B) / (2 * d * d)

def P_n(Bs):
    pr = list(combinations(range(len(Bs)), 2))
    return np.mean([P_pair(Bs[a], Bs[b]) for a, b in pr])

def pairs_P(Bs):
    return [P_pair(Bs[a], Bs[b]) for a, b in combinations(range(len(Bs)), 2)]

def D2_pair(A, B):
    d = A.shape[0]
    m2 = np.abs(A.conj().T @ B) ** 2
    return 1 - ((m2 - 1 / d) ** 2).sum() / (d - 1)

def D2_n(Bs):
    return np.mean([D2_pair(Bs[a], Bs[b]) for a, b in combinations(range(len(Bs)), 2)])

def P_bound(d):
    return 0.5 + 0.5 / np.sqrt(d)

# ---------- MUB constructions ----------
def mubs_prime(d):
    """Complete set of d+1 MUBs for prime d (columns = vectors)."""
    w = np.exp(2j * np.pi / d)
    k = np.arange(d)
    out = [np.eye(d, dtype=complex)]
    for a in range(d):
        B = np.array([w ** ((a * k * k + b * k) % d) for b in range(d)]).T / np.sqrt(d)
        out.append(B)
    return out

def mubs_d6():
    """3 MUBs in C^6 = C^2 (x) C^3: (Z (x) Z3), (X (x) F3_1), (Y (x) F3_2)."""
    q = [np.eye(2, dtype=complex),
         np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
         np.array([[1, 1], [1j, -1j]], dtype=complex) / np.sqrt(2)]
    t = mubs_prime(3)           # computational + 3 others
    return [np.kron(q[i], t[i]) for i in range(3)]

def is_unitary(U, tol=1e-12):
    return np.abs(U.conj().T @ U - np.eye(U.shape[0])).max() < tol

# ---------- unitary parametrisation  U = expm(i H), H hermitian ----------
def make_index(d):
    iu = np.triu_indices(d, 1)
    return iu, d + 2 * len(iu[0])        # params per unitary: d diag + n re + n im

def H_from_x(x, d):
    iu, npar = make_index(d)
    n = len(iu[0])
    H = np.zeros((d, d), complex)
    H[np.diag_indices(d)] = x[:d]
    H[iu] = x[d:d + n] + 1j * x[d + n:]
    H = H + np.triu(H, 1).conj().T
    return H

def unitary_and_cache(x, d):
    H = H_from_x(x, d)
    lam, V = np.linalg.eigh(H)
    U = (V * np.exp(1j * lam)) @ V.conj().T
    return U, (lam, V)

def grad_x_from_G(G, cache, d):
    """G = d f/d conj(U) (steepest-ascent direction convention, df = 2 Re tr(G^dag dU)).
    Returns df/dx for the real parameter vector x of H."""
    lam, V = cache
    dl = lam[:, None] - lam[None, :]
    Phi = np.exp(0.5j * (lam[:, None] + lam[None, :])) * np.sinc(dl / (2 * np.pi))
    K = V.conj().T @ G @ V
    Q = K * Phi.conj()
    S = V @ Q @ V.conj().T
    Z = S.conj()
    iu, _ = make_index(d)
    gd = -2 * np.imag(np.diag(Z))
    gre = -2 * np.imag(Z[iu] + Z.T[iu])
    gim = 2 * np.real(Z.T[iu] - Z[iu])
    return np.concatenate([gd, gre, gim])

def x_from_unitary(U, d):
    lam, V = np.linalg.eig(U)
    # U normal: use Schur for stability
    from scipy.linalg import schur
    T, Z = schur(U, output='complex')
    th = np.angle(np.diag(T))
    H = (Z * th) @ Z.conj().T
    H = (H + H.conj().T) / 2
    iu, _ = make_index(d)
    return np.concatenate([np.real(np.diag(H)), np.real(H[iu]), np.imag(H[iu])])

def haar(d, rng):
    Z = (rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))) / np.sqrt(2)
    Q, R = np.linalg.qr(Z)
    return Q * (np.diag(R) / np.abs(np.diag(R)))

# ---------- objectives (maximised); first basis fixed to identity ----------
def obj_and_G(Bs, kind, delta):
    """Returns f and list G_k = df/dconj(B_k).  kind 'P': f=mean_pairs sum smooth|m|; 'D': f=-mean_pairs sum (|m|^2-1/d)^2."""
    n = len(Bs); d = Bs[0].shape[0]
    prs = list(combinations(range(n), 2)); npr = len(prs)
    G = [np.zeros((d, d), complex) for _ in range(n)]
    f = 0.0
    for a, b in prs:
        A, B = Bs[a], Bs[b]
        m = A.conj().T @ B
        if kind == 'P':
            r = np.sqrt(np.abs(m) ** 2 + delta ** 2)
            f += r.sum() / npr
            W = m / r
            G[b] += 0.5 * A @ W / npr
            G[a] += 0.5 * B @ W.conj().T / npr
        else:
            c = np.abs(m) ** 2 - 1.0 / d
            f -= (c ** 2).sum() / npr
            G[b] += -2 * A @ (c * m) / npr
            G[a] += -2 * B @ (c * m.conj()).T / npr
    return f, G

def make_fg(d, n, kind, delta):
    npar = make_index(d)[1]
    def fg(x):
        Bs = [np.eye(d, dtype=complex)]; caches = [None]
        for k in range(n - 1):
            U, c = unitary_and_cache(x[k * npar:(k + 1) * npar], d)
            Bs.append(U); caches.append(c)
        f, G = obj_and_G(Bs, kind, delta)
        g = np.concatenate([grad_x_from_G(G[k], caches[k], d) for k in range(1, n)])
        return -f, -g
    return fg

def bases_from_x(x, d, n):
    npar = make_index(d)[1]
    return [np.eye(d, dtype=complex)] + [unitary_and_cache(x[k * npar:(k + 1) * npar], d)[0] for k in range(n - 1)]
