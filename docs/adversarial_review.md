# Adversarial review log

## How the review works

After each full draft of the report, fresh AI reviewers (model family: Claude Sonnet) are started with the report, the team's source documents, the codebase and the competition rules, but without the drafting history. They act as hostile but fair judges for the six criteria of the panel (correctness, novelty, attribution, clarity, motivation, interest) and return numbered findings with a severity (blocker, major, minor), a question a judge would ask, what they checked, and a proposed fix. The lead author (also an AI) decides on every finding in writing; AI editor agents apply the decisions to the report and the repository and keep an edit log. No human took part in the review cycles recorded here. After the edits, the claims below were re-checked by searching the revised report and the repository (a change is marked "done" only if it was found there). Findings that were not fully fixed are marked "open".

Entry format: id, severity, criterion, the attack as a question, our answer (accepted, partly accepted, rejected) with the reason, the edit made, and the status.

| cycle | reviewers | findings (blocker/major/minor) | main changes |
|---|---|---|---|
| 1 | 2 fresh AI reviewers (correctness and consistency; novelty, attribution, clarity, motivation, interest) | R: 3/14/11 (28); S: 4/12/9 (25); total 7/26/20 (53) | New finite-sample detection theorem replaces the "guaranteed floor"; abstract, contributions table, claim table, limitations, AI-use section rewritten and a Conclusion added; introduction rewritten to motivate the problem; near-miss and dimension-ten claims restated with their conditions; status tags corrected; 20 references and a related-work paragraph added; five independent check scripts and a dimension-ten regeneration added to the repository; team-internal references removed from the body. 23 of 53 findings remain open (see the end of Cycle 1). |

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
