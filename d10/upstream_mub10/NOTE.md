# Snapshot of the dimension-ten working folder ("mub10")

These files are copied unchanged from the dimension-ten working folder of the team. That folder is not under
version control, so there is no commit hash; this snapshot is the reference.

- `data/exact/bu10hp_unimod.txt`: the 3,040 unimodular cyclic 10-roots (high precision midpoints).
- `data/exact/d10_analysis.json`: the stored list of 1,136 candidate bases, orbits and margins.
- `code/exact/`: the programs that produced them (root search, Krawczyk certificate, orbit classification).
- `docs/`: the working ledger and the write-up of the Fourier-pair theorem.

Not included: the full list of 34,940 certified cyclic 10-roots and the per-root certificates. They were produced
in a separate working session and were not available when this repository was assembled. Consequences:
- `../check_d10.py upstream_mub10` re-certifies the 3,040 unimodular roots from scratch and recomputes everything
  downstream (orthogonality graph, 1,136 candidate bases, margin).
- The step "the other 31,900 roots are certified not unimodular" is NOT reproducible from this repository. In the
  report it is tagged as reported by the dimension-ten working session. An independent random search (1.2 million
  starts, `../search_match.py`) found no unimodular root outside the 3,040.
