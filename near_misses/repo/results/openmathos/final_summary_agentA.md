<!-- Written by the Open Math OS agent (DeepSeek V4.1 Flash) on the project machine as
     results/constellations/final_summary.md; fetched through the platform API at
     2026-11-15T09:19Z (01:19 PT). Copied here unedited below this comment. -->
# Constellation search: final state

Written after run 2 finished at its deadline (2026-11-15T07:14:24 UTC).

## Totals

| run | window | seed bases | starts | converged (misfit < 1e-11) |
| --- | --- | --- | --- | --- |
| 1 | 01:24:26 – 02:28:29 | 2026 / 2027 / 2028 | 1,050,000 | 0 |
| 2 | 02:29:47 – 07:14:24 | 3031 / 3032 / 3033 | 5,485,041 | 0 |
| total | | | 6,535,041 | 0 |

Run 1 was lost to a host kill (counts in progress.log only); run 2 seed streams are
disjoint from run 1's, so the counts add.

## Run 2 per shape (three workers each, 21 JSONL files all intact)

| shape | starts | converged | smallest misfit |
| --- | --- | --- | --- |
| (4,3,2) | 784,301 | 0 | 4.9880972555e-03 |
| (4,3,3) | 783,500 | 0 | 2.0222702427e-01 |
| (4,4,1) | 783,796 | 0 | 1.0249768385e-03 |
| (4,4,2) | 783,444 | 0 | 7.4933787457e-03 |
| (5,3,1) | 783,500 | 0 | 7.3278865630e-04 |
| (5,3,2) | 783,000 | 0 | 6.3655670663e-02 |
| (5,4,1) | 783,500 | 0 | 6.2649427163e-02 |

Every per-shape smallest misfit is the same stationary point that calibration and run 1
found, agreeing to all 11 printed digits across independent seed streams. Each worker's
20 smallest non-converged points coincide with the other workers' to the same precision.

A stored near miss recomputes exactly (written 7.3278865630e-04, recomputed the same), so
the files are self-consistent: shape, phases, and misfit normalisation as specified.

## What this does and does not mean

* Every value above is a local minimum of the misfit with r^T r > 0 at the order of
  7e-4 to 2e-1; none is a zero. Nothing converged in 6.5 M random starts.
* This is not evidence that any of these shapes has no zero-misfit configuration. Random
  multistart with a local optimiser is biased toward wide basins: a solution set of
  positive codimension can evade 6.5 M starts while dominating no basin.
* Conversely, no candidate was found, so nothing here supports writing that any
  constellation exists either.
* Covered: (4,3,2), (4,3,3), (4,4,1), (4,4,2), (5,3,1), (5,3,2), (5,4,1), plus
  calibration-only (5,5), (4,3,1), (5,2,2), (5,5,1), (3,3,3). Not covered: (6,),
  (5,5,1) beyond 300 calibration starts, and every shape with a group of size 6.
