#!/usr/bin/env bash
# Fetch the pinned OpenAI saved run (308 files, 82,505,759 bytes) with git instead of the GitHub API
# (use this where api.github.com is not reachable).  Run from openai_check/full_audit/.
# Afterwards every file is compared with the SHA-256 recorded in results/upstream-manifest.json.
set -euo pipefail
HEAD=4eaee87548250b2682affda7d05d947c05554bae
BASE="preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026"
TMP="$(mktemp -d)"
git clone --filter=blob:none --no-checkout https://github.com/openai/math "$TMP/math"
git -C "$TMP/math" sparse-checkout init --no-cone
git -C "$TMP/math" sparse-checkout set "/$BASE/verification/saved-run/"
git -C "$TMP/math" checkout "$HEAD"
mkdir -p upstream && rm -rf upstream/saved-run && cp -r "$TMP/math/$BASE/verification/saved-run" upstream/saved-run
python3 - <<'PY'
import json, hashlib, pathlib
root = pathlib.Path('upstream/saved-run'); m = json.load(open('results/upstream-manifest.json'))
bad = [f['path'] for f in m['files'] if hashlib.sha256((root / f['path']).read_bytes()).hexdigest() != f['sha256']]
print('upstream commit', m['commit'], '| files', len(m['files']), '| bytes', sum((root / f['path']).stat().st_size for f in m['files']), '| sha256 mismatches', len(bad))
raise SystemExit(1 if bad else 0)
PY
