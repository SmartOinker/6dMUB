#!/bin/bash
# Re-run of the Brierley-Weigert (2008) Table 4: every shape {5,a,b,c}, a>=b>=c>=1, plus {5,5,5}.
# For each shape: N random starts; counts of (i) strict convergence (misfit < 1e-11) and
# (ii) the 2008 criterion F < 1e-7.
N=${1:-2000}; OUT=${2:-../../results/constellations/table}; P=${3:-2}
mkdir -p "$OUT"
for a in 1 2 3 4 5; do for b in $(seq 1 $a); do for c in $(seq 1 $b); do echo "$a $b $c"; done; done; done > "$OUT/shapes.txt"
echo "5 5" >> "$OUT/shapes.txt"
cat "$OUT/shapes.txt" | xargs -P "$P" -I{} bash -c 'g="{}"; python3 search.py --groups $g --starts '"$N"' --seed 2026 --keep 3 --out '"$OUT"'/t_$(echo $g|tr -d " ").jsonl 2>/dev/null'
