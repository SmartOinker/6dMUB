# Rebuild and partial rerun of the MUB-6 certificate programs

## Safety review
All 8 sources (abi-fp-probe, seed, covout, ub, patchx, atlas, stageB, stageC; `compiled-build/source/`) were read (probe, seed, covout, atlas, ub in full; patchx/stageB/stageC at all I/O and `main` sections plus grep over all of them). They only compute and do file I/O on the paths given in argv (fopen/fwrite/fread; stageB also `rename`s `<prefix>N.bin.tmp` -> `<prefix>N.bin`, both argv-derived). No system/popen/exec/socket/getenv/dlopen/threads. Only odd item: the probe uses inline asm `fnstcw` to read the x87 control word (read-only). The 7 mathematical sources have the same sha256 as `code/extraction.json` (all match; `rebuild.json`). Note: the sources are in `saved-run/compiled-build/source/`, not `code/` (which holds only extraction.json). Build used a copy in `/home/claude/oai_cert/rebuild/src`; nothing was written to the clone or base_exec.

## Environment
| item | paper | this machine |
|---|---|---|
| CPU | Xeon Platinum 8573C | "Intel Xeon Processor @ 2.30GHz" (virtualised, 2 vCPU; flags incl. avx512*, amx, fma, avx512_fp16 => Sapphire/Emerald-Rapids-class) |
| compiler | Ubuntu GCC 13.3.0 | g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| glibc | 2.39 | Ubuntu GLIBC 2.39-0ubuntu8.9 |
| OS | Ubuntu | Ubuntu 24.04.5 LTS |
So compiler, glibc and OS are (apparently) the same; the CPU is a different (but same-ISA-generation, probably near-identical) part. Machine load average 4-6 on 2 cores (shared), so wall times are inflated.

## Commands (all `LANG=C LC_ALL=C`, `nice -n 10`, one process at a time)
- Build: `/home/claude/mub6/src/openai_check/build_rebuild.sh <src> <out> native|x86-64` (flags exactly as build.sh: `g++ -O3 -march=$m -ffp-contract=off`, `-std=gnu++17` for arun/brun/crun). Probes passed in both builds. ~23 s each. Binary hashes in rebuild.json. No `call pow` and no FMA instructions in either covrun disassembly (full manual inspection of the two squares in `coverSeeds::run` was NOT done; absence of a pow call only shows they were lowered to something).
- covrun: `build_native/covrun centers.txt`
- A0: `build_native/arun centers.txt 0 4 coarse0.bin bad0.txt` (centers.txt = our regenerated file, bit-identical to saved)
- C: `build_{native,generic}/crun 12 4 1 .042 1 1 5000000 0 1 batches/badN.bin batches/fN.bin` for N=0,3 (saved f0.bin / f3.bin as input)
- Comparison: sha256 and `cmp_records.py`.

## Results
| stage | what was rerun | outcome | details |
|---|---|---|---|
| seed cover | full `covrun`, -march=native | bit-identical | centers.txt sha256 c48bc9a2...5748a5789 = saved = Table 2 value; 249,878 centers, 151,744,086 pairs checked; exit 0; 1160 s wall (load-inflated; program-reported 1160.25 s) |
| Stage A, shard 0 | full `arun` part 0 of 4, native | bit-identical | coarse0.bin sha256 77b0cda5...418cd4 = saved; 764 records; bad0.txt empty (e3b0c442...) = saved; exit 0; 62,470 balls; 2080 s |
| Stage C batch 0 | `crun` on f0.bin, native and x86-64 | bit-identical (both) | bad0.bin af5570f5...; exit 0; done256 bad0; 41 s |
| Stage C batch 3 | `crun` on f3.bin, native and x86-64 | bit-identical (both) | bad3.bin 9a959370... = saved (2 records); exit 1; done256 bad2 (cap2) as in saved log; 44-49 s |
| covrun / A0 with `-march=x86-64` | not run | not run | out of compute budget (~20 and ~35 min). Only crun was compared across variants |
| A shards 1-3, B mid/fine/fallback, other 87 C batches, final C | not run | not run | not run |
Differing records: none anywhere (so no max-difference figures). Record counts agree in every comparison.

Saved logs for A are in a reduced format (progress lines `done N Gm failedBalls0`, no timings), so log text was not compared bit-for-bit; our log lines for A0 had the same G counts format with an additional `coverFailures0+1` counter at 53000 (the saved log does not print that field, so nothing to compare; final result identical regardless).

## What this does and does not show
Under the same compiler/libc (GCC 13.3.0, glibc 2.39) on a different (virtual, probably same-generation) Xeon, the seed cover, one full Stage A shard (a quarter of Stage A) and two Stage C batches (one with unresolved/cap exits) reproduce the saved outputs byte-for-byte; for C the result also holds with a generic x86-64 build. This is mild evidence that the recorded outputs do not depend on FMA/AVX-512 code generation or on particular hardware, since no FMA was emitted and results were stable. It does NOT check the mathematics, the inequalities, or any stage not rerun (B and 3/4 of A, 86/88 batches, final C). The CPU is likely close to the paper's, so independence from hardware is weak; the compiler/libc are the same, so compiler-dependence is untested. It also cannot detect a systematic flaw that the code would reproduce faithfully on every machine.
