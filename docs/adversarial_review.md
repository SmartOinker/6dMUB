# Adversarial review log

## How the review works

After each full draft of the report, fresh AI reviewers (model family: Claude Sonnet) are started with the report, the team's source documents, the codebase and the competition rules, but without the drafting history. They act as hostile but fair judges for the six criteria of the panel (correctness, novelty, attribution, clarity, motivation, interest) and return numbered findings with a severity (blocker, major, minor), a question a judge would ask, what they checked, and a proposed fix. The lead author (also an AI) decides on every finding in writing; AI editor agents apply the decisions to the report and the repository and keep an edit log. No human took part in the review cycles recorded here. After the edits, the claims below were re-checked by searching the revised report and the repository (a change is marked "done" only if it was found there). Findings that were not fully fixed are marked "open".

Entry format: id, severity, criterion, the attack as a question, our answer (accepted, partly accepted, rejected) with the reason, the edit made, and the status.

| cycle | reviewers | findings (blocker/major/minor) | main changes |
|---|---|---|---|
| 1 | 2 fresh AI reviewers (correctness and consistency; novelty, attribution, clarity, motivation, interest) | R: 3/14/11 (28); S: 4/12/9 (25); total 7/26/20 (53) | New finite-sample detection theorem replaces the "guaranteed floor"; abstract, contributions table, claim table, limitations, AI-use section rewritten and a Conclusion added; introduction rewritten to motivate the problem; near-miss and dimension-ten claims restated with their conditions; status tags corrected; 20 references and a related-work paragraph added; five independent check scripts and a dimension-ten regeneration added to the repository; team-internal references removed from the body. 23 of 53 findings remain open (see the end of Cycle 1). |
| 2 | 1 fresh AI reviewer (full read of the report, reruns of the checkers, own recomputation of the shot counts) | T: 1/7/8 (16) | Checkers print bounds with directed rounding and all quoted bounds were recomputed (E > 0.03849999999, E > 0.02349999999); all 34,940 cyclic 10-roots regenerated and certified in `d10/roots_full/`, hypothesis (L) deleted; detection test credited as the classical collision test and Theorem `thm:finite` generalized to an optimized threshold (N = 1,936 instead of 2,892); purity-witness proposition added; strongly unextendible sets credited to the cited prior paper (re-read); sections shortened and abstract rewritten; statement on the dates and status of the earlier repository added; this log file created. 5 of 16 findings remain open (see the end of Cycle 2). |
| 3 | 2 fresh AI reviewers (P: panel-style judge who saw only the text of the PDF without the title block; F: mathematics and report-versus-repository audit) | P: 1/8/9 (18); F: 0/8/9 (17); total 1/16/18 (35) | Lean 4 project `MUB6Bridge` built (no `sorry`, standard axioms) for the square-root lemma, the array form of the vector-to-basis theorem and the deterministic steps of the finite-sample theorem; placeholders replaced by a table of declarations; report restructured (structure theory and dimension ten moved into "Additional results, not used in the three answers", main text now about 30 of 50 pages); plain-text restatement of every key formula; ranked "what is new" paragraph and a quantum-information significance paragraph; scope wording and homogeneous sum-of-squares ladder fixed; reviewer's proposed mutation-test sentence rejected as false and replaced; false claim about dimension-ten energy minima corrected; Fourier-pair funnel and 35-shape table backed by shipped scripts and raw data; `docs/verification_matrix.md`, `verify_all.sh`, `docs/verify_all.log` added and stale documents corrected; supplementary PDFs replaced by redacted copies. 12 of 35 findings remain open (see the end of Cycle 3). |

## Cycle 1

Reviewer 1 (correctness and consistency) produced findings R1 to R28. Reviewer 2 (novelty, attribution, clarity, motivation, interest) produced findings S1 to S25. Report length after the cycle: 51 pages (it was 47 to 48 before; the target of 32 to 35 pages was not reached).

### Reviewer 1: correctness and consistency (R1 to R28)

**R1 | blocker | Correctness**
- Question: You say no pure state can hide and call 239 shots a guaranteed floor, but the Pearson statistic is only approximately noncentral chi-square for a fixed alternative, and your own simulation lies below the curve for N up to 100. Where is the theorem?
- Answer: accepted. The reviewer's simulation and ours agree: the approximation is optimistic by up to 12% below N of about 100 and conservative from about 126.
- Edit: new Theorem `thm:finite` (finite-sample detection guarantee), Corollary `cor:finite`, Section 6.5; script `hide_seek/finite_sample.py` and log. With 2,892 shots per setting every pure state is detected with probability at least 95% and white noise raises a false alarm with probability at most 2.7e-4 (0.03%). The 239-shot figure is called a large-sample approximation checked by simulation at N >= 126; the figure caption now says the circles lie below the curve for N <= 100; the sentence that the test "certifies" a triple was replaced by "the test only expresses the certified bound in shots". Abstract, contributions row 6, claim-table rows 16 and 16a, limitations and Section 6.6 updated.
- Status: open. Section 1 (answer to the third question) still says 2,893 shots, while the theorem, abstract, claim table and conclusion say 2,892 (script log: 2,892). One number must be corrected.

**R2 | blocker | Correctness, Attribution**
- Question: Does "near-misses, not solutions" mean that the two 2008 shapes do not exist, and are the 2008 detections "fully accounted for" when you certified only the lowest level found for each shape and do not have the 2008 end points?
- Answer: accepted. The certificate shows nonzero misfit at one strict local minimum, nothing more.
- Edit: abstract and Section 5 now say "certified strict local minima with nonzero misfit that pass the 2008 acceptance test; these two detections become undecided, not refuted"; "fully accounted for" replaced by "consistent with being near-misses; we certified only the lowest level found for each shape". Contributions row 3 and the conclusion follow.
- Status: done.

**R3 | blocker | Correctness, Clarity**
- Question: Why do raw placeholder tokens stand where the Lean status of your theorem should be?
- Answer: accepted. No Lean statement is made for the bridge theorem; the honest text is "none".
- Edit: the lead author was to replace the tokens. A search of the revised report still finds `LEAN-STATUS-PLACEHOLDER` (claim-table row 12), `LEAN-LIMIT-PLACEHOLDER` (limitation 2), `LEAN-DECL-PLACEHOLDER` (Section 10), and the repository and commit placeholders in the title block.
- Status: open. Replace the three Lean tokens with "Lean: none for Lemma `lem:sqrt`, Theorem `thm:bridge` or the certificates (an unbuilt draft is in `lean_drafts/`; no Lean claim is made)"; fill the title-block placeholders before submission.

**R4 | major | Correctness**
- Question: Does the bridge theorem also bound a partial fourth basis, as the remark says?
- Answer: accepted. Part (b) needs all 36 overlaps of a full pair (they sum to 6).
- Edit: Remark `rem:bridgeuses` now says part (a) applies vector by vector and part (b) needs a full basis.
- Status: done.

**R5 | major | Correctness**
- Question: Why is the six-phase bound tagged proved when only an outline is given and nobody on the team checked the case analysis?
- Answer: accepted.
- Edit: Proposition `prop:sixphase` retagged as reported (`\streported`); the text says the case analysis is in the structure paper and the appendix gives an outline only; workstream A's 600-point numerical test is tagged numerical; the Lean step is tagged in the appendix only. The independent numerical check `checks/check_sixphase.py` (numerical maximisation) was added to the repository.
- Status: done. (The new scripts are not yet cited in the report text; see the last list.)

**R6 | major | Correctness**
- Question: Why is the quartic obstruction, an exact statement, tagged computed when no one on the assembling workstream reran the exact check?
- Answer: accepted.
- Edit: Proposition `prop:quartic` retagged as reported; workstream A's double-precision semidefinite program (optimum -2.1e-8) kept as a numerical reproduction; the unproved extension with sphere multipliers was removed from the main text.
- Status: done.

