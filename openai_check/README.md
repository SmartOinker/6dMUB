# Independent re-run of the OpenAI MUB-6 record checker, mutation test and partial rebuild

Performed on 2026-11-15 as a second, independent run, by an AI agent that had not taken part in the first run.
Nothing from the OpenAI repository (sources, saved-run data, checker) is copied here; only the commit and paths are stated.

## What this is, and is not
It re-verifies the behaviour of the **bookkeeping checker** `check_records.py` published with the preprint, and shows that a partial rebuild of the published C++ programs reproduces three saved outputs bit for bit.
It does **not** verify the OpenAI proof, any floating-point inequality, the geometry or the mathematics (Sec. 2-6, App. A). The full 100-invocation native rerun is documented separately in `full_audit/` (logs, checkers, repeat-run log); it was not repeated in this partial rebuild. Stage A (all shards), Stage B, 86 of 88 initial C batches, the B fallback and the final C were not run.

## Upstream
- Repository: https://github.com/openai/math, pinned commit `4eaee87548250b2682affda7d05d947c05554bae` (`git rev-parse HEAD` printed exactly this after a blobless sparse clone and `git checkout` of the commit).
- Sparse path: `preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026/verification` (80 MB).
- Checker: `.../verification/saved-run/execution/check_records.py`, sha256 `565f4ee47ab7b7c4bf1c224981eb86ec94ef5f75a9487347a53af407eee45734`. It was unchanged after all runs.
- Local (not committed) copies: `/home/claude/oai_cert/base_exec` (saved-run `execution/`), `/home/claude/oai_cert/checker.py`.

## Environment
Python 3.13.18; g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0; glibc 2.39-0ubuntu8.9; x86_64.
CPU: Intel(R) Xeon(R) Processor @ 2.10GHz (virtualised, 2 vCPU, family 6 model 207 stepping 2; avx512f, fma, amx_tile, avx512_fp16). The paper used a Xeon Platinum 8573C.
The machine was shared (load average 4.8-6.4 on 2 cores), so wall times are inflated. Heavy commands were run under `nice -n 5`.

## Commands
```
mkdir -p /home/claude/oai_cert/clone && cd /home/claude/oai_cert/clone
git clone --filter=blob:none --sparse https://github.com/openai/math && cd math
git checkout 4eaee87548250b2682affda7d05d947c05554bae
git sparse-checkout set "preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026/verification"
cp -r <verification>/saved-run/execution /home/claude/oai_cert/base_exec
cp /home/claude/oai_cert/base_exec/check_records.py /home/claude/oai_cert/checker.py
cd /home
nice -n 5 python3 -I /home/claude/oai_cert/checker.py /home/claude/oai_cert/base_exec
nice -n 5 python3 -I mutate.py /home/claude/oai_cert/base_exec /home/claude/oai_cert/checker.py /home/claude/oai_cert/work mutations_rerun.json
# rebuild (sources = saved-run/compiled-build/source/*.cpp, copied to /home/claude/oai_cert/rerun/src)
bash build_rebuild.sh /home/claude/oai_cert/rerun/src /home/claude/oai_cert/rerun/out/native native
export LANG=C LC_ALL=C
nice -n 5 covrun centers.txt                                          # seed cover
nice -n 5 crun 12 4 1 .042 1 1 5000000 0 1 batches/badN.bin batches/fN.bin   # N = 0 and 3, inputs = saved fN.bin
```
The scripts are unchanged copies of the first run's versions (`mutate.py`, `cmp_records.py`, `build_rebuild.sh`). `cmp_records.py` was not needed, because sha256 values were identical.

## 1. Baseline
Unmodified checker on the unmodified saved run: **exit 0**, result "PASS within numerical consistency scope", wall 6.1 s (this loaded machine; 3.7 s earlier). The output reports 249,878 centres and 151,744,086 pairs; coarse records 764/774/757/788; mid 600; fine 22,379; 88 batches; initial C 163 bad (all cap).

## 2. Mutation test
`mutate.py` (read in full before running) hard-link-copies the base run once per mutant. It replaces exactly one or a few files in the copy with a new inode (the base is never modified), and applies one of 26 hand-written corruptions: deleted, duplicated, swapped or numerically perturbed records, edited centres, logs or `commands.json`, and a stray file. It then runs `python3 -I checker.py <copy>` as a subprocess and records exit code and message. It never writes to or imports the checker, makes no network calls, and deletes each copy afterwards. The checker sha256 and a re-run on the base run (exit 0) were checked afterwards.

**Result: 17 caught, 9 missed, identical to the earlier run.** All 26 verdicts agree. All 26 messages agree once the scratch path prefix is normalised (the work directory differs from the earlier one). Total harness wall time was 121 s.

