from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
ROOT=Path(__file__).resolve().parent.parent
BASE='preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026'
def get(url):
 return urllib.request.urlopen(url,timeout=120).read()
head='4eaee87548250b2682affda7d05d947c05554bae'  # Immutable audited revision
url=f'https://api.github.com/repos/openai/math/contents/{BASE}/verification/saved-run?ref={head}'
listing=json.loads(get(url))
# Git tree for the exact saved-run directory.
parent=json.loads(get(f'https://api.github.com/repos/openai/math/contents/{BASE}/verification?ref={head}'))
sha=next(x['sha'] for x in parent if x['name']=='saved-run')
tree=json.loads(get(f'https://api.github.com/repos/openai/math/git/trees/{sha}?recursive=1'))
assert not tree.get('truncated')
entries=[x for x in tree['tree'] if x['type']=='blob']
out=ROOT/'upstream/saved-run';out.mkdir(parents=True,exist_ok=True)
def fetch(x):
 path=out/x['path'];path.parent.mkdir(parents=True,exist_ok=True)
 b=get(f'https://raw.githubusercontent.com/openai/math/{head}/{BASE}/verification/saved-run/'+x['path'])
 blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 assert blob==x['sha'],x['path']
 path.write_bytes(b)
 return {'path':x['path'],'git_blob':blob,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 records=list(pool.map(fetch,entries))
(ROOT/'results/upstream-manifest.json').write_text(json.dumps({'repository':'openai/math','commit':head,'saved_run_tree':sha,'files':records},indent=2)+'\n')
print(json.dumps({'commit':head,'files':len(records),'bytes':sum(x['bytes'] for x in records)},indent=2),flush=True)
# Read all sections, without depending on source text extraction from PDF.
sections=json.loads(get(f'https://api.github.com/repos/openai/math/contents/{BASE}/build/sections?ref={head}'))
for x in sections:
 if x['name'].endswith('.tex'):
  (ROOT/'upstream'/x['name']).write_bytes(get(x['download_url']))
(ROOT/'upstream/paper.pdf').write_bytes(get(f'https://raw.githubusercontent.com/openai/math/{head}/{BASE}/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026.pdf'))
print('manuscript downloaded',flush=True)