**R7 | major | Correctness, Consistency**
- Question: The abstract states the byte-identical full rerun as a fact, but the body says it was only reported. Which is it?
- Answer: accepted.
- Edit: abstract and contributions row 1 say "a full native rerun by one of our workstreams (reported; not repeated by the workstream that assembled this report)"; Section 3 and the claim table already used "reported".
- Status: open. The Conclusion still says the proofs' "published computations rerun byte for byte" without the qualifier; the ledger uses "cited" where the report uses "reported" (see R12).

**R8 | major | Attribution, Novelty**
- Question: Do you "characterize" the cube-rank-two Hadamard matrices when the decisive step is a prior subblock classification?
- Answer: accepted.
- Edit: abstract now says "a short reduction to a 2026 subblock classification shows that ... cube rank at most two exactly for the Fourier, transposed Fourier and Tao types"; the proof idea and the appendix proof name the classification as prior work and as the decisive step.
- Status: done.

**R9 | major | Correctness**
- Question: What is "the obstruction" that degree-four certificates "cannot see"?
- Answer: accepted.
- Edit: abstract now says "a degree-four sum-of-squares relaxation of the energy problem below has value zero although the true minimum is positive"; Section 4 states that the result is specific to the formulation (12 state coordinates, fixed measurements).
- Status: done.