| id | mutation | caught, earlier run | caught, this rerun | checker s |
|---|---|---|---|---|
| M01 | delete one record (header fixed) | yes | yes | 3.8 |
| M02 | delete one record (header NOT fixed) | yes | yes | 2.8 |
| M03 | duplicate one record (header fixed) | yes | yes | 6.0 |
| M04 | small numeric change to a phase p[0] in a record, one file only (fine.bin) | yes | yes | 3.1 |
| M05 | small numeric change to p[0] in coarse0.bin record (upstream, no consistency partner stored downstream) | no | no | 4.2 |
| M06 | same small change to a record applied consistently in fine.bin AND its batch copy | no | no | 5.5 |
| M07 | change a record inside a saved C-failure file | yes | yes | 3.4 |
| M08 | swap two records (fine.bin only) | yes | yes | 2.2 |
| M09 | swap two records consistently in fine.bin and batch f0.bin | no | no | 4.7 |
| M10 | truncate a record file | yes | yes | 1.6 |
| M11 | truncate the centers file (drop last row, count header kept) | yes | yes | 0.1 |
| M12 | remove a seed centre consistently (header decremented) - leaves a seed region uncovered | yes | yes | 1.8 |
| M13 | alter one coordinate of a seed centre (still in range) - shifts a seed cell | no | no | 5.1 |
| M14 | inflate a stored radius within the global cap (coarse0 rec -> 0.126) | no | no | 6.5 |
| M15 | radius over cap (fine.bin rec radius 0.0161 > .016) | yes | yes | 2.6 |
| M16 | weaken a stored bound within the checker's cap: Root residual froot -> 9e-7 (coarse0 rec) | no | no | 7.7 |
| M17 | stored bound beyond cap: orthogonality residual ort -> 1e-3 | yes | yes | 2.5 |
| M18 | forge verdict: C.batch3 failures hidden (bad file emptied, log, exit code all rewritten) | yes | yes | 6.2 |
| M19 | flip exit status in commands.json only (C.batch3 returncode 1 -> 0) | yes | yes | 4.9 |
| M20 | recategorise failures in log (cap2 -> cluster2) only | no | no | 6.2 |
| M21 | make a final-C failure file nonempty | yes | yes | 7.2 |
| M22 | delete last fb1 record, consistently forging logs (fallback B + final C part 2) | no | no | 9.4 |
| M23 | delete coarse0 record, A0 log edited consistently (G764->G763) - downstream B parent count unchanged | yes | yes | 3.0 |
| M24 | extra stray file in data/ | yes | yes | 7.8 |
| M25 | phase value out of declared bound |p|<=4 (set p[3]=5 in mid.bin rec) | yes | yes | 3.2 |
| M26 | single bit flip in low mantissa bit of a p entry (mid.bin rec 50 p[3]) | no | no | 7.8 |
Missed (9): M05, M06, M09, M13, M14, M16, M20, M22, M26. Some of these are harmless by design (M09 swap, M20 relabel, M26 one-ulp flip). The rest (M05, M06, M13, M14, M16, M22) are value-level, geometric or consistently forged edits that the checker cannot see, in line with its own docstring: "derived checker, not the original audit". Exact messages and before/after values are in `mutations_rerun.json`; interpretations of each survivor are in the earlier NOTES.md.

## 3. Partial rebuild
Sources: 7 mathematical sources match sha256 in `verification/code/extraction.json`. The 8th (`abi-fp-probe.cpp`) has no entry there. A grep found no system/popen/exec/socket/getenv/dlopen/thread/fork. Build: `build_rebuild.sh native`, flags `g++ -O3 -march=native -ffp-contract=off` (`-std=gnu++17` for arun/brun/crun). Both ABI/FP probes passed. The `covrun` disassembly has 0 `call pow` lines and 0 FMA instructions; the two squares in `coverSeeds::run` were not inspected by hand.
Native binary hashes differ from the earlier rebuild's (different CPU model/clock and build path), but the outputs below are identical (see `rebuild_rerun.json`).

| stage rerun | exit (saved) | wall | saved sha256 (prefix) | rerun | match |
|---|---|---|---|---|---|
| seed cover, `covrun centers.txt` | 0 (0) | 1298.9 s | c48bc9a2be1e... | same | bit-identical; 249,878 centres, 151,744,086 pairs checked |
| Stage C batch 0 (`f0.bin`) | 0 (0) | 176.9 s | af5570f5a181... | same | bit-identical; `done256 bad0` |
| Stage C batch 3 (`f3.bin`) | 1 (1) | 259.6 s | 9a9593704f38... | same | bit-identical; `done256 bad2 (cap2)` |

The seed cover `centers.txt` value `c48bc9a2...5748a5789` equals the earlier note's Table 2 value. The paper itself was not re-opened in this run.
Not rerun (time box): `covrun`/A with `-march=x86-64`, all Stage A shards, Stage B, 86 other C batches, B fallback, final C.

## Interpretation
Same compiler and libc, a different (virtualised, same-generation) CPU: the saved checker input is consistent with the published sources for the three stages rerun. Hardware independence is weakly tested, because the CPU is similar and no FMA was emitted. It cannot detect a systematic flaw that the code reproduces faithfully, and it does not check the mathematical argument.

## Lean scope of the OpenAI repository (read, not rebuilt; added 2026-11-15)

For the report's paragraph "Verified versus headline" two files of `openai/math` were read at the pinned revision
`4eaee87548250b2682affda7d05d947c05554bae` (fetched from raw.githubusercontent.com; not redistributed here):

| file | sha256 of the file as fetched |
|---|---|
| `lean/docs/266.md` (scope note) | `3141714e25026b26a4028e27ee001e70295310bad4290b5a8f7c9fd546e8a174` |
| `lean/ComparatorChallenges/MUBSix.lean` (statement file) | `7a634ee492b54abe357901a69272c42aa8dfc85b7a3401eef723468bb0c6c355` |
| `lean/lean-toolchain` (`leanprover/lean4:v4.34.1`) | `d5edba4e4b8faad9c1baeadb265716d20d03be4d1a2647dc5e35b0c0325bea7b` |

What was read: the scope note says the formalization proves a family bound of five and a Fourier character-sum
vanishing statement, and that it does not establish the upper bound of three. The statement file defines
`IsMUBFamily`, `Attainable n` and states `fourier_and_family_bound`, whose second part is
`∀ n : ℕ, Attainable n → n ≤ 5`; in that file the proof is `sorry` (it is the challenge statement). The proof
directory (`lean/OAI/Analysis/MutuallyUnbiased`) was NOT fetched, built or audited by us. Nothing here verifies the
OpenAI Lean development.
