# Check of the OpenAI MUB-6 preprint's saved run (read-only; nothing in the repo copy was modified)

## (i) Extracted facts (preprint "The maximum number of mutually unbiased bases in dimension six", 24 Sep 2026; repo openai/math)
- **Thm 1.1 (Computer-assisted):** "Under the arithmetic and compiler conditions in Appendix A, the fresh complete execution documented in Section 7.5 certifies that there are no four pairwise MUBs in C^6. Consequently N(6)=3." (3 bases: Lemma 1.2.) Conclusion in Sec. 8 via **Thm 7.1** (finite-execution certificate): seven specified sources + Appendix A arithmetic + all terminal conditions of Sec. 7.2 => no 4 MUBs.
- **Conditions (App. A.1, Sec. 7.1):** IEEE binary64, round-to-nearest, correctly rounded + - * / sqrt, FLT_EVAL_METHOD=0, `-ffp-contract=off`, no fast-math/reassociation, gradual underflow (no FTZ/DAZ), masked exceptions, C locale, 32-bit int/64-bit unsigned long/little-endian; both `pow(.,2)` in coverSeeds::run must compile to separate binary64 multiplies (checked in disassembly of the recorded binary only). Stated as assumptions; probes give "limited evidence".
- **Stages:** Seed cover (Sec. 2, Prop 2.10): `covrun` enumerates 9 reduced phases on a 112-grid, radius .032, filtered by vanishing-sum tests -> centres. **A** (Sec. 3-4; `arun`, 4 shards mod 4): each seed -> covers all feasible completions (2x2 unitary cells, Taylor bounds) by certified phase balls ("Records", coarse). **B** (Sec. 5; `brun` .07/.013, .016/.005, fallback .011/.0038): certified refinement into smaller balls via tangent grids. **C** (Sec. 6; `crun 12 4 1 .042 1 1 5000000`): in each ball covers vectors unbiased to first two bases by small balls, builds O/U graphs, excludes two disjoint 6-cliques with 36 U cross-edges; a graph-step cap = "unresolved" (saved, not an exclusion).
- **Numbers (Table 1, Sec. 7.5):** 151,744,086 pairs -> 249,878 centres; A: 764/774/757/788 records (0 unresolved); B mid 600, fine 22,379 (88 batches); initial C: 73 exits 0, 15 exits 1, 163 unresolved (all graph-step caps); B fallback 1,127 records; final C 4x(282,282,282,281), 0 unresolved. 100 native invocations. Run 03:10-04:24 UTC 4 Oct 2026; supervisor wall 4470 s. Hardware/software: x86-64 Xeon Platinum 8573C, Ubuntu GCC 13.3.0, glibc 2.39, `g++ -O3 -march=native -ffp-contract=off` (-std=gnu++17 for A/B/C).
- **Which run:** theorem rests only on the 4 Oct "fresh" run. The 7 Sep run "has not been authenticated" (evidence packet not recovered; hashes/counts agree but are not used).
- **Repo caveat:** VERIFY.md says the packet is a *curated subset*: no binaries, hashes inventory, raw logs, timing, provenance. Paper refers to verification/computation/README.md, proof_run.py, REPRODUCE.md, build-manifest.json; I did not find these in the fetched `verification/` tree (only code/extraction.json and saved-run/).
- **Checker verifies** (check_records.py, 373 lines): full parse + EOF of every record file; finite values; generous bounds (|p|<=4, |T|<=1.01, tiny caps on n0/id/ort/hor/froot, radius <= stage cap); centers.txt format/count; exact command argv/inputs/outputs/exit/completed flags of all 100 children; log progress lines vs. counts (A, B, C); four A shards, B parent/output counts; fine -> batch partition (byte-equal except radius .016); C bad files = ordered subsequence of assigned input; fallback inputs = nonempty bad files, ASCII order; final C partition mod 4, zero failures; exact file-set membership.
- **Checker does NOT verify:** any floating-point computation or inequality; that records cover the parent ball/seed (no geometry); that centres cover the 9-phase space (only counts/range); any C++ source/binary/compiler/hardware; authenticity or provenance of logs (text logs are trusted); the mathematics (Sec. 2-6, App. A) linking records to the theorem. Its own docstring: "derived checker, not the original audit".
- Extra checks I did: sha256 of centers.txt, coarse0-3, mid, fine, fb1 all equal Table 2; first 20 hex of the 7 .cpp sha256 equal verification/code/extraction.json.

## (ii) Mutation tests (checker unmodified; baseline exit 0 in ~3.7 s). 26 mutants; 17 caught, 9 survived.
Detail (exact messages, before/after) in `mutations.json`.

