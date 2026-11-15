"""Groebner basis of cyclic-6-roots over GF(p) (sympy), to bound dim of quotient ring.
Rigorous use: dim_Q(Q[x]/I) <= dim_Fp(Fp[x]/I_p) (rank <= dim of reduction mod p)."""
import sys, time, itertools
from sympy import symbols, groebner, Poly, GF
p = int(sys.argv[1]) if len(sys.argv)>1 else 32003
method = sys.argv[2] if len(sys.argv)>2 else 'f5b'
z = symbols('z0:6')
def cyc(n=6):
    eqs=[]
    for m in range(1,n):
        eqs.append(sum(__import__('math').prod(z[(k+i)%n] for i in range(m)) for k in range(n)))
    eqs.append(__import__('math').prod(z)-1)
    return eqs
if __name__=='__main__':
    t=time.time()
    G = groebner(cyc(), *z, order='grevlex', modulus=p, method=method)
    print('time',time.time()-t, 'size',len(G.exprs))
    lms=[Poly(g,*z,modulus=p).monoms(order='grevlex')[0] for g in G.exprs]
    # count standard monomials
    n=6
    # bound degrees by max exponent
    mx=[max(m[i] for m in lms) for i in range(n)]
    print(lms)
    import pickle; pickle.dump(lms,open('lms_%d.pkl'%p,'wb'))
