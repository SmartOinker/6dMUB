#!/usr/bin/env python3
"""
Dimension 6: the pair {I, Fourier} and unimodular vectors with unimodular DFT.

Pipeline (see RESULTS.md for the honest status of each claim):
  1  numerical search (random-start least squares) for the 5 phases      [numerical]
  2  polish to ~90 digits + Krawczyk certification with python-flint arb  [certified]
  3  completeness via cyclic 6-roots (156 certified roots + upper bound)  [see completeness()]
  4  orthogonality graph, 6-cliques = bases                                [certified / numerically-zero]
  5  pairwise unbiasedness test of the 16 bases                           [certified]
  6  by-product for triples {I, Fourier, B_a}                              [certified + numerical optimisation]
Exit code 1 if an expected count (48 vectors, 16 bases, 0 MU pairs) fails.
"""
import sys, os, json, time, itertools, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import least_squares, minimize
from flint import arb, acb, ctx
import mubcore as mc
import cyclic6 as cy

OUT = '/home/claude/mub6/results/fourier'
SRC = os.path.dirname(os.path.abspath(__file__))
PREC = 320            # bits (~96 digits)
T0 = time.time()
R = {}                # everything that goes into results.json
FAIL = []

def log(*a):
    print('[%6.1fs]' % (time.time()-T0), *a, flush=True)

def s30(x):           # arb midpoint -> 30 digit string
    return x.mid().str(30, radius=False)

