#!/usr/bin/env bash
# usage: build_rebuild.sh <srcdir> <outdir> <march>   (march = native | x86-64)
set -euo pipefail
src=$1; out=$2; m=$3
mkdir -p "$out"; export LANG=C LC_ALL=C; cd "$src"
G="nice -n 10 g++"
$G -O3 -march=$m -ffp-contract=off abi-fp-probe.cpp -o $out/abi-fp-probe-covrun; $out/abi-fp-probe-covrun
$G -std=gnu++17 -O3 -march=$m -ffp-contract=off abi-fp-probe.cpp -o $out/abi-fp-probe-abc; $out/abi-fp-probe-abc
$G -O3 -march=$m -ffp-contract=off covout.cpp -o $out/covrun
for p in "atlas arun" "stageB brun" "stageC crun"; do set -- $p; $G -std=gnu++17 -O3 -march=$m -ffp-contract=off $1.cpp -o $out/$2; done
nm -D $out/covrun > $out/covrun.dynamic-symbols.txt
objdump -d -C $out/covrun > $out/covrun.disassembly.txt