**R10 | major | Correctness**
- Question: The dimension-ten theorem needs the 31,900 non-unimodularity certificates, which are not in the repository, yet it is tagged conditional only on the root count. Is that honest?
- Answer: accepted.
- Edit: Theorem `thm:ten` now assumes (H) (at most 34,940 roots) and a new hypothesis (L) (the list of 34,940 certified boxes with the 3,040 / 31,900 split, taken from workstream A's working session); tagged conditional; the abstract says "conditional on a cited root count and on a list of certified roots from our working session that is only partly reproduced"; the repository check is stated to re-certify only the 3,040 unimodular roots; the text is written to stay true if regeneration fails. A regeneration was started in `d10/roots_full/` (random-start Newton search; its log reports 34,940 distinct roots after 56,000 starts).
- Status: open. The regeneration output is raw and uncertified (no Krawczyk boxes, no non-unimodularity certificates), so (L) remains a hypothesis; the report does not yet mention `d10/roots_full/`.

**R11 | major | Correctness, Reproducibility**
- Question: The sqrt-lemma test described in the report (Dirichlet vectors, Nelder-Mead, slack 1.6e-6) is not in the repository. What does the cited script actually do?
- Answer: accepted. The reviewer ran it and found a different test.
- Edit: Section 6.3 and claim row 12 now describe `checks/check_sqrt_lemma.py` exactly (1.8 million overlap entries from 50,000 random unitary pairs and a grid of 2,000,001 points; smallest slack 8e-15 on the random entries and 0 on the grid); the Dirichlet and Nelder-Mead numbers were deleted. The lemma's proof does not depend on the test.
- Status: done.

**R12 | major | Consistency**
- Question: Why do the ledger and the README say that the Fourier-pair certificates are unfinished and the mutation test was not re-run, when the report claims both?
- Answer: accepted (assigned to the lead author).
- Edit: new independent checks were added (see R5, R6, R10 and the list at the end), and `d6_fourier/verify_fourier6_certs.py` and `openai_check/` (rerun record of the checker and of the 26-mutation test) now exist. A search of `docs/verification_ledger.md` and `README.md` shows they were not yet updated: ledger rows 5, 11, 21 and 23 and the "not verified" list still carry the old statements, and the README still says "results to be added" and does not list the new check scripts.
- Status: open. Update the ledger rows and the README, and use the same status words as the report ("reported" and "cited" must be one vocabulary).

**R13 | major | Attribution, Clarity**
- Question: The AI-use section cites a log file that does not exist and claims three rounds of review. Where is the log?
- Answer: accepted.
- Edit: this file; Section 10 (v) now says the log "also says how many rounds were completed" instead of "three rounds". One round (cycle 1) is recorded here.
- Status: done.

**R14 | major | Attribution**
- Question: The abstract says you map what each proof rests on, but the third proof was only read from an AI-prepared summary.
- Answer: accepted.
- Edit: abstract: "From their repositories (two proofs) and from summaries (the third)"; the trust-map paragraph on that proof says it rests on the preprint's abstract and an AI-prepared summary and is not verified.
- Status: done.

**R15 | major | Correctness**
- Question: Does the Fourier-pair design lesson need the cited count of 156 cyclic 6-roots, and does it cover non-MU triples?
- Answer: accepted.
- Edit: abstract says "(given the classical count of cyclic 6-roots)"; Corollary `cor:fourier6` now speaks of "any mutually unbiased triple".
- Status: done.

**R16 | major | Correctness**
- Question: Is the second product triple really the second McNulty-Weigert class, or only some MU triple?
- Answer: accepted.
- Edit: Section 6.1 states that the triple is defined from the review (eq. 7.19), that the checker verifies only that it is mutually unbiased, that the class is taken from the review, and that the minima 0.0238354 and 0.0387628 recurring among the Fourier-pair triples are consistent with it.
- Status: done.

**R17 | major | Correctness**
- Question: Do the 300 orthogonal pairs form exactly 16 sets of six?
- Answer: accepted. Recomputation: 16 cliques of size six cover 228 of the 300 edges.
- Edit: Section 3 (Fourier redo, item 4) now says 16 cliques of size six covering 228 of the 300 edges, each vector in two, and that all 16 triples are interval-certified with E >= 0.0234999 (Proposition `prop:fourier6`).
- Status: done.

**R18 | minor | Correctness**
- Question: Is "a line meets the unit circle in at most two points" the right reason in the cube-rank proof?
- Answer: accepted.
- Edit: step 1 of the proof now argues with two distinct circles meeting in at most two points unless they coincide, which forces alpha times beta to be zero.
- Status: done.

**R19 | minor | Correctness, Consistency**
- Question: Do small numbers agree everywhere (5e-17, 0.0798 for which triple, 368 against 369 shots, 1,000 against 5,000 shots for the dimension-four control)?
- Answer: accepted.
- Edit: report now says "within 1e-16" and qualifies the 0.0798 bias as obtained with an exactly mutually unbiased triple held fixed. `hide_seek/RESULTS.md` was not aligned: it still says 1,000 shots for the dimension-four control and 368 for 99% at five sigma (report: 5,000 and 369).
- Status: open. Edit `hide_seek/RESULTS.md`.

**R20 | minor | Consistency**
- Question: Why do mu, F, Delta, B, Q, H, K and N each mean several things?
- Answer: partly accepted.
- Edit: the 2008 function is now F_BW; the Hessian is `\mathcal H`, the Krawczyk operator `\mathcal K`, the phase ball `\mathcal B`, the fourth basis `\mathcal F`; the dimension-ten energy is declared a different functional; "bias" and the other terms are defined where first used. Not done: the misfit mu against the game value mu, the several uses of Delta, Q and N, and the "game loss" against "gap" and "shortfall" wording.
- Status: open.

**R21 | minor | Correctness**
- Question: Is degree six really "the first level" that can certify a gap?
- Answer: accepted.
- Edit: "the first even degree above four" in Sections 4 and 6.2.
- Status: done.

**R22 | minor | Consistency**
- Question: How can a preprint dated 24 September rest on a run of 4 October?
- Answer: accepted. We inferred a revision; this is flagged.
- Edit: trust-map table now reads "24 Sep 2026 (revised after a run of 4 Oct)".
- Status: done (the revision is an inference, not checked against the source).

**R23 | minor | Correctness**
- Question: Is Q symmetric in the positive-semidefiniteness argument?
- Answer: accepted.
- Edit: Appendix B states that the argument uses symmetry of Q, that the stored matrices are exactly symmetric (checked bit by bit), and the symmetrisation otherwise.
- Status: done.

**R24 | minor | Clarity**
- Question: Why do editing comments ("Include VERBATIM") remain in the source?
- Answer: accepted.
- Edit: the markers were removed (none found in the revised source). The font-shape warning of the tag macros was not re-checked.
- Status: done.

**R25 | minor | Correctness**
- Question: Where is the dimension-seven positive control?
- Answer: accepted.
- Edit: tagged reported (it exists only in working-session notes); the text says "reportedly".
- Status: done.

**R26 | minor | Correctness**
- Question: Is the mixed-volume value 35,940 verified?
- Answer: partly accepted. The reviewer allowed either citing a source or keeping the hedge; the working-session notes disagree on whether it came from the literature or from a homotopy package, so we kept the hedge.
- Edit: tagged reported and stated as "not recomputed by us" in Section 7 and in limitation 7.
- Status: done.

**R27 | minor | Correctness**
- Question: Does every use of the cited count of 156 cyclic 6-roots carry the conditional tag?
- Answer: accepted.
- Edit: the steps in Section 3 and Finding 3 of Section 5 are now tagged conditional.
- Status: done.

**R28 | minor | Correctness**
- Question: Is the phase-ball "proof sketch" a sketch or a proof?
- Answer: accepted. The reviewer checked every step.
- Edit: renamed "Proof" (Appendix `app:phase`).
- Status: done.

### Reviewer 2: novelty, attribution, clarity, motivation, interest (S1 to S25)

**S1 | blocker | Motivation, Clarity**
- Question: The three questions are posed and never answered together. Where is the conclusion?
- Answer: accepted.
- Edit: new Section `sec:conclusion` ("three questions, three answers") at the end of the body, before the appendices.
- Status: open. Its last paragraph says the same three steps, including "a number that can be measured", go through in dimension ten; Section 7 says there is no certified energy bound in dimension ten. It also states the byte-for-byte rerun without "reported" (see R7). Fix both sentences.

**S2 | blocker | Motivation, Interest**
- Question: Why should a reader care? The report opens by saying that nothing is new.
- Answer: accepted.
- Edit: Section 1 rewritten: opens with why MUBs matter (complementary measurements, tomography, key distribution, random access codes), why six is the first open case and what an experimentalist cannot currently be told; then the three questions with three answers and numbers; terms, roadmap and a story line follow.
- Status: done.

**S3 | blocker | Clarity, Attribution**
- Question: Why are there placeholder tokens inside claim statements?
- Answer: accepted (same as R3).
- Edit: see R3.
- Status: open (see R3).

**S4 | blocker | Attribution, Novelty**
- Question: AI-drafted proofs by two workstreams carry the same "proved" tag as human-checked work, and "read line by line by a workstream" hides that the reader is an AI.
- Answer: partly accepted. We rejected a table of reviewers per claim group and a new draft tag: the honest statement is that proofs were written with AI assistance and cross-read by AI agents of a different workstream, and no line-by-line human refereeing is claimed.
- Edit: Section 10 now says exactly that ("What this checking is not") and limitation 3 says that no second person reviewed the checker; in the body, "read line by line" became "cross-read by workstream X (AI-assisted)"; the tools used are listed (Claude, Codex, open-weight agents).
- Status: open. The abstract does not say that the structure theory and the Lean part are AI-drafted and not rebuilt by the assembling workstream; model versions are not named in the AI-use list.

**S5 | major | Novelty**
- Question: Isn't the vector-to-basis theorem a routine corollary presented as a headline result, and does it concern any fourth basis or only completions of a given triple?
- Answer: partly accepted. We kept it as a theorem but say plainly that it is elementary and that its value is converting a one-vector certificate to basis-level figures; we did not rename it a corollary.
- Edit: "elementary" in the abstract, contributions row 5 and Section 6.3; new Remark `rem:constant` (largest constant, how it improves if overlaps are bounded away from one); Section 1 says "completing the triple".
- Status: open. Contributions row 5 and the abstract sentence ("any fourth basis") still omit "completing the triple".

**S6 | major | Novelty, Attribution**
- Question: Is the "by how much" story mostly prior work (the exact minimum), with the new part smaller than the abstract suggests?
- Answer: partly accepted. We separated prior from new but did not reorder the abstract.
- Edit: Section 6.1 paragraph "What is prior and what is ours"; abstract and row 4 state that the exact minimum is prior work and that the certificate reaches 99.3% of it; "to our knowledge" added for the second product triple and the 16 Fourier-pair triples.
- Status: open. The abstract still leads with the canonical-triple value 0.0385 rather than with the new certificates.

**S7 | major | Novelty, Attribution**
- Question: Where is the prior art a specialist expects (Hadamard-matrix route, cyclic roots, self-testing, SDP hierarchies, gap results)?
- Answer: accepted. References were collected and checked by a helper; none were invented.
- Edit: 20 verified references added (bibliography now 45 entries) and a paragraph "Related work and what is new here" at the end of Section 1 with "to our knowledge" statements; the cyclic-root, Hadamard-order-six, self-testing, hierarchy and extension-gap items are cited there.
- Status: open. Two suggested items were not added (the self-adjoint order-six Hadamard antecedent, and the prime-power constructions beyond the one cited). The "Prior work (not ours)" paragraph in Section 10 was not extended.

**S8 | major | Novelty, Interest**
- Question: Is the laboratory story credible, and is "239 shots against 1e8 rounds" a fair comparison?
- Answer: partly accepted. The comparison was qualified; the scenario was not changed.
- Edit: the game figure is called an upper-bound heuristic (Section 1, Section 6.6: "no round count for the game is a guarantee"); the paragraph on an "earlier team report" was removed; a sentence connects the test to self-testing work (Section 1); the 239-shot figure is no longer a headline.
- Status: open. The hider-and-referee scenario is unchanged (no verifier scenario was added), and the circuit and noise paragraph in Section 6.5 and the gate-error bullet in Section 6.6 were not cut.

**S9 | major | Attribution**
- Question: Why does the body refer to an "earlier team report", a "team ledger" and team commits the panel cannot open?
- Answer: accepted.
- Edit: those phrases were removed from the body (none found); hashes of team repositories were replaced by "commit given in the title block" in Sections 2, 3 and Appendix A; only the Mathlib commit (public) is kept; the comparison with the related Weyl-Heisenberg result now says that wording was not compared and no priority is claimed.
- Status: open. One team-repository hash remains in claim-table row of Section 8 ("of the team Lean repository"); replace it by "commit given in the title block".

**S10 | major | Attribution**
- Question: Abstract and contributions table state other workstreams' results without a hedge.
- Answer: partly accepted.
- Edit: abstract and row 1 qualify the full rerun as reported and not repeated by us; row 4 says "Lean-checked as reported"; row 2 says "reported and numerically reproduced".
- Status: open. The abstract has no one-clause statement that the structure theory and Lean development were written by other, AI-assisted workstreams and only partly re-run (see S4).

**S11 | major | Novelty, Interest**
- Question: Is dimension ten bolted on, conditional on an unverified count, and does its closing sentence overclaim?
- Answer: accepted.
- Edit: Section 7 shortened (pipeline stated first, funnel description in centimetres and the derivation moved to Appendix D); closing sentence fixed: "there is no certified energy bound in dimension ten" (0.0202 is numerical, 0.0022 for orbit 8); the abstract and Section 1 say the result tests the method and says nothing about N(10); (H) and (L) stated as hypotheses.
- Status: done. (The Conclusion repeats the overclaim; tracked under S1.)

**S12 | major | Clarity**
- Question: Why does every section open with a block of tag vocabulary and why do sentences carry two tags?
- Answer: partly accepted. At most one status tag per sentence and plain sentences instead of status blocks were adopted; reducing the vocabulary to five tags was rejected because the claim table and ledger use the nine tags consistently.
- Edit: status paragraphs of Sections 1 to 7 replaced by one or two plain sentences; "What this means for the story" line added to Sections 1 to 5, 6 and 7; provenance tags thinned.
- Status: open. Sections 8, 9 and 10 still open with "Status of this section".

**S13 | major | Clarity, Story**
- Question: Does Section 4 (structure theory) serve the story and can a non-specialist follow it?
- Answer: partly accepted. We shrank it and moved the proofs, but did not move the quartic obstruction into Section 6.2.
- Edit: Section 4 rewritten to about 1.9 pages (target was 1.5): three-sentence motivation for the entrywise cube, four statements with one tag each and a proof idea, the open step; full proofs (cube rank, cubic cap, six-phase outline, quartic certificate, total-variation corollary) moved to Appendix A; terms defined at first use.
- Status: done (deviation: 1.9 pages; the ladder in Section 6.2 refers to the quartic result instead of absorbing it).

**S14 | major | Clarity, Story**
- Question: Do Sections 3 and 5 read like notebooks and tell the Fourier-pair computation four times?
- Answer: partly accepted. The Fourier redo is told once (Section 3, label `sec:fourierredo`) and referred to elsewhere; the phase-ball proof and the 35-row table moved to appendices; we did not cut the phase-ball result or the worked examples, and did not move the redo to Section 7.
- Edit: Appendices `app:phase` and `app:table`; near-miss wording changed as in R2.
- Status: done (deviations as stated).

**S15 | major | Clarity**
- Question: Is the trust-map table unreadable, with undefined terms, and does it rest on AI summaries?
- Answer: accepted.
- Edit: compact four-column table `tab:trust` plus one short paragraph per proof (reduction, local test, arithmetic, Lean); terms defined once; the third proof marked as resting on an abstract and an AI-prepared summary.
- Status: done.

**S16 | major | Clarity**
- Question: Are terms and notation used before they are defined (energy, bias, game loss, Hadamard matrix, SOS)?
- Answer: partly accepted. Definitions at first use were added; we did not add a separate glossary box.
- Edit: energy, bias, game loss, Hadamard matrix, cube rank, SOS certificate, cubic Tao matrix and Assumption A are defined where first used, including in the abstract; the unitarity correction moved to Appendix B; the centimetre widths of the funnel figure were removed.
- Status: done.

**S17 | minor | Novelty**
- Question: Why is hedging almost absent ("to our knowledge")?
- Answer: accepted.
- Edit: hedges added in the related-work paragraph for the energy bounds, the conversion to basis-level figures, the detection statement, the near-misses and dimension ten.
- Status: open. No hedge was added for the mutation test or in the abstract for the cube-rank criterion.

**S18 | minor | Clarity**
- Question: Does "how to see it" in the title promise something the work cannot deliver?
- Answer: accepted.
- Edit: the opening "nothing in this section is new" was removed; the title is unchanged.
- Status: open. Change the title (for example "what is verified, how far away it is, and how to test for it").

**S19 | minor | Clarity**
- Question: Why is the report so long (about 15 pages could go)?
- Answer: accepted.
- Edit: sections cut or moved as in S13 and S14; the 1/72 appendix and the 22-row claim table were kept.
- Status: open. 51 pages against a target of 32 to 35; the reproduction appendix, the 1/72 appendix and the claim table are the main candidates.

**S20 | minor | Clarity**
- Question: Do the 7-row reading-guide table and the 22-row claim table duplicate each other?
- Answer: accepted.
- Edit: none beyond the corrections inside each table.
- Status: open. Add a "new / re-derived / prior" column to the 7-row table and mark the claim table as an index (or move it to an appendix).

**S21 | minor | Attribution**
- Question: Is "independent recomputation" independent when the code was written by the same kind of AI from the other workstream's description?
- Answer: accepted.
- Edit: Section 3 states that the partial rebuild on a second machine has weak independence and that the workstreams share an AI workflow.
- Status: open. Item (iii) of "How AI output was checked" in Section 10 still says "independent recomputation ... with its own programs" without saying that independence is of code, not of authorship.

**S22 | minor | Novelty**
- Question: Is the SOS ladder a result or a table, and why does degree four fail?
- Answer: accepted.
- Edit: "first even degree above four" added (see R21).
- Status: open. The reason for the degree-four failure (the pseudomoment is the uniform measure on a design, if correct) was not added; it should be checked before it is written.

**S23 | minor | Clarity**
- Question: Are "workstream A/B/C", "audit commit" and similar team terms understandable?
- Answer: rejected. The reading guide defines the three workstreams once and the claim table and the event section use them; the competition asks to separate event work from prior work, and the same labels are used in the AI-use section. Team-specific phrases ("earlier team report", "team ledger") were removed (see S9).
- Edit: none.
- Status: closed.

**S24 | minor | Interest**
- Question: Are the strongest pieces signposted in the reading guide?
- Answer: rejected. The order of the reading guide follows the three questions; ranking contributions by interest would break that order.
- Edit: none.
- Status: closed.

**S25 | minor | Clarity**
- Question: Why does a proof outline sit next to a "proved" tag?
- Answer: accepted (same as R5).
- Edit: see R5.
- Status: done.

### Still open after cycle 1

Counts (53 findings): accepted 40, partly accepted 11, rejected 2; open 23 (R1, R3, R7, R10, R12, R19, R20, S1, S3, S4, S5, S6, S7, S8, S9, S10, S12, S17, S18, S19, S20, S21, S22).

- Placeholders: the three Lean tokens in the claim table, limitation 2 and Section 10; repository link and commit in the title block (R3, S3).
- One number: 2,893 in the answer to the third question of Section 1 against 2,892 everywhere else (R1).
- Conclusion: the dimension-ten paragraph claims a measurable number that dimension ten does not have, and the byte-for-byte rerun lacks "reported" (S1, R7, S11).
- Dimension ten: hypothesis (L) is still unverified in the repository; `d10/roots_full/` holds an uncertified random-start regeneration of the 34,940 roots and no certificates of non-unimodularity; the report does not mention it (R10).
- Ledger, README and result files: `docs/verification_ledger.md` rows 5, 11, 21, 23 and the "not verified" list, the README directory map and its "results to be added" line, and `hide_seek/RESULTS.md` (1,000 shots, 368 shots) disagree with the report (R12, R19).
- New checks not cited: `checks/check_sixphase.py`, `checks/check_hadamard_identities.py`, `checks/check_gap72.py`, `checks/check_phase_ball.py`, `checks/check_sqrt_lemma.py` (cited), `openai_check/`, `d6_fourier/verify_fourier6_certs.py` exist in the repository, but only the square-root script is named in the report; the report should cite each as a numerical check by workstream A, with its scope.
- Notation: misfit mu against game value mu, several meanings of Delta, Q and N, and the terms game loss, gap and shortfall (R20).
- Abstract and contributions table: say "completing the triple"; add that the structure theory and the Lean part were written by other, AI-assisted workstreams and only partly re-run; lead with the new certificates; name model versions in the AI-use list (S4, S5, S6, S10).
- Hide and seek: the verifier scenario is not reframed and the circuit and noise paragraph and the gate-error bullet are not cut (S8).
- Structure of the body: "Status of this section" remains in Sections 8, 9 and 10; one team-repository hash remains in the claim table; the reading-guide table has no new / re-derived / prior column; the claim table is still in the body (S9, S12, S20).
- Related work: two suggested prior-art items not added; "Prior work (not ours)" in Section 10 not extended; no hedge for the mutation test or the cube-rank criterion in the abstract (S7, S17).
- Title and length: the title still says "how to see it"; the report is 51 pages against the target of 32 to 35 (S18, S19).
- Independence wording in Section 10 (iii), and the reason why degree four fails in the SOS ladder (S21, S22).

## Cycle 2

One fresh AI reviewer read the full report (51 pages), re-derived the new material, reran `hide_seek/finite_sample.py`, `cert/verify.py` (both triples), `cert/verify_sets.py`, `d6_fourier/verify_fourier6_certs.py` and `d10/roots_full/certify_roots.py`, and recomputed the shot counts independently. Findings T1 to T16. The lead AI agent of workstream A decided; three AI editors applied the decisions. No human took part. Status is stated as found when cycle 3 started, and a later closure is noted in brackets.

**T1 | blocker | Correctness**
- Question: Proposition `prop:cert6` says E > 0.038499999998, but 0.0385 minus 2.2e-12 is smaller than that; does the checker print its lower bound rounded to nearest, and are the other quoted bounds rounded the right way?
- Answer: accepted. The shot counts do not change (checked by the reviewer).
- Edit: `cert/verify.py`, `cert/verify_sets.py` and `d6_fourier/verify_fourier6_certs.py` now print bounds rounded down; all quoted bounds were recomputed: E > 0.03849999999 (nominal level 0.0385 minus at most 2.2e-12), E > 0.02349999999; running text uses E > 0.0384999 and E > 0.0234999; "E >= 0.0385" is attributed to Erlwein's exact minimum only; derived numbers (bias > 0.046248 and 0.036132, game loss > 3.302e-4 and 2.015e-4) stay valid; the bound for explicit sets was recomputed with directed rounding (bias <= 0.030223873, game loss <= 2.357826e-4).
- Status: open. At the start of cycle 3 the ledger, `cert/README.md` and the README still carried 0.038499999998, `verify_sets.py` printed upper bounds rounded to nearest, and one report sentence said that all derived numbers use the rounded-down values (they do not, see F7, F8, F9). [Closed in cycle 3.]

**T2 | major | Clarity, Correctness**
- Question: Why do the tokens `LEAN-STATUS-PLACEHOLDER`, `LEAN-LIMIT-PLACEHOLDER`, `LEAN-DECL-PLACEHOLDER` and the title-block placeholders remain in the compiled PDF?
- Answer: accepted. The reviewer's proposed text (a Lean draft that was never compiled) was not used in cycle 2; filling the tokens was left to the lead author.
- Edit: none in cycle 2.
- Status: open. [The three Lean tokens were replaced in cycle 3 (P1). The title-block repository link, commit and one author field are still unfilled.]

**T3 | major | Correctness, Novelty**
- Question: Hypothesis (L) is already discharged by `d10/roots_full/`; why does the report still call it a hypothesis and say the list is not in the repository?
- Answer: accepted. The reviewer reran the certifier (35 s) and got the stated counts.
- Edit: all 34,940 cyclic 10-roots regenerated and certified in `d10/roots_full/` (34,940 Krawczyk-certified, pairwise disjoint, 3,040 unimodular, 31,900 certified not unimodular, 0 undecided; the 3,040 coincide with the stored list); (L) deleted everywhere, Theorem `thm:ten` conditional on (H) only; the 31,900 non-unimodularity certificates retagged as certified; appendix rewritten; the fallback caveat (mixed volume 35,940 reported, not verified) kept; the statement that `find_roots.py` is a heuristic and the folder is not under version control kept once.
- Status: done.

**T4 | major | Attribution, Novelty**
- Question: The detection test is the textbook collision test for uniformity; why does the report call the statement new and leave out the property-testing literature?
- Answer: accepted.
- Edit: the test is credited as the classical collision test (Goldreich-Ron, Paninski) with Hoeffding's variance formula; "is new" removed; ideal measurements and independent identical preparations stated in the abstract and Section 1; Theorem `thm:finite` generalized to an optimized threshold: N = 1,936 shots per setting for 95% detection of every pure state at false-alarm probability at most 0.1% (5,142 for 99%; 3,007 and 7,687 for the second product triple and the 16 Fourier-pair triples); the unoptimized t = 1/2 figure (2,892) is kept and labeled; Proposition `prop:purity` added (uniform statistics force the largest eigenvalue at most 0.8232); 239 shots is kept only as a large-sample rule of thumb.
- Status: done.

**T5 | major | Attribution**
- Question: Are the other literature claims supported (sources the reviewer could not check; "to our knowledge" claims resting on the Wall Atlas), and why is the overlap with the unextendible-sets paper in dimension ten left vague?
- Answer: accepted. The reviewer could verify the older literature and not the 2026 documents.
- Edit: the cited paper of Grassl, McNulty, Mista and Paterek was re-read (abstract and introduction) and credited for strongly unextendible sets and the idea of purity witnessing; the dimension-ten relation is stated "to our reading" as: their example with the standard and Fourier bases is a special case of Theorem `thm:ten`, independent of (H), computation not reproduced by us; our addition is the complete list of all 1,136 candidate third bases with certified margins; novelty claims narrowed to "in the documents we read, to our knowledge"; one sentence dropped for length.
- Status: done.

**T6 | major | Correctness**
- Question: Shapes with three groups cannot be sub-shapes of the triple {5,5,5}_6; on what grounds do 14 of the 17 existing shapes exist?
- Answer: accepted. Entrywise comparison shows each of the 14 lies below one of the three examples of the cited constellation paper.
- Edit: text and table caption now say "14 as sub-shapes of the three examples of [CWT] (found numerically here with misfit below 1e-14), and these three themselves". The 17 / 5 / 13 count is unchanged.
- Status: done.

**T7 | major | Clarity, Interest**
- Question: Is the report one story, and why is it 12 to 15 pages too long (about 40-line abstract, "story" boxes, definitions after use, a different story in Section 4 and Section 7)?
- Answer: partly accepted. We cut and reordered; we did not move Section 4 and Appendix A to a separate supplement.
- Edit: every "What this means for the story" box and every "Status of this section" paragraph deleted, one "In short:" sentence per section; Section 1 reordered (MUBs and dimension six, Terms, three questions, related work, roadmap); abstract rewritten; the Fourier-redo steps moved to an appendix; Section 4 cut to one page and Section 7 to about 1.2 pages; the sum-of-squares ladder to one paragraph. Fragment lengths: Sections 1 to 3 from 8 to about 5.9 pages, Section 5 from 3.4 to about 3.05, Section 6.1 to 6.4 from 6.4 to about 5.0 (target 4.5 not reached).
- Status: open. The compiled report still had about 49 pages. [Reduced to a main text of about 30 pages in cycle 3 (P7); 50 pages in total with appendices.]

**T8 | major | Attribution**
- Question: What was done during the event for the code taken from the earlier repository and the dimension-ten working folder, which have no public hash?
- Answer: accepted.
- Edit: Section "Event work" now says that both were created during the event, that the earlier repository is delivered as a git bundle and is not public, and that the dimension-ten folder was not under version control.
- Status: done.

**T9 | minor | Consistency**
- Question: Do small numbers agree (2,893 against 2,892, about 240 against 239, N >= 126 against the simulated N, the simulated rate at N = 50, 12 s against 25 s, a printed "nan", the path `d6f/`, the false roadmap sentence)?
- Answer: accepted.
- Edit: 2,893 removed; 239 everywhere; simulation points stated as N = 50, 100, 126, 239; "under 30 s" for the 16 Fourier-pair certificates; path `d6_fourier/fourier6.py`; roadmap sentence about prior work fixed; the printed output of `verify_fourier6_certs.py` no longer has the "nan" column. The N = 50 rate is quoted from two labeled runs (0.098 new run, 0.096 earlier run).
- Status: done.

**T10 | minor | Correctness**
- Question: Is Remark `rem:constant` unused and over-sold ("about 3 times" the constant)?
- Answer: accepted.
- Edit: "about 3 times" deleted; the remark reduced to the statement about c(P), with the sentence that it is not used for any number and needs an a priori bound P on all squared overlaps.
- Status: open. The reduced remark kept the clause "by part (a), P >= 1/6 + ...", which is false; the correct bound is 1/6 + sqrt(gamma/18)/5 (the reviewer's own proposed wording had the same error; found in cycle 3, P16 and F1). [Closed in cycle 3: remark deleted.]

**T11 | minor | Clarity, Motivation**
- Question: Does the abstract wrongly say that the two 2008 entries "supported the conjecture"?
- Answer: accepted.
- Edit: abstract wording by the lead author ("two entries of the 2008 numerical table of partial fourth bases"); Section 5 says the table measured how large a partial fourth basis can be built.
- Status: done. (The abstract still ends "so these two entries become undecided"; a clearer wording was requested in the cycle 3 list of unclear sentences.)

**T12 | minor | Correctness**
- Question: Is the scope of Theorem `thm:finite` stated (ideal settings, identical preparations), is the threshold gamma/2 wasteful, and do 200 random states far above the minimum say anything?
- Answer: accepted.
- Edit: scope stated in abstract and Section 1; threshold optimized (see T4); the simulation now also uses 200 states near the minimizer (no missed detection in 20,000 runs).
- Status: done.

**T13 | minor | Attribution**
- Question: The AI-use section points to `docs/adversarial_review.md`, which does not exist.
- Answer: accepted.
- Edit: this file was created (it held cycle 1 at that time); the pointer in Section 10 kept.
- Status: open. Section 10 says the log "also says how many rounds were completed", but the report text gives no number (repeated as P13). [Number to be added after cycle 3.]

**T14 | minor | Attribution, compliance**
- Question: Why does the claim table contain a prefix of a team-repository hash?
- Answer: accepted.
- Edit: replaced by "audit revision named in the title block" in the body.
- Status: done. (Cycle 3 showed that this wording points the panel to text it cannot see, see P2.)

**T15 | minor | Clarity**
- Question: Are the two product triples additional to the 16 Fourier-pair triples, and is the "14 triples" sentence correct?
- Answer: accepted. Equal numerical minima show that both product triples are among the 16.
- Edit: the text says that four of the 16 triples have the minima of the two product triples; twelve have numerical minimum 0.0326759 and, to our knowledge, no certified bound existed for them or for the second product triple.
- Status: done.

**T16 | minor | Clarity**
- Question: Are workstreams A, B and C understandable, is "No hardware run was performed" repeated, and what is "revised after a run of 4 Oct"?
- Answer: accepted.
- Edit: the workstreams are defined at the start of the trust-map section with a pointer to the event-work section; the table cell was replaced; "Status" paragraphs removed.
- Status: done. ("No hardware run was performed" still appears twice.)

### Still open after cycle 2

Counts (16 findings): accepted 15, partly accepted 1 (T7), rejected 0; open 5 (T1, T2, T7, T10, T13).

- Stale repository documents (ledger, cert README, README) and upper bounds printed with round-to-nearest in `verify_sets.py` (T1).
- Placeholders: three Lean tokens in the claim table, limitation 2 and the Lean section, and the title-block link, commit and author field (T2).
- Length: about 49 pages (T7).
- A false clause in the unused remark on the constant (T10).
- The number of review rounds is not in the report (T13).

## Cycle 3

Two fresh AI reviewers. The panel-style judge (P1 to P18) saw only the text of the PDF without the title block and read the rule files and the problem entry; the second reviewer (F1 to F17) did a mathematics and report-versus-repository audit: it re-derived every proof, recomputed every number from scratch and reran 17 checkers on a copy of the repository. The lead AI agent of workstream A decided; AI editors applied the decisions. No human took part. Report length at the start: 49 pages. Report length after the cycle: 50 pages, of which the main text (up to the conclusion) is about 30. The report in the working folder was rebuilt after the cycle; the stale copy under `report/` in the repository is listed as open.

### Reviewer P: panel-style reading of the PDF text (P1 to P18)

**P1 | blocker | Clarity, Correctness**
- Question: What is the Lean status of Lemma `lem:sqrt`, Theorem `thm:bridge`, Theorem `thm:finite` and Proposition `prop:purity`, when three tokens stand in its place?
- Answer: accepted. The reviewer's proposed text ("not formalized") would now be false for two of them, so it was not used.
- Edit: a Lean 4 project `MUB6Bridge` was built locally by workstream A (Lean v4.35.0, Mathlib v4.35.0, no `sorry`, standard axioms; log `lean/BUILD_LOG.txt`). It formalizes the square-root inequality (not the equality cases), the array form of the vector-to-basis theorem (18 numbers for part (a), arrays of squared overlaps for part (b)), the numbers of the corollary, and only the deterministic steps of the finite-sample theorem (Pearson identity, two variance bounds, the arithmetic of N = 1,936). No probability statement is formalized, so Theorem `thm:finite` is not Lean-verified. The three tokens were replaced by a table of declarations (Table `tab:leanA`, Section "Event work"), the claim table row, limitation 2 and the new tag "Lean-checked here" (array form); no stronger Lean claim is made. A search of the PDF text finds no Lean placeholder.
- Status: done.

**P2 | major | Clarity, Attribution**
- Question: Why does the report point to a title block the panel cannot see for the Lean revision, the audit revision and the repository?
- Answer: partly accepted. We give both full 40-character hashes in the body (a hash is not a link); the repository link itself stays in the title block, as the rules require.
- Edit: baseline hash of workstream B and audit hash of workstream C stated in the body (Section 3, Section 6.1 and the Lean table intro); several "commit given in the title block" phrases removed.
- Status: open. The claim table (row on the 128-bit record check) still says "audit revision named in the title block", and "submission repository" is still used for paths (the reviewer asked for "supplementary archive").

**P3 | major | Clarity**
- Question: Are the key formulas readable in the text the panel sees (displays scrambled, "t = 1/2" read as "t = 12")?
- Answer: accepted.
- Edit: Sentences "In plain text:" in typewriter font after the energy definition, the 2008 function and the misfit, Proposition `prop:cert6`, Lemma `lem:sqrt`, Theorem `thm:bridge` (a) and (b), Corollary `cor:numbers`, Proposition `prop:fourier6`, Theorem `thm:finite`, Proposition `prop:purity`, Proposition `prop:cubiccap` and Theorem `thm:ten`; fractions written as "t = 1/2".
- Status: done.

**P4 | major | Correctness**
- Question: Do "any fourth basis", "the best approximate quadruples" and the Fourier-pair statements claim more than is proved?
- Answer: accepted.
- Edit: "any fourth basis" is always followed by "added to a triple for which the one-vector bound is certified"; the Fourier-pair statements carry "given the classical count of 156 cyclic 6-roots"; the abstract and conclusion now say that no bias-optimal and no game-optimal quadruple of C^6 contains the local triple, because two explicit quadruples beat every completion of it; the game is stated as inconclusive for the triples with the smaller bound; claim-table row 13 marks the Fourier-pair part as given a cited count.
- Status: done.

**P5 | major | Correctness, Attribution**
- Question: Is Proposition `prop:quartic` stated for the formulation that is proved, and how does it differ from the cited degree-four result of Sarkar?
- Answer: accepted.
- Edit: the sum-of-squares ladder is homogeneous throughout (level t: N^(t-2)(E_hom - gamma N^2) is a sum of squares of real forms of degree t; t = 2 is the proposition with optimum exactly 0, t = 3 our certificates, t = 4 Erlwein); the proposition says "homogeneous degree-four relaxation" and what `check_quartic_sos.py` verifies (own exact functional, 1,404 constraints, rank 63); the appendix states the identity as `cert/verify.py` computes it, including that the checker asserts and does not enforce symmetry of Q (the old text was wrong); the unproved statement about sphere multipliers removed; two sentences on the cited paper (a formulation with all basis amplitudes as variables against ours for a fixed triple), no priority claimed.
- Status: done.

**P6 | major | Novelty, Motivation**
- Question: Where is the ranked statement of what is new?
- Answer: accepted.
- Edit: new paragraph "What is new here, in order of strength" at the end of Section 1 (five items; the Lean-checked array form of the bridge inequality is part of item 3; the certificate for the local triple is called only a cross-check of Erlwein's exact value; structure results and dimension ten called secondary); the related-work paragraph reduced to attribution only.
- Status: done.

**P7 | major | Clarity, Interest**
- Question: Why does a quarter of the report (structure theory, dimension ten, a phase-ball proposition) sit on the main line?
- Answer: accepted.
- Edit: new order: question, trust map, what an outsider can check, the 2008 table, a number for the missing basis, then Section "Additional results, not used in the three answers" with the structure theory (about 1 page) and dimension ten (about 1.3 pages), then claim table, limitations, event work, conclusion; the phase-ball proposition stays in an appendix and is mentioned in one sentence marked "not used"; Lean table and E > 1/72 proof kept in the appendix. Main text about 30 pages, 50 in total. Whether the tag "reported, not re-run" was thinned as requested was not checked.
- Status: done.

**P8 | major | Motivation**
- Question: Why does the report not explain the quantum-information significance of N(6)?
- Answer: accepted.
- Edit: new paragraph "Why the number matters for quantum information" in Section 1: a state of a 6-level system has 35 real parameters, each basis gives 5 independent probabilities, seven mutually unbiased bases would give exactly 35 and three give 15, so optimal tomography and protocols using d + 1 bases are not available in dimension six; what Section 5 adds is a measurable quantity for how far.
- Status: done.

**P9 | major | Correctness**
- Question: Are the statements on the OpenAI Lean content and the three proofs firmer than the evidence read ("proves only 'at most five'", "real and mutually consistent", "by sorry")?
- Answer: partly accepted. The reviewer's clarification "a challenge file contains sorry by design" was not used because the cited working document does not say that; the remark was kept with a quotation from that document instead.
- Edit: abstract now says "according to its own scope note"; table 1 says "N(6) <= 5 only"; "real and mutually consistent" replaced by "agree in their conclusion"; the `by sorry` remark kept with the sentence that the file "is not itself a completed proof artifact" and "we did not examine any solution file".
- Status: done.

**P10 | minor | Correctness**
- Question: Does "17 of 26 corruptions detected" read as a quality grade without scale?
- Answer: partly accepted. The reviewer's proposed sentence "all 9 value-level corruptions pass undetected" is rejected as false: three of the nine misses are not value changes, and some inconsistent value changes are caught.
- Edit: abstract, contributions and limitations now say that the checker confirms counts, hashes and ranges and recomputes no inequality; of 26 deliberate corruptions it catches 17; the 9 it misses include every in-range change of a stored value that we applied consistently across copies (a phase, a radius, a stored bound, a seed center); "not a quality grade". Checked against the mutation table (9 misses: M05 M06 M09 M13 M14 M16 M20 M22 M26).
- Status: done.

**P11 | minor | Correctness**
- Question: Does the detection corollary for the Fourier-pair triples and the "must fail in d = 4" sentence overstate (settings not all local; d = 4 is a sanity check)?
- Answer: accepted.
- Edit: the Fourier-pair triples are no longer called local and the corollary says that their three settings are in general not all local; the abstract says that in dimension four no such test can succeed because a complete set of bases exists there.
- Status: done.

**P12 | minor | Attribution**
- Question: Are the explicit quadruples a reproduction of prior numerics?
- Answer: accepted.
- Edit: the game-optimal set is tagged as a reproduction of the value quoted in the McNulty-Weigert review (0.703888; the cited distance value of another reference is a different quantity); the low-bias set is described as obtained from 72 starts with an objective different from the cited distance. The editor kept the review as the cited source; the lead author should confirm.
- Status: done.

**P13 | minor | Attribution**
- Question: Is the hostile-review claim verifiable (number of rounds, issues found), and is the independent constellation search of the agent platform described where the checks are?
- Answer: accepted.
- Edit: the independent re-implementation was added to the near-miss checks (reproduces the smallest misfits of four shapes to ten digits). The number of rounds is not yet in Section 10.
- Status: open. Section 10 (v) still says only that the log "also says how many rounds were completed"; state "three rounds, 53 + 16 + 35 findings" there.

**P14 | minor | Clarity**
- Question: Are Krawczyk test, Arb, constellation, seed center, stage, root record, Cantelli and the random-access-code game explained at first use?
- Answer: accepted.
- Edit: glosses at first use for all of them; a paragraph "The OpenAI pipeline in three sentences" before the mutation table; the random-access game explained in Terms; constellation defined in Section 1.
- Status: done.

**P15 | minor | Clarity**
- Question: Why does the same triple have five names?
- Answer: accepted.
- Edit: "the local qubit-qutrit triple" once, then the symbol only; "canonical", "first" and "perfect local" removed from the text.
- Status: open. One sentence of the event-work section still says "the exact minimum energy on the canonical triple" (Lean identifiers with "canonical" are names and stay).

**P16 | minor | Correctness**
- Question: Is the inequality in Remark `rem:constant` supported?
- Answer: accepted. It is not (same as F1).
- Edit: the remark and all references deleted.
- Status: done.

**P17 | minor | Clarity**
- Question: Why do the supplementary documents carry names, an affiliation and draft remarks?
- Answer: accepted.
- Edit: supplementary PDFs replaced by copies with names, affiliation and repository address blacked out, with a README that gives the upstream revisions (the files are renamed by workstream).
- Status: open. The workstream C document still contains "independent human review and a team rehearsal are pending" and the README itself says the documents carry "review pending" status lines.

**P18 | minor | Clarity**
- Question: Why is an outline-only result stated as a proposition with a "proved" feel?
- Answer: accepted.
- Edit: the six-phase bound is now a remark tagged reported with the numerical confirmation (4,000 starts, largest value 5.7154760665 = 7 sqrt6/3).
- Status: done.

### Reviewer F: mathematics and report-versus-repository audit (F1 to F17)

Result in the reviewer's words: every proof is correct as a proof, except one false clause in an unused remark; the damage is in provenance, tags and repository agreement; no blocker.

**F1 | major | Correctness**
- Question: Does Remark `rem:constant` follow from part (a) of the bridge theorem (P >= 1/6 + ...)?
- Answer: accepted. Part (a) gives a deviation that can be negative; the correct bound is 1/6 + sqrt(gamma/18)/5.
- Edit: remark deleted (see P16).
- Status: done.

**F2 | major | Correctness, Consistency**
- Question: Why does Section 4 say "Four statements are established" when the six-phase bound is tagged reported?
- Answer: accepted.
- Edit: the sentence was replaced by a plain list of statements with their own tags (cube rank and cubic cap proved, six-phase bound a reported remark, quartic obstruction certified); a search finds no "established" in that section.
- Status: done.

**F3 | major | Correctness**
- Question: Is "0.0202 for the product orbit and lower for other classes" true, when orbit 16 has 0.0207?
- Answer: accepted. The reviewer is right (`d10/energy10.json`).
- Edit: corrected in Section "Dimension ten" and the claim table: the numerical minimum is 0.0202 for the Weyl-Heisenberg orbit, one other class is slightly higher (0.0207), 17 of the other 18 are lower, down to 0.0022; both numbers numerical.
- Status: done.

**F4 | major | Reproducibility**
- Question: Which program certifies the 156 cyclic 6-roots, the 108 non-unimodular ones, the 1e-78 enclosures and the 120 pair defects (the shipped `fourier6.py` certifies only 48 and decides orthogonality in floating point)?
- Answer: accepted. The reviewer's own brute force confirms the content.
- Edit: `d6_fourier/certify_d6_roots.py` (n = 6 version of the dimension-ten certifier), `certify_graph.py` and `check_partial_bases.py` were added to the repository and reproduce the funnel 156 = 48 + 108, the possibly-orthogonal graph and the partial bases. The report text was not updated: the caption of Table `tab:ten` still names `fourier6.py` as "the same pipeline", the Fourier-redo appendix still says 4,000 starts (the shipped script uses 6,000) and none of the three new scripts is named.
- Status: open.

**F5 | major | Reproducibility**
- Question: Where are the raw data and seeds of the 35-shape table, the 52,000-start counts, the 4.99e-3 long run and the explicit-example evaluation?
- Answer: accepted.
- Edit: raw search output and the scripts of the earlier repository were added under `near_misses/repo/`, and `near_misses/check_table.py` recomputes every table entry, the 389 and 695 of 52,000 counts, the level counts, the long run and the example check from them (bookkeeping on stored floating-point output, not a certificate).
- Status: done.

**F6 | major | Report against repository**
- Question: Why do `docs/verification_matrix.md` and `docs/verify_all.log` not exist, and why would `verify_all.sh` fail on three expected-output patterns?
- Answer: accepted.
- Edit: `docs/verification_matrix.md` (67 rows) written; `verify_all.sh` patterns regenerated from the actual output; `docs/verify_all.log` shows 40 steps passed, 0 failed (about 11 minutes on 2 cores); README lines corrected.
- Status: done.

**F7 | major | Report against repository**
- Question: Why do the ledger, `cert/README.md` and the d10 notes contradict the report (old rounded-up bounds, "pending" rows, missing scripts)?
- Answer: accepted.
- Edit: `docs/verification_ledger.md` replaced by a pointer to the matrix; the old values 0.038499999998 and 0.023499999997 no longer occur in `cert/README.md`, the README or the ledger; `hide_seek/RESULTS.md` corrected (369 and 5,000 shots).
- Status: done.

**F8 | minor | Correctness (rounding)**
- Question: Are upper bounds (bias, game loss, exclusion radius, residual) printed rounded down?
- Answer: accepted.
- Edit: `verify_sets.py` uses directed rounding; report now says bias <= 0.030223873, game loss <= 2.357826e-4, bias <= 0.040598666, game loss <= 6.180870e-4, 1.80e-5 for the exclusion radius, the interval end 7.32788656303687804425 for the lower end and 0.0234999999946 for the smallest 16-triple bound; the threshold sentence uses 0.030223873 and still passes.
- Status: open. `cert/verify.py` still prints the Frobenius bound with `%.3e`, giving 9.550e-15 for a true upper end of 9.55013e-15 (no effect on any conclusion).

**F9 | minor | Correctness (provenance)**
- Question: Is "every derived number was computed from the rounded-down values" true?
- Answer: accepted. The detection numbers use 0.0384999 and 0.0234999.
- Edit: sentence corrected: the bridge numbers use 0.03849999999 and 0.02349999999, the detection numbers the rounder 0.0384999 and 0.0234999 (shot counts identical for both, checked by the reviewer).
- Status: done.

**F10 | major | Clarity (leftover tokens)**
- Question: Why do five placeholders and an unfinished author field remain, and is a bibliography item unused?
- Answer: accepted.
- Edit: the three Lean tokens were replaced (P1). The title block still has `REPOLINK-PLACEHOLDER`, `COMMIT-PLACEHOLDER` and an author field "to be completed by the team"; the bibliography item `Steel04` is still not cited.
- Status: open. Fill the title block at submission (it is removed before the panel sees the text); cite or delete `Steel04`.

**F11 | minor | Report against repository**
- Question: Do line counts and start counts match the scripts?
- Answer: accepted.
- Edit: none.
- Status: open. Limitation 3 says `verify.py` has "its own 114 lines" (the file has 116); the Fourier-redo appendix says 4,000 starts (shipped script: 6,000); the "one stage-A shard (764 records)" of the first native rerun is not documented in `openai_check/`.

**F12 | minor | Report against script**
- Question: Does `finite_sample.py` enumerate the three-setting identity or one setting?
- Answer: accepted. It enumerates one setting; the identity follows by addition.
- Edit: none.
- Status: open. Section 6 still says "by full enumeration ... for N = 2, 3, 4" without "per setting".

**F13 | minor | Correctness**
- Question: Is "four of the 16 triples have the minima of the two product triples" proved?
- Answer: accepted. Only numerical coincidence is shown (a proof would use F_6 = H_2 tensor F_3 up to permutation and phases).
- Edit: none; the sentence is tagged numerical.
- Status: open. Write "numerically coincide with".

**F14 | minor | Consistency**
- Question: Is the ladder defined non-homogeneously while the proposition is proved homogeneously?
- Answer: accepted.
- Edit: see P5 (homogeneous ladder, "homogeneous" in the proposition).
- Status: done.

**F15 | minor | Consistency**
- Question: Is the dimension-ten clique enumeration certified or computed, and how long does the check take?
- Answer: accepted. Computed (exact graph combinatorics in software on a certified graph) is the honest tag.
- Edit: none.
- Status: open. The main text tags the clique enumeration "certified", the appendix "computed"; the reproduction block still says "about 2 minutes" (measured 17 s).

**F16 | minor | Clarity**
- Question: Is the 3 x 3 eigenvector statement in the coordinates appendix shown?
- Answer: accepted. The reviewer verified it and the Lean transport covers it.
- Edit: none.
- Status: open. Print the eigenvalue table in the proof.

**F17 | minor | Correctness**
- Question: Is the remark that the analytic bound 1/72 does not clear the bias threshold consistent (1/36 = 0.02778 < 0.030224)?
- Answer: rejected as a finding. The reviewer states it is not an error.
- Edit: none.
- Status: closed.

### Still open after cycle 3

Counts (35 findings: P 18, F 17): accepted 31, partly accepted 3 (P2, P9, P10), rejected 1 (F17); open 12 (P2, P13, P15, P17, F4, F8, F10, F11, F12, F13, F15, F16). Reviewers' own scores of the cycle (correctness of what is proved 9 of 10; correctness of what is claimed 7 of 10) are in their reports and are not repeated here.

- Report copy: `report/report.tex` and `report/report.pdf` in the repository (03:58) are older than the rebuilt report in the working folder (04:49) and must be replaced before submission.
- Title block, to be filled at submission: repository link, code-and-data commit, one author field (F10). The report title still says "how to see it" (open since cycle 1, S18).
- Pointers to the title block: one claim-table row and the words "submission repository" (P2).
- Number of review rounds not stated in Section 10 (P13).
- Wording: "canonical triple" in the event-work section (P15); "numerically coincide" (F13); "per setting" (F12); 114 against 116 lines and 4,000 against 6,000 starts (F11); tags and run time of the dimension-ten clique check (F15); eigenvalue table (F16).
- Fourier-pair funnel: name `certify_d6_roots.py`, `certify_graph.py` and `check_partial_bases.py` in the report and fix the caption of Table `tab:ten` (F4).
- Supplementary document of workstream C still carries a "review pending" line (P17). Printed Frobenius bound in `cert/verify.py` rounded to nearest (F8).
- Sentences of the cycle 3 list of unclear sentences not yet reworded, for example the abstract's "We do not offer a fourth proof" and "so these two entries become undecided".
- Not open as defects but not removable by editing: hypothesis (H), the cited count of 34,940 cyclic 10-roots, is not verified; the certificate checkers have had no human review (a pointwise float second implementation exists); the identification of the second product triple with the second McNulty-Weigert class is unchecked; Theorem `thm:finite` and the probability statements are not Lean-verified; the three 2026 proofs are not verified by us. The model versions of the AI agents are not named in the AI-use list (open since cycle 1, S4).
