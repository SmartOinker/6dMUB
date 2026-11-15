# Cycle 4: decisions of the lead author on `cycle4_panel_review.md` (findings 1..15, called Q1..Q15)

General: accept every finding unless listed otherwise. `/home/claude/build/SPEC.md` still applies. Never change a
number unless you re-check it. Keep all `\label`s that other files reference. American spelling, no em dashes.
This is the last large edit round: make the text shorter and plainer, do not add new claims.

## New facts
H1. Lean (Q1): the project `MUB6Bridge` now also contains `Bases.lean` (built; Lean v4.35.0, Mathlib v4.35.0, no
    sorry, standard axioms): for orthonormal bases of C^6, `bridge_bias` (for each vector f_j of the fourth basis
    some squared overlap with the triple deviates from 1/6 by at least sqrt(gamma/18)) and `bridge_game`
    (`gameScore B F <= 1/2 + sqrt(6)/12 - c* gamma/72`, where `gameScore` is DEFINED as 1/2 + (1/72) times the
    average of the six pair sums). A further file with the corollaries for the two product triples as statements
    about bases, and the remaining shot-count arithmetic, is being added. Honest wording everywhere: "Lean-verified:
    the cap inequality of Lemma lem:sqrt and Theorem thm:bridge as inequalities about orthonormal bases of C^6, with
    the game score defined by its formula; NOT Lean-verified: that this formula is the optimal success probability
    of the random-access code (cited), the equality cases of the lemma, the energy certificates, and every
    probability statement." The lead author rewrites the Lean paragraph and table.
H2. OpenAI Lean (Q2): a first-hand reading of the pinned OpenAI repository's Lean scope note is being prepared
    by a helper; the lead author will insert a short "Verified versus headline" paragraph in Section 2. Editors of
    Section 2: do not rewrite the Lean-status paragraph beyond the wording fixes below.
H3. Text layer (Q3): the assembler will make sqrt(6) and the simple fractions 1/2, 1/6 readable in the PDF text
    layer automatically. Editors: do NOT add more "In plain text" lines; keep the existing ones.

## Decisions by finding
- Q4 (focus and length), binding page budgets for main-text and appendix fragments (compile to check):
  * `s1_question.tex` (Sections 1 to 3): at most 5 pages. Delete the paragraph "Three questions and what we found"
    if it repeats the abstract and reading guide (keep a three-line version), keep "why it matters", "terms",
    "what is new, in order of strength", related work (shortened), roadmap (3 lines).
  * `s5_const.tex` (2008 table): at most 2.5 pages.
  * `s6a_number.tex`: at most 4.5 pages. `s6b_hide.tex` is the lead author's.
  * `s4_structure.tex` + `s7_ten.tex` together: at most 1.75 pages; delete the dimension-seven sentence; dimension
    ten in at most 12 lines of prose plus the theorem and the small table.
  * `s4_structure_app.tex`: at most 3.5 pages: keep the statement and full proof of E > 1/72 ONLY IF it fits in
    1.5 pages, otherwise a proof outline with the key inequalities; keep the Lean table of workstream B; every other
    structure proof becomes a two-to-four-line proof idea with a pointer to the section of the supplementary
    structure paper (do not cite its file name; say "supplementary structure paper, Section N").
  * `s5_const_app.tex`: near-miss certificate at most 1.25 pages; the 35-row table stays; phase-ball appendix at
    most half a page (statement, proof idea in four lines, "not used elsewhere"); Fourier-pair redo at most
    three quarters of a page.
  * `s7_ten_app.tex`: at most 1.25 pages.
  * `s6_number_app.tex`: see Q5.
- Q5: in `s6_number_app.tex` state plainly that \cite{Erlwein} is an unrefereed manuscript with a verification
  bundle; add one sentence on what an independent person needs to re-run the checker (two commands, two seconds,
  Python with python-flint); the lead author appends the checker source as a listing after your text: end the
  appendix with the line `% VERIFY-LISTING-HERE`.
- Q6: (a) fix the cross-reference for the game (defined in `sec:bridge`); (b) `\Tz` is defined in Section 1: say
  "defined in Section~\ref{sec:question}"; (c) no "title block" pointers: cite the hash in the text; (d) rename the
  tests T1..T5 of the near-miss appendix to C1..C5 and any other map called T to another letter (the statistic T of
  the detection theorem and the triples keep their names); (e) reading guide is the lead author's; (f) define or
  remove orbit numbers.
- Q7: (a) explain the 27,189 versus 27,188 records in one clause from the audit document
  (`/home/claude/src_text/fanghao.txt`); (b) verify.py is "about 120 lines" everywhere; (c) explain once the pooled
  runs behind "52,000" (50,000 + 2,000 starts; seeds 101/102 and 2026) and the 6,000-start run (seed 77); (d) lead
  author; (e) add the pointer for "no four bases can score more than mu" (Lemma `lem:sqrt` summed over a pair, or
  the Lean declaration `pairSum_le`).
- Q8: replace "agree with 2008 within sampling error" by an accurate sentence naming the shapes that differ by
  more than sampling error ({5,4,2,1}: 92.92% versus 99.70%; {5,5,1,1}: 95.40% versus 92.85%; check the table) and
  say that we do not explain the difference (different optimizer and tolerance are possible reasons, not shown).
- Q9: (a) Theorem `thm:bridge`: "Fix $\gamma>0$ and suppose $\E(\psi)\ge\gamma$ for every unit vector $\psi$";
  (b) "bias" is our name for the largest deviation; the game is that of \cite{ABMP}; (c) game loss is defined as
  $1/2+\sqrt6/12$ minus the score (exact), with the decimal as a value; (d), (e), (f): lead author.
- Q10: lead author (AI-use section). In Section 3 use "workstream" exactly as defined in the reading guide (one
  team member working with AI agents).
- Q11: tags: Proposition `prop:quartic` gets the single tag `\stexact` (new macro "[computed, exact arithmetic]",
  added to the preamble by the lead author); replace stacked tags "\stproved\ from \stcert\ inputs" by the single
  macro `\stgiven` ("[proved here, given certified inputs]", also added to the preamble); drop `\stproved` from
  one-line observations; write "the second sentence uses the classical count 156 \cite{BF91}".
- Q12: state the cleaner fact: ONE explicit quadruple (the game-optimized one) beats every completion of `\Tz` on
  BOTH measures (bias at most 0.040598666 against more than 0.046248; game loss at most 2.357826e-4 against more
  than 3.302e-4); the second quadruple has the lowest bias we found (at most 0.030223873). Check both numbers with
  `cert/verify_sets.py` output before writing. Keep "for the second product triple the game comparison is
  inconclusive".
- Q13: dimension ten: reduce as in Q4; say that (H) is known to us only from a table in \cite{FR15} (crediting
  \cite{Faugere02}) and that what the proof needs is an upper bound on the number of complex roots.
- Q14: Section 3: say before the number that the checker's documented scope is counts, hashes and ranges, and
  call the result "confirms the documented scope"; add one sentence on what a stronger checker would recompute.
- Q15: abstract is the lead author's.

Report back in under 100 words: page counts before/after for each of your fragments, what you could not do.
