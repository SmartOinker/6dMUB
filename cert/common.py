"""Shared conventions: 12 real variables x (psi = x[:6] + i x[6:]), cubic monomial basis order."""
import itertools
n = 12
def monos(d):
    out = []
    for c in itertools.combinations_with_replacement(range(n), d):
        e = [0] * n
        for i in c:
            e[i] += 1
        out.append(tuple(e))
    return out
def fact(k):
    return [1, 1, 2, 6][k]
def mult3(a):          # coefficient of x^(2a) in N^3 = (sum x_i^2)^3, |a| = 3
    r = 6
    for k in a:
        r //= fact(k)
    return r
