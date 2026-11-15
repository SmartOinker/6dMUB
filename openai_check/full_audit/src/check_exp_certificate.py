"""Exact rational validation of the source's transcendental error budgets.
This supplements, but does not replace, the stated IEEE primitive model.
"""
from fractions import Fraction as F
from pathlib import Path
import json,math
def A(x,n):return sum((-1)**j*x**(2*j+1)/F(2*j+1) for j in range(n))
p=F(884279719003555,281474976710656)
s=16*A(F(1,5),12)-4*A(F(1,239),4)
claimed=F(-1204334632739641172855772829555432415587,10003273510806667494906565283020800000000000000000000000)
assert p-s==claimed
tail=F(16,25*5**25)+F(4,9*239**9)
assert abs(p-s)+tail<F('1.225418e-16')
u=F('2e-16');alpha=(1+u)**9-1;rho=(1+u)**27-1
assert alpha<F('1.81e-15') and rho<F('5.5e-15')
y=F('.786');cos_tail=y**20/math.factorial(20);sin_tail=y**21/math.factorial(21)
assert cos_tail<F('3.330e-21') and sin_tail<F('1.247e-22')
cos_err=F('.4')*rho+F('1.4')*(1+rho)*alpha+F('4e-20')
sin_err=F('.2')*rho+(1+rho)*alpha+F('4e-20')
assert cos_err<F('4.74e-15') and sin_err<F('2.92e-15')
assert cos_err*cos_err+sin_err*sin_err<F('5.6e-15')**2
assert F('5.6e-15')+F('3e-16')+F('1e-295')<F('6e-15')
out={'result':'PASS','arithmetic':'fractions.Fraction exact','pi_difference_matches_published_fraction':True,'pi_error_upper':str(abs(p-s)+tail),'pi_error_bound':'1.225418e-16','cosine_tail_upper':str(cos_tail),'sine_tail_upper':str(sin_tail),'cosine_coordinate_error_bound':'4.74e-15','sine_coordinate_error_bound':'2.92e-15','combined_analytical_error_bound':'6e-15','source_asserted_exp_bound':'2e-14','scope':'Exact inequalities in the analytic expair proof, conditional on the source operation-count and correctly rounded primitive model.'}
Path('results/exp-certificate.json').write_text(json.dumps(out,indent=2)+'\n');print(out['result'])
