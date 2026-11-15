"""Exact algebraic checks; symbolic equalities have no floating tolerance."""
import sympy as S,json,math
from pathlib import Path
R=Path(__file__).resolve().parent.parent
I=S.I;w=-S.Rational(1,2)+I*S.sqrt(3)/2
A=[S.eye(2),S.Matrix([[1,1],[1,-1]]),S.Matrix([[1,1],[I,-I]])]
B=[S.eye(3),S.Matrix(3,3,lambda j,k:S.expand(w**((j*k)%3))),None]
B[2]=S.diag(1,w,w)*B[1]
U=[S.kronecker_product(a,b) for a,b in zip(A,B)];sc=[1,6,6]
checks=0
for r in range(3):
 for s in range(3):
  G=U[r].conjugate().T*U[s]
  for j in range(6):
   for k in range(6):
    if r==s:assert S.simplify(G[j,k]-(sc[r] if j==k else 0))==0
    else:assert S.simplify(G[j,k]*S.conjugate(G[j,k])-S.Rational(sc[r]*sc[s],6))==0
    checks+=1
# The sharp witness uses three +alpha and three -alpha displacements.
a=S.symbols('a',real=True)
z=S.Matrix([a,a,a,-a,-a,-a]);assert sum(z)==0 and (z.T*z)[0]==6*a*a
sstar=math.sqrt(6)/(4*math.pi)*math.acos(1/math.sqrt(6))
# Elementary rational comparison gives a convenient radius 1/5.
lower=6-8*S.Rational(22,7)**2*S.Rational(1,5)**2
assert lower==S.Rational(3478,1225) and lower>S.Rational(5,2)
# Dot-product accumulation estimate: n*u/(1-n*u) <= 1.05*n*u for n<=2001.
u=S.Rational(2,10**16);n=2001;assert n*u/(1-n*u)<S.Rational(21,10)*S.Rational(1,10**16)*n
uvar=S.symbols('u',positive=True)
derivative=(S.sin(S.sqrt(uvar))-S.sqrt(uvar)*S.cos(S.sqrt(uvar)))/(4*uvar**S.Rational(3,2))
assert S.simplify(S.diff(S.cos(S.sqrt(uvar)),uvar,2)-derivative)==0
assert S.limit(derivative,uvar,0)==S.Rational(1,12)
assert S.simplify((3*S.exp(I*a)+3*S.exp(-I*a))/6-S.cos(a))==0
out={'result':'PASS','arithmetic':'SymPy exact Q(i,sqrt(3))','sympy_version':S.__version__,'ordered_gram_checks':checks,'unscaled_overlap_bound_s_one_fifth':str(lower),'sharp_phase_radius_expression':'sqrt(6)/(4*pi)*acos(1/sqrt(6))','sharp_phase_radius_display_only':sstar,'sharpness_witness':'x=(alpha,alpha,alpha,-alpha,-alpha,-alpha)/(4*pi), y=-x, alpha=acos(1/sqrt(6))','accumulation_bound_exact_rational_check':True,'sharp_radius_derivative_and_witness_identities':True}
(R/'results/exact-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
