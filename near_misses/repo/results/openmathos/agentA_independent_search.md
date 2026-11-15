# Open Math OS agent A: independent re-implementation (DeepSeek V4.1 Flash, effort High)

Prompt: `prompts/openmathos_A_independent_search.md`. The agent wrote its own search from the
mathematical definitions only (no access to our code) on the project's cloud machine
(4 CPUs, 16 GB RAM, Python 3.12.14, numpy 2.5.3, scipy 1.18.1). The text below is copied from
its final message in the session "Independent numerical search for mutually unbiased
constellations in C^6" (read through the platform API on Nov 14, 18:15 PT).

## Its calibration table (converged = final misfit < 1e-11)

| line | shape | starts | converged | smallest misfit | our value for comparison |
|---|---|---|---|---|---|
| a | (5,5) | 200 | 158 | 2.029401006e-15 | 48 of 60 converged |
| b | (4,3,1) | 300 | 22 | 1.944392406e-15 | 31 of 300 converged |
| c | (5,2,2) | 400 | 37 | 1.794426486e-15 | 54 of 400 converged |
| d | (5,5,1) | 300 | 0 | 0.3467852772 | 0.3467852771905 |
| e | (4,4,1) | 4000 | 0 | 0.001024976839 | 0.00102497683851953 |
| f | (5,3,1) | 4000 | 0 | 0.0007327886563 | 0.000732788656303688 |
| g | (4,3,2) | 6000 | 0 | 0.004988097256 | 0.0049880972555 |
| h | (3,3,3) | 2000 | 0 | 0.0877873683 | 0 of 2000 converged (best 0.0889) |

The smallest misfits for lines d to g agree with ours to all 10 digits the agent printed,
although the two programs were written independently and use different random seeds.
The agent also noted, unprompted, that the best points for (4,4,1) and (5,3,1) are stationary
points with misfit about 1e-3: "local minima, not zeros".

## Its long runs (progress snapshot, worker 1 of 3, 43 minutes after launch)

280,000 starts, 40,000 per shape, none converged. Best misfits so far:
(4,3,2) 0.0049881; (4,4,1) 0.00102498; (5,3,1) 0.000732789; (5,4,1) 0.0626494;
(4,3,3) 0.202227; (4,4,2) 0.00749338; (5,3,2) 0.0636557.
Three workers run until about 23:15 PT (planned total about 1.3 million starts per shape).
Output on the cloud machine: `results/constellations/*.jsonl`, `progress.log`.

# Open Math OS agent B: structured search (Kimi K3.1 Pro, Ultramath mode)

Prompt: `prompts/openmathos_B_structured_search.md`. Status at 18:15 PT: no candidate
constellation submitted. The coordinating agent reproduced a known {5,5,2,2} control
(misfit 1.9e-15), and rejected one member's report pending corrections to two of its
arguments. Its negative results are for the specific symmetric structures it tried and are
not evidence of non-existence.
