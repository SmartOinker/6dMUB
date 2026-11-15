#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

# Prefer the task-local installation when present; otherwise use pinned elan.
if [[ -x lean-4.35.0-darwin_aarch64/bin/lake ]]; then
  export PATH="$PWD/lean-4.35.0-darwin_aarch64/bin:$PATH"
fi
export MATHLIB_CACHE_DIR="$PWD/mathlib-cache"
mkdir -p logs

case "$(lean --version)" in
  *"version 4.35.0,"*) ;;
  *) printf '%s\n' 'Expected Lean 4.35.0.' >&2; exit 1 ;;
esac
if [[ ! -d .lake/packages/mathlib ]]; then
  lake update > logs/setup.log 2>&1
fi
test "$(git -C .lake/packages/mathlib rev-parse HEAD)" = \
  56a005855ea17e0b0958f73ec801ae140b0a1679
if grep -En '\b(sorry|admit|native_decide)\b|^[[:space:]]*axiom[[:space:]]' MUB*.lean; then
  printf '%s\n' 'Forbidden proof placeholder or extra axiom found.' >&2
  exit 1
fi
{
  date -u '+UTC check time: %Y-%m-%dT%H:%M:%SZ'
  lean --version
  lake --version
  printf 'Mathlib commit: '
  git -C .lake/packages/mathlib rev-parse HEAD
} > logs/environment.txt
lake build > logs/build-final.log 2>&1
# The unchanged forty-five-module baseline is hash pinned and rebuilt above.
# Directly re-elaborate the new actual Fourier and C2 frame obstruction module.
for module in MUBNormalizerObstructions; do
  lake env lean "$module.lean" > "logs/direct-$module.log" 2>&1
done
python3 audit_inventory.py prepare
lake env lean AuditAll.lean > logs/axioms-all.log 2>&1
python3 check_portability.py
python3 audit_inventory.py verify
printf '%s\n' 'PASS: forty-six-module build, one new direct check, and every-theorem axiom audit completed.'
