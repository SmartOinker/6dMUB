"""Second product triple of McNulty-Weigert (third basis uses two different qutrit bases) and thresholds."""
import numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(2)
w = np.exp(2j*np.pi/3)
H2 = np.array([[1,1],[1,-1]])/np.sqrt(2)
A = [np.eye(2), H2, np.diag([1,1j])@H2]
F = np.array([[w**(j*k) for k in range(3)] for j in range(3)])/np.sqrt(3)
D = np.diag([1,w,w])
B = [np.eye(3), F, D@F, D@D@F]
for a in range(4):
    for b in range(a+1,4):
        assert np.allclose(abs(B[a].conj().T@B[b])**2, 1/3)
U0 = np.kron(A[0],B[0]); U1 = np.kron(A[1],B[1])
U2a = np.kron(A[2],B[2])
U2b = np.column_stack([np.kron(A[2][:,0],B[2][:,k]) for k in range(3)] + [np.kron(A[2][:,1],B[3][:,k]) for k in range(3)])
def run(Us, name):
    for r in range(3):
        assert np.allclose(Us[r].conj().T@Us[r], np.eye(6))
        for s in range(r+1,3):
            assert np.allclose(abs(Us[r].conj().T@Us[s])**2, 1/6), (name, r, s)
    def E(x):
        psi = x[:6]+1j*x[6:]; psi = psi/np.linalg.norm(psi)
        return sum(((abs(U.conj().T@psi)**2-1/6)**2).sum() for U in Us)
    vals = np.array([minimize(E, rng.normal(size=12), method="BFGS", options={"gtol":1e-12}).fun for _ in range(300)])
    print(name, "min E =", vals.min(), "; distinct minima:", np.unique(np.round(vals,6))[:6])
run([U0,U1,U2a], "T0 (canonical, Xinrui's)")
run([U0,U1,U2b], "T1 (third basis |0_y>B2, |1_y>B3)")
c = 3*np.sqrt(6)/(np.sqrt(6)+1)**2
print("c =", c, "(21*sqrt6-36)/25 =", (21*np.sqrt(6)-36)/25)
for nm, g in [("1/72 proved", 1/72), ("deg-6 SOS numeric 0.0383", 0.0383), ("conjectured sharp", (4-np.sqrt(6))/40)]:
    print(f"{nm}: single-outcome bias > {np.sqrt(g/18):.4f}; game deficit > {c*g/72:.3e}; 5-sigma shots for bias = {25*(1/6)*(5/6)/(g/18):.0f}; H2 sum deficit bits > {np.log2(1+6*g):.4f}")
print("E needed to beat delta=0.030224:", 18*0.030224**2, "; E needed to beat game gap 2.358e-4:", 2.358e-4*72/c)
mu=0.5+0.5/np.sqrt(6)
for d in (1.191e-4, 2.358e-4):
    print("rounds at 3 sigma for gap", d, ":", 9*mu*(1-mu)/d**2)
