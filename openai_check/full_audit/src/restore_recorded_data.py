"""Restore the recorded data from byte-identical pinned reference files.

This restores exact recorded bytes; it does not rerun the native computation.
Run fetch_upstream.py first if the downloaded reference data are unavailable.
Existing files with unexpected bytes are never overwritten.
"""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parent.parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=json.loads((ROOT/'results/recorded-package-manifest.json').read_text())
    reference=json.loads((ROOT/'results/upstream-manifest.json').read_text())
    sources={}
    for item in reference['files']:
        sources.setdefault(item['sha256'],[]).append(ROOT/'upstream/saved-run'/item['path'])
    wanted={name:record for name,record in manifest.items()
            if name.startswith(('results/fresh/','results/replay/'))
            and (name.endswith('.bin') or name.endswith('/centers.txt'))}
    assert len(wanted)==285
    copied=0;verified_sources=set()
    for name,record in wanted.items():
        target=ROOT/name
        expected=record['sha256']
        if target.exists():
            if target.stat().st_size!=record['bytes'] or digest(target)!=expected:
                raise SystemExit('Existing recorded data differ; refusing to overwrite: '+name)
            continue
        candidates=sources.get(expected,[])
        source=next((p for p in candidates if p.is_file()),None)
        if source is None:
            raise SystemExit('Reference data missing. Run python3 src/fetch_upstream.py first.')
        if source not in verified_sources:
            if source.stat().st_size!=record['bytes'] or digest(source)!=expected:
                raise SystemExit('Reference hash mismatch: '+str(source))
            verified_sources.add(source)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        if digest(target)!=expected:raise SystemExit('Restored data hash mismatch: '+name)
        copied+=1
    print(json.dumps({'result':'PASS','data_files_checked':len(wanted),
                      'data_files_restored':copied,
                      'scope':'Exact SHA-256 restoration of previously recorded bytes; no new native execution.'},indent=2))

if __name__=='__main__':main()
