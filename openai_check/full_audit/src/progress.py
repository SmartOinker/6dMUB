from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent/'results/fresh'
if (R/'COMPLETE.json').exists():print((R/'COMPLETE.json').read_text());raise SystemExit
out={}
for p in sorted(R.glob('*.stdout')):
 lines=p.read_text().splitlines()
 if lines:out[p.stem]=lines[-1]
print(json.dumps(out,indent=2))