| id | mutation | caught? | message (abridged) | interpretation |
|---|---|---|---|---|
| M01 | delete fine.bin record #10000, header fixed | yes | B output count decreases or exceeds output: Bfine/11 | caught (count vs log) |
| M02 | delete coarse2 record, header unfixed | yes | truncated dimension ... coarse2.bin/756 | caught |
| M03 | duplicate record in batches/f5.bin | yes | batch partition differs: 5 | caught |
| M04 | fine.bin rec 5000 p[0] +1e-6 (that file only) | yes | batch differs beyond radius or insertion order: 19 | caught via fine<->batch byte equality |
| M05 | coarse0 rec 300 p[0] +0.05 rad | no | - | not caught; checker has no link from coarse record content to anything downstream except counts. A wrong A-record would mean a mis-located ball; undetectable without rerun |
| M06 | same change consistently in fine.bin + f19.bin | no | - | not caught; expected: C results are only counters, not recomputed. Says nothing about the theorem; shows record *contents* are unchecked beyond range |
| M07 | bad3.bin record changed by 1e-12 | yes | C failures are not an ordered assigned-input subsequence | caught |
| M08 | swap 2 records in fine.bin only | yes | batch differs ... insertion order: 0 | caught |
| M09 | swap same 2 records in fine.bin and f0.bin | no | - | harmless: order is irrelevant to coverage |
| M10 | truncate coarse1.bin by 100 B | yes | truncated record | caught |
| M11 | centers.txt last row dropped, header kept | yes | centers count or EOF mismatch | caught |
| M12 | centre row deleted, header decremented | yes | cover terminal center count differs | caught only because covrun log states count 249878 |
| M13 | one centre coordinate changed (in range) | no | - | gap: centres' coverage of the 9-phase space is not checked (only format/range/count); records do not name their parent centre. Honest cover is established only by rerunning covrun |
| M14 | coarse0 rec radius -> 0.126 (cap) | no | - | gap in scope: radius only bounded by stage cap; an inflated radius is conservative (bigger ball) but a deflated/wrong one would be undetected |
| M15 | fine rec radius .0161 > .016 | yes | scalar/radius bounds | caught |
| M16 | coarse0 rec froot -> 9e-7 (cap 1e-6) | no | - | stored certified bound not recomputed; a too-small stored bound is the unsafe direction and is undetectable here |
| M17 | ort -> 1e-3 (cap 1e-5) | yes | scalar/radius bounds | caught by loose sanity cap |
| M18 | hide C.batch3's 2 failures (bad file, log, exit code edited) | yes | stage or command arguments differ: C.Bfallback | caught by fallback-input cross-check (bad3 must be in fallback argv) |
| M19 | commands.json C.batch3 returncode 1->0 | yes | unexpected return code | caught |
| M20 | relabel failure categories cap->cluster in log | no | - | harmless: all categories go to fallback; only the sum is checked |
| M21 | final-C bad file nonempty | yes | nonempty terminal bad file | caught |
| M22 | drop last fb1 record AND edit 3 log count fields | no | - | gap in scope: a consistent deletion of a last-stage record (i.e. an uncovered sub-ball) is undetectable because coverage of parent by children is not recomputed; log text is trusted. Requires attacker/error editing logs too; an accidental loss would be caught (cf. M01) |
| M23 | drop coarse0 record, A0 log edited | yes | B parent coverage differs: Bmid/0 | caught downstream by parent count |
| M24 | stray extra file in data/ | yes | data file membership differs | caught |
| M25 | p[3]=5.0 in mid.bin | yes | phase/tangent bounds | caught |
| M26 | 1-ulp bit flip of p[3] in mid.bin | no | - | harmless to this checker; downstream B/C were not rerun on it (the checker cannot tell) |

Reading: survivors show the checker is a bookkeeping/consistency check (counts, order, formats, chain linkage). It cannot detect value-level or geometric corruption. That is its documented scope, not a flaw in the theorem; the mathematical content rests on the C++ rerun + Appendix A.

## Fourier cell (task 4) - partial/inconclusive
Records have 36 phase entries p (apparently in turns, my inference, undocumented). Heuristic `fourier_cell.py`: max deviation of Haagerup products from 6th roots of unity. Several records are near (dev <0.02 turns: 3 per coarse shard, 12 in fine.bin, 13 in fb1.bin) but those include other families' points. The one exact hit (dev 0, Root dim k=0, radius 0; last record of every stage) has products only cube roots -> consistent with Tao's isolated S6, not F6. Per-record C vector counts are NOT in the saved logs (only done/bad counters), so the "48 vectors" number cannot be read off. Not established.

## (iii) Reproduction
```
mkdir -p /home/claude/oai_cert/clone && cd /home/claude/oai_cert/clone
git clone --depth 1 --filter=blob:none --sparse https://github.com/openai/math
cd math && git sparse-checkout set "preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026/verification"
cp -r <...>/verification/saved-run/execution /home/claude/oai_cert/base_exec; cp <...>/check_records.py /home/claude/oai_cert/checker.py
cd /home && python3 -I /home/claude/oai_cert/checker.py /home/claude/oai_cert/base_exec          # exit 0, 3.7 s, Python 3.13, x86_64
python3 -I /home/claude/mub6/src/openai_check/mutate.py /home/claude/oai_cert/base_exec /home/claude/oai_cert/checker.py /home/claude/oai_cert/work /home/claude/mub6/results/openai_check/mutations.json
python3 -I /home/claude/mub6/src/openai_check/fourier_cell.py /home/claude/oai_cert/base_exec/data
```
PDF fetched by curl from raw.githubusercontent.com; text via `pdftotext -layout`. Data total 80 MB (no sampling needed).

## (iv) Not accessed / not run
- C++ programs not built or run (would need hours; platform-specific); compiler/hardware/pow-lowering not checked; build.sh and sources not read line by line.
- verification/computation archive, proof_run.py, REPRODUCE.md, build-manifest.json: not found in the fetched tree; execution archive (raw logs, binaries, hashes inventory) unavailable.
- Appendix A and Sec. 2-6 mathematics not checked; the PDF was read for Sec. 1, 7, 8, A.1 only.
- No independent verification of the seed cover or any floating-point inequality.
