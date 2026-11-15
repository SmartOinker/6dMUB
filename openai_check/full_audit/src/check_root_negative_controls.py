"""Check that independently verified Roots reject deliberate corruption."""
import json
import verify_roots as V

path=V.R/'upstream/saved-run/execution/data/coarse0.bin'
_,ix,k,v=next(V.records(path))
V.certify(k,v)
cases={}
w=list(v);w[0]+=1/16;cases['phase_residual_corruption']=w
assert k>0
w=list(v);w[36:36+36*k]=[2*x for x in w[36:36+36*k]]
cases['tangent_gram_corruption']=w
for name,offset in [('zero_C',-8),('zero_n0',-7),('zero_id',-6),('zero_mnorm',-3),('zero_froot',-2)]:
 w=list(v);assert w[offset]>0;w[offset]=0;cases[name]=w
for name,w in cases.items():
 for transpose in [False,True]:
  try:V.certify(k,w,transpose)
  except AssertionError:pass
  else:raise AssertionError(('corruption accepted',name,transpose))
out={'result':'PASS','valid_control':'coarse0.bin record 0','corruptions_rejected_in_both_orientations':list(cases),'scope':'Rejection controls; these do not replace the full certificate check.'}
(V.R/'results/root-negative-controls.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