# =============================================================== 1. FIND
def find_solutions():
    rng = np.random.default_rng(20241114)
    sols = []; last_new = 0; n = 0
    while True:
        n += 1
        x = rng.uniform(0, 2*np.pi, 5)
        r = least_squares(mc.f_float, x, jac=mc.jac_float, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        if np.max(np.abs(r.fun)) < 1e-10:
            p = np.angle(np.exp(1j*r.x))
            if not any(np.max(np.abs(np.angle(np.exp(1j*(p-q))))) < 1e-6 for q in sols):
                sols.append(p); last_new = n
        # stop when no new solution during the last 2000 starts (and at least 4000 starts)
        if n >= 4000 and n - last_new >= 2000: break
        if n >= 40000: break
    return sols, n, last_new

# =============================================================== 2. CERTIFY
def certify(sols):
    ctx.prec = PREC
    ROW_CHOICES = [[1,2,3,4,5],[0,2,3,4,5],[0,1,3,4,5],[0,1,2,4,5],[0,1,2,3,5],[0,1,2,3,4]]
    RADII = ['1e-3', '1e-4', '1e-5', '1e-6', '1e-8']
    out = []
    for idx, p0 in enumerate(sols):
        done = False
        for rows in ROW_CHOICES:
            try:
                c = mc.newton_arb(list(p0), rows)
            except Exception:
                continue
            ok_big = None
            for rs in RADII:
                ok, _ = mc.krawczyk(c, rows, arb(rs))
                if ok: ok_big = rs; break
            if ok_big is None: continue
            # tight enclosure of the (unique) zero: tiny box inside the certified box
            ok2, K = mc.krawczyk(c, rows, arb('1e-40'))
            if not ok2: continue
            # 6th (dropped) equation: Parseval => f_dropped = -sum(others) exactly.
            f = mc.f_arb(c)
            dropped = [j for j in range(6) if j not in rows][0]
            fd_center = f[dropped]
            fd_box = mc.f_arb(K)[dropped]       # enclosure over the tight box (contains the true zero)
            out.append(dict(idx=idx, rows=rows, dropped=dropped, center=c, K=K,
                            radius=ok_big, tiny='1e-40',
                            f_dropped_center=fd_center, f_dropped_box=fd_box))
            done = True; break
        if not done:
            raise RuntimeError('could not certify solution %d' % idx)
    return out

def vec_acb(K):
    return [acb(1)] + [acb(0, x).exp() for x in K]

def ip(u, v):         # normalised inner product <u,v>/6 for unnormalised unimodular vectors
    s = acb(0)
    for a, b in zip(u, v):
        s += a.conjugate()*b
    return s/6

def abs2(z): return z.real**2 + z.imag**2

# =============================================================== 3. COMPLETENESS
def completeness(vecs_float_z):
    """Return dict describing the completeness argument and its status."""
    info = {}
    rng = np.random.default_rng(777)
    t = time.time()
    sols, starts = cy.find_all(rng)
    info['cyclic_roots_found_numerically'] = len(sols)
    info['cyclic_search_starts'] = starts
    if len(sols) != 156:
        info['status'] = 'FAILED: found %d roots' % len(sols); return info
    ctx.prec = PREC
    boxes = []
    for z in sols:
        zc = cy.newton_acb(z)
        ok, K = cy.krawczyk_c(zc, arb('1e-30'))
        if not ok:
            info['status'] = 'FAILED: complex Krawczyk'; return info
        boxes.append((zc, K))
    # disjointness of boxes (centres further than 2*sqrt2*r apart in sup norm)
    cent = np.array([[complex(float(z.real.mid()), float(z.imag.mid())) for z in zc] for zc, _ in boxes])
    dmin = min(np.max(np.abs(cent[i]-cent[j])) for i in range(156) for j in range(i))
    info['min_sup_distance_between_roots'] = float(dmin)
    info['all_156_certified_distinct'] = bool(dmin > 1e-25)
    # classify: |z_k| enclosure excludes 1 for some k  => certified non-unimodular
    nonuni = 0; maybe = []
    for i, (zc, K) in enumerate(boxes):
        bad = False
        for z in K:
            a = (z.real**2 + z.imag**2) - 1
            if not a.contains(0): bad = True
        if bad: nonuni += 1
        else: maybe.append(i)
    info['certified_non_unimodular_roots'] = nonuni
    info['roots_not_excluded_as_unimodular'] = len(maybe)
    # match with the 48 vectors (z_k = v_{k+1}/v_k)
    matched = set()
    for zv in vecs_float_z:
        hit = [i for i in range(156) if np.max(np.abs(cent[i]-zv)) < 1e-9]
        if len(hit) == 1: matched.add(hit[0])
    info['matched_with_48_vectors'] = len(matched)
    info['unmatched_not_excluded'] = len(set(maybe) - matched)
    info['roots_summary_consistent'] = (len(matched) == 48 and set(maybe) == matched)
    info['seconds_roots'] = time.time()-t
    return info

def upper_bound_156():
    """Upper bound on the number of isolated complex roots (all in the torus since prod z=1).
    Uses cached result of bound_cyclic6.py (see that file for the argument)."""
    p = os.path.join(OUT, 'bound_cyclic6.json')
    subprocess.run([sys.executable, os.path.join(SRC, 'bound_mv.py')], check=True, stdout=subprocess.DEVNULL)
    return json.load(open(p))

# =============================================================== 4. GRAPH / BASES
def bron_kerbosch(adj, n):
    res = []
    def bk(Rr, P, X):
        if not P and not X: res.append(sorted(Rr)); return
        piv = max(P | X, key=lambda u: len(adj[u] & P))
        for v in list(P - adj[piv]):
            bk(Rr | {v}, P & adj[v], X & adj[v]); P = P - {v}; X = X | {v}
    bk(set(), set(range(n)), set())
    return res

# =============================================================== 6(ii) optimisation
def triple_basis_matrix(Bfloat):
    """18 x 6 matrix whose rows are conj of unit vectors b (so overlap = rows @ v)."""
    I6 = np.eye(6)
    Fo = np.exp(2j*np.pi*np.outer(np.arange(6), np.arange(6))/6)/np.sqrt(6)
    rows = [I6[i].conj() for i in range(6)] + [Fo[:, j].conj() for j in range(6)] \
         + [b.conj()/np.sqrt(6) for b in Bfloat]
    return np.array(rows)

def resid(x, M):
    v = x[:6] + 1j*x[6:]
    v = v/np.linalg.norm(v)
    return np.abs(M @ v)**2 - 1/6

def best_unbiasedness(M, seed, nstarts=120):
    rng = np.random.default_rng(seed)
    cands = []
    for _ in range(nstarts):
        x0 = rng.normal(size=12)
        r = least_squares(resid, x0, args=(M,), xtol=1e-14, ftol=1e-14, gtol=1e-14)
        cands.append((np.max(np.abs(r.fun)), r.x))
    cands.sort(key=lambda t: t[0])
    starts = [c[1] for c in cands[:8]] + [rng.normal(size=12) for _ in range(12)]
    best = (cands[0][0], cands[0][1])
    for x0 in starts:
        x0 = x0/np.linalg.norm(x0)
        t0 = np.max(np.abs(resid(x0, M)))
        y0 = np.concatenate([x0, [t0]])
        cons = [{'type': 'ineq', 'fun': lambda y: y[12] - resid(y[:12], M)},
                {'type': 'ineq', 'fun': lambda y: y[12] + resid(y[:12], M)},
                {'type': 'eq', 'fun': lambda y: np.dot(y[:12], y[:12]) - 1}]
        try:
            res = minimize(lambda y: y[12], y0, constraints=cons, method='SLSQP',
                           options={'maxiter': 300, 'ftol': 1e-14})
            val = np.max(np.abs(resid(res.x[:12], M)))
            if val < best[0]: best = (val, res.x[:12])
        except Exception:
            pass
    return float(best[0]), best[1]

# =============================================================== MAIN
def main():
    # ---- 1
    sols, nstarts, last_new = find_solutions()
    R['task1'] = dict(n_solutions=len(sols), n_random_starts=nstarts, last_new_at_start=last_new,
                      rng_seed=20241114, status='numerical (not a proof)')
    log('found', len(sols), 'solutions; starts', nstarts, 'last new at', last_new)
    if len(sols) != 48: FAIL.append('number of vectors != 48')

    # ---- 2
    cert = certify(sols)
    R['task2'] = dict(precision_bits=PREC, krawczyk_box_radii_used=sorted(set(c['radius'] for c in cert)),
        tight_box_radius='1e-40', rows_used_counts={str(r): sum(1 for c in cert if str(c['rows']) == str(r))
            for r in sorted({str(c['rows']) for c in cert})},
        max_tight_enclosure_radius=max(float(max(k.rad() for k in c['K'])) for c in cert),
        max_abs_f_dropped_at_center=max(float(abs(c['f_dropped_center']).upper()) for c in cert),
        f_dropped_box_contains_zero_all=all(c['f_dropped_box'].contains(0) for c in cert),
        max_f_dropped_box_radius=max(float(c['f_dropped_box'].rad()) for c in cert),
        status='certified by interval arithmetic')
    log('certified', len(cert), 'radii', R['task2']['krawczyk_box_radii_used'])
    # disjointness of the Krawczyk boxes (mod 2 pi) -- distinctness of the 48
    ph = np.array([[float(k.mid()) for k in c['K']] for c in cert])
    dmin = min(np.max(np.abs(np.angle(np.exp(1j*(ph[i]-ph[j]))))) for i in range(48) for j in range(i)) if len(cert) > 1 else None
    R['task2']['min_sup_distance_between_solutions_mod_2pi'] = float(dmin)
    V = [vec_acb(c['K']) for c in cert]
    n = len(V)
    R['vectors_phases_p1_to_p5_30digits'] = [[s30(k) for k in c['K']] for c in cert]
    R['vectors_rows_used'] = [c['rows'] for c in cert]

    # ---- 3
    zs = []
    for c in cert:
        v = [1] + [np.exp(1j*float(k.mid())) for k in c['K']]
        zs.append(np.array([v[(k+1) % 6]/v[k] for k in range(6)]))
    comp = completeness(zs)
    ub = upper_bound_156()
    comp['upper_bound_certificate'] = ub
    # Verdict.  PROOF OUTLINE: (a) 156 pairwise distinct roots certified by complex Krawczyk;
    # (b) #isolated roots in the torus <= mixed volume (Bernstein-Kushnirenko) = 156 (qhull float volumes,
    # integrality checked); all roots lie in the torus since prod z_k = 1.  Hence these are ALL roots.
    # (c) exactly 48 of them are not excluded from |z_k|=1 and they are the 48 vectors found.
    comp['completeness_conclusion'] = bool(comp.get('all_156_certified_distinct') and ub['mixed_volume_rounded'] == 156
        and ub['integrality_error'] < 1e-6 and comp.get('roots_summary_consistent'))
    comp['completeness_caveat'] = ('depends on the mixed volume computed in floating point (qhull) being exactly 156; '
        'BKK theorem itself is standard. Not an exact-arithmetic proof.')
    if not comp['completeness_conclusion']: FAIL.append('completeness argument did not close')
    R['task3'] = comp
    log('completeness info', {k: v for k, v in comp.items() if k != 'upper_bound_certificate'})

    # ---- 4
    G = {}
    adj = [set() for _ in range(n)]
    nonzero_margin = 1e9; zero_max = 0.0
    for a in range(n):
        for b in range(a+1, n):
            z = ip(V[a], V[b])
            if z.real.contains(0) and z.imag.contains(0) and float(abs(z).upper()) < 1e-30:
                adj[a].add(b); adj[b].add(a); zero_max = max(zero_max, float(abs(z).upper()))
            else:
                lo = float(abs(z).lower())
                if lo <= 0: raise RuntimeError('undecided inner product %d %d' % (a, b))
                nonzero_margin = min(nonzero_margin, lo)
    cl = bron_kerbosch(adj, n)
    sizes = {}
    for c in cl: sizes[len(c)] = sizes.get(len(c), 0)+1
    bases = sorted([c for c in cl if len(c) == 6])
    cover = [sum(1 for B in bases if i in B) for i in range(n)]
    R['task4'] = dict(n_edges=sum(len(s) for s in adj)//2, maximal_clique_size_histogram={str(k): v for k, v in sorted(sizes.items())},
        n_bases=len(bases), bases=bases, orthogonal_pairs_max_abs_ip_upper_bound=zero_max,
        non_orthogonal_pairs_min_abs_ip_certified_lower_bound=nonzero_margin,
        vectors_per_basis_incidence_hist={str(k): cover.count(k) for k in sorted(set(cover))},
        bases_partition_the_48=bool(all(c == 1 for c in cover)),
        status='non-orthogonality certified; orthogonality = enclosure contains 0, |<u,v>|<1e-30 (exact zero NOT proved)')
    log('bases', len(bases), 'incidence', R['task4']['vectors_per_basis_incidence_hist'], 'clique sizes', sizes)
    if len(bases) != 16: FAIL.append('number of bases != 16')

    # ---- 5
    pairs = []; margin_min = None; cert_all = True; mu_pairs = 0
    for a, b in itertools.combinations(range(len(bases)), 2):
        best_mid = 0.0; best_lo = 0.0
        for i in bases[a]:
            for j in bases[b]:
                w = abs2(ip(V[i], V[j]))
                d = w - arb(1)/6
                dm = abs(d)
                best_mid = max(best_mid, float(dm.mid())); best_lo = max(best_lo, float(dm.lower()))
        if best_lo <= 0: cert_all = False; mu_pairs += 1
        pairs.append(dict(a=a, b=b, max_dev=best_mid, certified_lower_bound=best_lo))
    R['task5'] = dict(n_pairs=len(pairs), n_pairs_not_certified_non_MU=mu_pairs,
        smallest_max_deviation_over_pairs=min(p['max_dev'] for p in pairs),
        smallest_certified_lower_bound_over_pairs=min(p['certified_lower_bound'] for p in pairs),
        pairs=pairs, status='certified by interval arithmetic')
    log('pairs', len(pairs), 'MU pairs', mu_pairs, 'min dev', R['task5']['smallest_max_deviation_over_pairs'])
    if mu_pairs != 0 or len(pairs) != 120: FAIL.append('MU pairs != 0 (or pair count != 120)')

    # ---- 6
    t6 = []
    Vfl = [np.array([complex(float(z.real.mid()), float(z.imag.mid())) for z in v]) for v in V]
    for ai, B in enumerate(bases):
        mids = []; los = []
        for vi in range(n):
            if vi in B: continue
            devs = [abs(abs2(ip(V[b], V[vi])) - arb(1)/6) for b in B]
            mids.append(max(float(d.mid()) for d in devs)); los.append(max(float(d.lower()) for d in devs))
        M = triple_basis_matrix([Vfl[i] for i in B])
        val, x = best_unbiasedness(M, seed=1000+ai)
        t6.append(dict(basis=ai, n_other_vectors=len(mids), min_over_vectors_of_max_dev=min(mids),
                       certified_lower_bound_min=min(los), all_certified_biased=bool(min(los) > 0),
                       numerical_best_max_deviation_any_unit_vector=val))
        log('triple', ai, t6[-1])
    R['task6'] = dict(triples=t6,
        overall_smallest_numerical_best=min(t['numerical_best_max_deviation_any_unit_vector'] for t in t6),
        status_i='certified by interval arithmetic', status_ii='numerical optimisation (upper bound on true minimum; not a proof)')
    if not all(t['all_certified_biased'] for t in t6): FAIL.append('some other vector unbiased to a B_a')

    R['runtime_seconds'] = time.time()-T0
    R['failures'] = FAIL
    json.dump(R, open(os.path.join(OUT, 'results.json'), 'w'), indent=1, default=str)
    log('FAIL list:', FAIL)
    sys.exit(1 if FAIL else 0)

if __name__ == '__main__':
    main()
