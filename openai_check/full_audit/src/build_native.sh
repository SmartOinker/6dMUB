#!/usr/bin/env bash
set -euo pipefail
mkdir -p build
export LC_ALL=C
CXX=${CXX:-g++}
"$CXX" -O3 -march=native -ffp-contract=off upstream/abi-fp-probe.cpp -o build/abi-probe
./build/abi-probe
for pair in 'covout.cpp covrun' 'atlas.cpp arun' 'stageB.cpp brun' 'stageC.cpp crun'; do
 read -r src exe <<< "$pair"
 "$CXX" -std=gnu++17 -O3 -march=native -ffp-contract=off "upstream/$src" -o "build/$exe"
done
"$CXX" -std=gnu++17 -O2 -ffp-contract=off -fsanitize=undefined -fno-sanitize-recover=all src/graph_check.cpp -o build/graph_check
objdump -d -C build/covrun > build/covrun.disassembly.txt
nm -D build/covrun > build/covrun.dynamic-symbols.txt
