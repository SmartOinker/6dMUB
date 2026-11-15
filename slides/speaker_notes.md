# Speaker notes: The missing fourth basis in dimension six

Caltech x SAIR Mathathon, Problem 124. Speaking rate planned at about 130 words per minute. Slide numbers are the content-slide numbers shown on the slides; the title slide is slide 0. Every number and claim below is taken from the revised report (49 pages); if a number here differs from the report, the report wins.

## Timing table

| Slide | Title | Time | Words in script | Words at 130 wpm |
|---|---|---|---|---|
| Title | The missing fourth basis in dimension six | 0:40 | 92 | 87 |
| 1 | In dimension six, three mutually unbiased bases are easy to build and a fourth has never been found | 1:50 | 223 | 238 |
| 2 | Three 2026 computer proofs say N(6)=3, and none is formally verified end to end | 1:20 | 166 | 173 |
| 3 | We reran what an outsider can rerun: the checker catches 17 of 26 corruptions, and the rebuilt parts match bit for bit | 1:20 | 179 | 173 |
| 4 | We can prove structure for order-six Hadamard matrices, but the universal step toward N(6)=3 is still open | 1:40 | 225 | 217 |
| 5 | No pure state hides from the local triple: its energy is above 0.0384999, which is 99.3% of the exact minimum | 1:30 | 200 | 195 |
| 6 | A 10^-7 threshold accepted two near-misses, so "found numerically" is not "proved" | 1:10 | 147 | 152 |
| 7 | One certified vector bound forces every fourth basis to be far from unbiased, farther than explicit quadruples | 2:00 | 261 | 260 |
| 8 | Hide and seek is a theorem: with 1,936 shots per setting, a collision test flags every pure state as not white noise | 2:30 | 335 | 325 |
| 9 | Dimension ten with the same method: 34,940 certified cyclic roots funnel down to 1,136 candidate bases, and none extends | 1:20 | 169 | 173 |
| 10 | In dimension ten, no four MUBs contain the standard and Fourier bases, if the cited root count holds | 1:30 | 209 | 195 |
| 11 | Claims and status, in one table | 1:00 | 136 | 130 |
| 12 | AI did most of the computing and drafting, so every lower bound is a certificate with a short checker | 1:10 | 154 | 152 |
| 13 | Three questions, three answers, and what stays open | 1:00 | 131 | 130 |
| **Total** | | **20:00** | 2627 | 2600 |

Check: 0:40 + 1:50 + 1:20 + 1:20 + 1:40 + 1:30 + 1:10 + 2:00 + 2:30 + 1:20 + 1:30 + 1:00 + 1:10 + 1:00 = 20:00. Backup slides are untimed and used only for questions.

## Title slide

**Headline on slide:** The missing fourth basis in dimension six

**Time:** 0:40

Good morning. We are Ren Jie Tee, Xinrui and Raymond Fong How, and this is our talk on Problem 124, mutually unbiased bases in dimension six. The title carries our three questions: what is verified, how far away is a fourth basis, and how would one see it. Every claim on every slide has a small colored tag that says how we know it: proved here, Lean-checked as reported, interval-certified, computed, numerical only, cited, conditional, open, or reported and not re-run by us. Everything on a slide is also in our report.

**If asked:** Q: Did you prove that N(6) is 3? A: No. We did not prove it and we did not verify the three 2026 proofs. We checked parts of them and turned their conclusion into numbers.

## Slide 1. The question

**Headline on slide:** In dimension six, three mutually unbiased bases are easy to build and a fourth has never been found

**Time:** 1:50

Two orthonormal bases of six-dimensional space are mutually unbiased if every overlap between a vector of one and a vector of the other has squared modulus one sixth. Physically they are complementary measurements: certainty in one means complete randomness in the other. Write six as two times three, a qubit times a qutrit. Take the three qubit bases, the eigenbases of the Pauli operators Z, X and Y, and tensor them with three mutually unbiased qutrit bases: the standard basis, the Fourier basis F three, and a twisted Fourier basis D F three. That gives three mutually unbiased bases of the six-level system, and each can be measured locally, with no entangling gate. The picture shows these three settings, and the question mark is the fourth basis that nobody has found. In prime power dimensions you can always reach d plus one bases. Six is the first dimension where that fails to be clear. Zauner conjectured in 1999 that three is the maximum. In 2026, three computer-assisted preprints claim to prove it. The next case of the same shape, dimension ten, is open. So we ask three questions about the claim: how do we know, by how much, and what would one see in a laboratory. Along the way we say what is ours, what is prior work, and what is only numerical.

**If asked:** Q: Why not just trust three independent proofs? A: They are not independent in method. One re-implements another, all three were AI-assisted according to their authors, and none is formal end to end. That is the next slide.

## Slide 2. What was proved: trust map

**Headline on slide:** Three 2026 computer proofs say N(6)=3, and none is formally verified end to end

**Time:** 1:20

This table is a trust map of the three preprints. Everything in it is cited; reading is not verification, and we did not re-derive any of it. OpenAI covers the space with about two hundred fifty thousand seed centers and runs a graph search to exclude two further bases, in double precision. Its Lean development proves only that N of six is at most five. Jaswal re-implements the same method with binary64 intervals and has no Lean; our description of that one rests on a summary. Cardenes Wuttig and Tindall use a connectedness argument with ball arithmetic. Their Lean theorem takes the numerical certificate as a hypothesis, and the numbers sit outside Lean. So, to our reading, nothing is formal end to end, and the proofs share a method and a trusted base. The box at the bottom is the tag legend. Interval-certified means a short program checked it in ball or exact arithmetic. Reported means a teammate ran it and we did not re-run it.

**If asked:** Q: Are you saying the proofs are wrong? A: No. We say what each rests on. We found no error, and we did not verify them.

## Slide 3. What we checked

**Headline on slide:** We reran what an outsider can rerun: the checker catches 17 of 26 corruptions, and the rebuilt parts match bit for bit

**Time:** 1:20

So we checked what an outsider can check. OpenAI's record checker runs unmodified and reproduces the counts of the preprint. To learn what its pass means, we made twenty-six small corruptions of the saved records, one at a time. It caught seventeen and missed nine: two harmless, seven scope gaps. It confirms bookkeeping, counts and ranges, and recomputes no inequality. We ran the whole test twice, the second time by a separate agent at the pinned upstream revision, with identical verdicts. That is a statement about the checker, not a flaw in the theorem. We also rebuilt the seed cover and two stage-C batches of the published programs: bit-identical, though on the preprint's own toolchain, so independence is weak. The full native rerun, one hundred invocations with eight principal files byte-identical, is workstream C's, and we did not re-run it, so it carries the reported tag. Byte agreement shows reproducibility, not that the covering lemmas are right. Finally we redid the Fourier pair from scratch: one hundred fifty-six, forty-eight, sixteen, and no fourth basis, given the classical root count.

**If asked:** Q: Does 17 of 26 mean the proof is 65 percent right? A: No. The mutations were ours, not from the real run. They show what the checker does not check.

## Slide 4. Toward a proof a human can read

**Headline on slide:** We can prove structure for order-six Hadamard matrices, but the universal step toward N(6)=3 is still open

**Time:** 1:40

Our second theme is structure, from workstream B, for complex Hadamard matrices H of order six. The entrywise cube of H has a rank. First box: that rank is at most two exactly when H is in the Fourier family, a transpose of it, or the cubic Tao class. This is proved, with one cited ingredient, the classification of Hadamard matrices with an order-three subblock by Cardenes Wuttig and Tindall. Second box: outside the Tao class, the squared operator norm of the cube is at most eighteen, and a trace bound has equality exactly when the cube rank is two. That is proved, and the identities were checked numerically. Third box: six unit phases summing to root six have a sum of cubes of modulus at most seven root six over three. The written proof is workstream B's and we did not re-derive it, so it is reported, and a numerical search confirms it. Fourth box: a degree-four sum-of-squares relaxation of the energy has optimum exactly zero, with a rank sixty-three pseudomoment matrix. Our own functional is verified in exact arithmetic; workstream B's is reported. The last box is the step that would finish the argument: residual products vanishing on all compatible triples. It is unproved. Norm eighteen implying cube rank two is also unproved. Nothing here yet bounds the number of mutually unbiased bases.

**If asked:** Q: Is the cubic cap new? A: The reduction and the cap are workstream B's, with a cited Fourier condition from the Cardenes Wuttig and Tindall paper. We do not claim priority beyond that, and it does not bound N(6).

## Slide 5. No hidden state

**Headline on slide:** No pure state hides from the local triple: its energy is above 0.0384999, which is 99.3% of the exact minimum

**Time:** 1:30

Now the number. For a state psi, the energy E is the sum, over the eighteen outcomes of the three local measurements, of the squared deviation of the outcome probability from one sixth. E is zero exactly when the state is unbiased to all three bases, which is what a fourth basis vector would have to be. So how small can E be? The number line shows what is known. At degree four, sum-of-squares certificates give nothing: zero. An analytic bound of one over seventy-two, about 0.0139, was built in Lean by a teammate; we report it and did not re-run the build. Our degree-six certificate, checked in interval arithmetic, gives E above 0.0384999; the nominal level is 0.0385. The exact minimum, four minus root six over forty, about 0.03876, is prior work of Erlwein at degree eight. So our bound is an independent certificate of ninety-nine point three percent of his exact value, at lower degree. It is not a new bound on this triple. What the same pipeline adds is the second product triple and all sixteen triples that contain the standard and Fourier bases: E above 0.0234999, given the classical count of one hundred fifty-six cyclic six-roots.

**If asked:** Q: Is 0.0385 new? A: No. Erlwein has the exact value (4 - sqrt 6)/40 = 0.03876. Ours is an independent certificate at degree six. What is new is the same certificate for the second product triple and the 16 Fourier-pair triples.

## Slide 6. Why certificates

**Headline on slide:** A 10^-7 threshold accepted two near-misses, so "found numerically" is not "proved"

**Time:** 1:10

Why certificates? Because of a table from 2008. Brierley and Weigert searched for partial fourth bases, called constellations, and counted a shape as found when a function fell below ten to the minus seven. We reran the search for two shapes, five-four-four-one and five-five-three-one, and certified in interval arithmetic that the lowest points reached are strict local minima of the misfit with nonzero value: one point zero two five times ten to the minus three, and seven point three three times ten to the minus four. The 2008 function there is two point nine and one point five times ten to the minus eight, below the threshold. So these points pass the 2008 acceptance test, and the two entries become undecided, not refuted. We do not prove those shapes empty. Conversely, the shape five-three-three-three exists, yet one start in twenty thousand finds it. Thirteen shapes remain undecided.

**If asked:** Q: So are those two shapes empty? A: We do not know. We certified that the points we found are not solutions. The misfit might vanish elsewhere.

## Slide 7. From a vector to a basis

**Headline on slide:** One certified vector bound forces every fourth basis to be far from unbiased, farther than explicit quadruples

**Time:** 2:00

A bound on one vector is not yet a statement about a measurement. Here is the bridge. The formula on top is an elementary inequality: the square root of p is at most its tangent line at one sixth, minus c star times the squared deviation, with c star about 0.6176. The proof is a few lines and is in the backup. Summing it over the overlaps of two bases gives the theorem. If the energy is at least gamma on every unit vector, every fourth basis has bias at least the square root of gamma over eighteen, and loses at least c star gamma over seventy-two in the random-access game, compared with four mutually unbiased bases. With E above 0.0384999, the bias exceeds 0.046248 and the game loss exceeds three point three zero two times ten to the minus four. Now compare with explicit sets. We found two quadruples numerically, one minimising bias and one maximising the game score, and certified their numbers in interval arithmetic: bias at most 0.030224 and game loss at most two point three five eight times ten to the minus four. Both beat every completion of the perfect triple. That is the design lesson: the best approximate quadruples are not completions of the perfect local triple. For the second product triple, bias above 0.036132 and loss above two point zero one five times ten to the minus four, the bias lesson holds, but the game comparison is inconclusive. These bounds cover every fourth basis, because the proof uses only the energy bound on single vectors.

**If asked:** Q: Does this show no fourth basis exists? A: No. It concerns quadruples that contain one of the triples we examined. We have no certified lower bound over all quadruples, and that is open.

## Slide 8. Hide and seek

**Headline on slide:** Hide and seek is a theorem: with 1,936 shots per setting, a collision test flags every pure state as not white noise

**Time:** 2:30

What would this look like in a laboratory? Play hide and seek. A hider prepares the same pure state of a qubit and a qutrit again and again and tries to look like white noise to the three local measurements. A referee takes N shots in each setting and computes a statistic T: the fraction of pairs of shots with equal outcomes, summed over the three settings, minus one half. T is an unbiased estimator of the energy, and Pearson's chi-square statistic equals fifteen plus six times N minus one times T, exactly. This is now a theorem with a finite-sample guarantee. With 1,936 shots per setting, every pure state is flagged as not white noise with probability at least ninety-five percent, and the false-alarm probability is at most point one percent. With 5,142 shots the figures are ninety-nine percent and point one percent. The proof is in the backup: Hoeffding's variance formula and Cantelli's inequality. The curve on the left is the older large-sample rule of thumb: 239 shots for ninety-nine percent at point one percent false alarm. That is an approximation, checked by simulation, and optimistic below a hundred shots, so we do not call it a theorem. The dashed line is the dimension-four control, where a hiding state exists. It is never caught. The table gives total shots under gate noise, in the large-sample model: 589, 594, 646 and 1,500 at two-qubit error zero, point one, one and ten percent. There is also a purity witness: statistics exactly uniform in the three settings force the largest eigenvalue of the state to be at most 0.8232. What is new? Not the test: it is the classical collision test of Goldreich and Ron, and Paninski. The idea that strongly unextendible triples separate pure from some mixed states is due to Grassl, McNulty, Mista and Paterek in 2017. Ours is feeding the test the certified energy gap. The game needs 9.37 times ten to the seven rounds, a different question. No hardware run was done.

**If asked:** Q: Is the detection test new? A: No, the test is classical: the collision test for uniformity (Goldreich and Ron, Paninski, with Hoeffding's variance formula). The idea that strongly unextendible triples separate pure from some mixed states is Grassl, McNulty, Mista and Paterek's. What is new is feeding it the certified energy gap, which gives a guarantee for every pure state with three fixed local settings.

## Slide 9. Ten, same method

**Headline on slide:** Dimension ten with the same method: 34,940 certified cyclic roots funnel down to 1,136 candidate bases, and none extends

**Time:** 1:20

Now dimension ten, with the same method. A vector unbiased to the standard basis and the Fourier basis corresponds to a unimodular cyclic ten-root. Cyclic ten-roots solve a polynomial system, and the literature reports 34,940 solutions. We regenerated all 34,940 and certified each one inside the repository with Krawczyk tests in ball arithmetic: 3,040 are unimodular, so they are the vectors we need, and 31,900 are certified not unimodular. Among the 3,040, 57,680 pairs could be orthogonal, and they form exactly 1,136 candidate bases. No pair of candidate bases is mutually unbiased, and no vector is unbiased to a candidate triple. On the right is the calibration: the same pipeline in dimension six returns the known counts, 156, 48 and 16. The bars are on a log scale, so dimension ten is wider but the shape is the same. Counts and margins were recomputed by separate code. The completeness of the root list rests on one hypothesis, the cited root count, which we come to on the next slide.

**If asked:** Q: Why trust the pipeline? A: In dimension six it reproduces Grassl's known counts. It reportedly recovers a complete set of eight bases in dimension seven, which we mark as reported.

## Slide 10. Ten: theorem and limits

**Headline on slide:** In dimension ten, no four MUBs contain the standard and Fourier bases, if the cited root count holds

**Time:** 1:30

Here is the dimension ten theorem, and it is conditional. Hypothesis H: the cyclic ten-roots system has at most 34,940 solutions. That count is a Groebner basis computation attributed to Faugere, known to us through a table in the literature, and we did not verify it. Assuming H, for every vector unbiased to I and the Fourier basis, and each of the 1,136 candidate bases, some vector of the basis has squared overlap at least 0.04178 away from one tenth. So no triple extends, and no four mutually unbiased bases of C ten contain the standard and Fourier bases. Grassl, McNulty, Mista and Paterek built unextendible sets of at most three bases up to dimension sixteen in 2017. To our reading, their dimension-ten example, where it contains these two bases, is a special case of our theorem, and their result does not depend on H. We did not reproduce their computation. We add the complete certified list of 1,136 candidates, with margins. Limits: only triples containing that pair, nothing about N of ten. The fallback without H rests on a mixed-volume value, 35,940, that we did not recompute. One point two million random starts support H but do not prove it. No certified energy bound exists in dimension ten.

**If asked:** Q: Is the dimension-ten result a theorem? A: Yes, as a computer-assisted theorem conditional only on H, the cited count of at most 34,940 cyclic 10-roots, which we did not verify. The roots themselves are all certified in the repository.

## Slide 11. Claims and status

**Headline on slide:** Claims and status, in one table

**Time:** 1:00

This table is the whole talk in one place. Read down the status column. Cited: that no end-to-end formal proof exists, to our reading, and Erlwein's exact minimum, which is prior work. Computed: the checker test and the partial rebuild. Reported, not re-run: the full native rerun by workstream C, and the six-phase bound. Proved here: the cube-rank criterion with a cited ingredient, the cubic cap, the bridge theorem and the detection guarantee, the last two from certified inputs. Lean-checked as reported: one over seventy-two, by a teammate. Interval-certified: the energy bounds, the exact degree-four obstruction, and the 2008 near-misses. Conditional: dimension ten. Open: the universal step. The who column uses our three workstreams: A for certificates, bridge, detection test and dimension ten, B for structure theory and Lean, C for the audit and full rerun.

**If asked:** Q: Which claims are formally verified? A: Only the energy bound one over seventy-two, in Lean, by a teammate, reported, and we did not re-run it. No Lean claim is made for the bridge lemma.

## Slide 12. AI use and limits

**Headline on slide:** AI did most of the computing and drafting, so every lower bound is a certificate with a short checker

**Time:** 1:10

We used AI heavily: Claude for workstream A, Codex for B and C, and open-weight agents on the event platform. The team chose the questions and reviewed outputs, but we never rely on a model's word. Every certified bound has a checker in ball arithmetic, separate from the program that found it. We calibrated on known answers: ninety-nine point three percent of Erlwein's value, the counts 156, 48 and 16, and the dimension-four control. Every claim that is not a citation was recomputed at least once by other code, except the teammate's Lean build and full native rerun, and two single-run records. Fresh AI reviewers attacked the report in logged rounds. Not checked: we verified none of the three 2026 proofs. We do not claim line-by-line human refereeing of every proof. The checkers and dimension-ten code were not reviewed line by line by a human. Lean covers only one over seventy-two. No hardware run.

**If asked:** Q: Could the certificate checker itself be wrong? A: Yes. It is about 100 lines and no second person or independent program has reviewed it. Its output agrees with Erlwein's independent exact value to 0.7 percent, which is our main external check.

## Slide 13. Summary

**Headline on slide:** Three questions, three answers, and what stays open

**Time:** 1:00

To summarize. How do we know? None of the three proofs is formal end to end. The checker catches seventeen of twenty-six corruptions, a teammate reports a full rerun, and two 2008 entries are certified near-misses, now undecided. By how much? Every pure state has energy above 0.0384999; every fourth basis added to the local triple has bias above 0.046248 and game loss above three point three zero two times ten to the minus four. Dimension ten, conditionally, the same flavor. What would one see? With 1,936 shots per setting, a guarantee, every pure state is exposed; 239 is the rule of thumb; no hardware run. Open: the universal step, hypothesis H, a bound over all quadruples, hardware, and a formal bridge theorem. Thank you; we are happy to take questions.

**If asked:** Q: What is the one thing you would do next? A: A certified energy bound over all mutually unbiased triples of C six, to which the bridge theorem and the finite-sample theorem then apply unchanged.

## Backup slides (untimed)

B1 proof of the square-root lemma; B2 the finite-sample theorem, statement and a three-line proof sketch (collision statistic T, exact variance by Hoeffding's formula, Cantelli's inequality); B3 degree-six certificate method and what the checker trusts (E > 0.03849999999 from the nominal level 0.0385 minus S <= 2.189e-12); B4 sharp phase-ball radius; B5 six-phase bound and quartic SOS obstruction; B6 second product triple and the 16 Fourier-pair triples (E > 0.0323999 for 12, E > 0.0234999 for 2, E > 0.0384999 for 2; every fourth basis added to any of them has bias above 0.036132, above 0.030224); B7 mutation-test breakdown.

## Q&A preparation

**1. Is the detection test new?**

No. The test is the classical collision test for uniformity (Goldreich and Ron; Paninski), analyzed with Hoeffding's variance formula for U-statistics and Cantelli's inequality. The qualitative idea that strongly unextendible triples separate pure states from some mixed states is due to Grassl, McNulty, Mista and Paterek (2017). What is new is feeding the test the certified energy gap: that turns it into a finite-sample guarantee for every pure qubit-qutrit state with three fixed local settings (1,936 shots per setting for 95 percent detection at 0.1 percent false alarm). We also give a purity witness: exactly uniform statistics force the largest eigenvalue of the state to be at most 0.8232.

**2. Why 1,936 and not 239?**

Guarantee versus approximation. 1,936 shots per setting come from the finite-sample theorem and its corollary: no large-sample approximation, a Chebyshev-type (Cantelli) bound, so it is conservative (5,142 shots for 99 percent). The figure 239 is the large-sample rule of thumb (99 percent detection, 0.1 percent false alarm), from a noncentral chi-square model with 15 degrees of freedom. It is an approximation, checked by simulation, and optimistic below N = 100 (model 0.108 against simulated 0.098 at N = 50). The two answer different questions: 239 is what an experimentalist should expect, 1,936 is what we can prove.

**3. Is 0.0385 new?**

No. The exact minimum (4 - sqrt6)/40 = 0.03876 on the canonical triple is prior work of Erlwein, with a degree-eight certificate. Our certified inequality E > 0.0384999 (nominal level 0.0385) is an independent degree-six certificate, 99.3 percent of his value, not a new bound on that triple. What the same pipeline adds, to our knowledge: certified bounds E > 0.0234999 for the second product triple and for all 16 triples containing the standard and Fourier bases (given the classical count of 156 cyclic 6-roots), the bridge from one vector to a whole basis, and the detection guarantee.

**4. Is dimension ten a theorem?**

Yes, as a computer-assisted theorem conditional only on hypothesis (H), the cited count of at most 34,940 cyclic 10-roots (Fuhr and Rzeszotnik, crediting Faugere), which we did not verify. All 34,940 roots are now regenerated and certified inside the repository (3,040 unimodular, 31,900 certified not unimodular), and the margin 0.04178 is certified in ball arithmetic. Without (H) the fallback of at most 1,000 further roots rests on a mixed-volume value 35,940 reported by an auxiliary session and not recomputed. To our reading, the dimension-ten example of Grassl, McNulty, Mista and Paterek (2017), where it contains the standard and Fourier bases, is a special case, and their result does not depend on (H). There is no certified energy bound in dimension ten, and the theorem says nothing about N(10).

**5. Did you verify the 2026 proofs?**

No. We mapped what each rests on (two from their repositories, one from summaries), reran OpenAI's record checker, corrupted its saved records on purpose (17 of 26 detected, run twice with identical verdicts), and rebuilt the seed cover and two stage-C batches bit for bit on the preprint's own toolchain. A teammate (workstream C) did a full native rerun with 8 principal files byte-identical, which we did not re-run. Reproducing outputs does not check the mathematics that connects them to the theorem.

**6. Is anything in Lean?**

Only E > 1/72 on the canonical triple, built by a teammate (workstream B) and reported; we did not re-run the build, so it carries the tag Lean-checked, as reported. The report also lists some of B's structure declarations (a counting step, the cubic cap with a Fourier condition as premise, the final envelope step of the six-phase bound) with the same tag. The bridge lemma has a Lean draft in the repository that has never been compiled, and no claim in the report is Lean-verified by it, so we make no Lean claim for it. The Lean part of the OpenAI proof covers N(6) <= 5 only; nothing is formal end to end.

**7. What did a human check?**

We do not claim line-by-line human refereeing of every proof. The team chose the questions and reviewed outputs. The proofs were written with AI assistance and cross-read by AI agents and scripts; certificates are checked by separate short checkers in ball arithmetic; every claim that is not a citation was recomputed at least once by another program (exceptions: the teammate's Lean build and full native rerun, and two single-run records). The hostile review rounds were done by fresh AI reviewers and are logged; the log records no human participant. The certificate checker (about 100 lines) has not been reviewed by a second person.

**8. What do the 2008 near-miss values mean?**

The values 1.02497683851953e-3 and 7.32788656303688e-4 are the misfit mu = ||r||_2 at certified strict local minima of the shapes {5,4,4,1} and {5,5,3,1}. The 2008 function F = mu^2/36 there is 2.9e-8 and 1.5e-8, below the 2008 threshold 1e-7. So the 2008 acceptance test accepts them, and the two entries become undecided, not refuted. We did not prove the shapes empty, and we certified only the lowest level found for each shape.

**9. Does the cubic norm cap prove N(6)=3?**

No. We proved the cap ||H^o3||^2 <= 18 for order-six Hadamard matrices outside the Tao class (with a cited Fourier condition), and that the trace bound is an equality exactly when the cube rank is two. Whether norm 18 forces cube rank two is not proved, and neither is the universal step (vanishing of the residual products on all compatible triples) that would finish the argument. Nothing in the structure section yet bounds the number of MUBs.

**10. What does the Fourier-pair result add?**

All 16 triples that complete {I, F_6} have interval-certified energy: E > 0.0323999 for 12, E > 0.0234999 for 2 and E > 0.0384999 for 2, so every fourth basis added to any of them has bias above 0.036132, which exceeds the explicit quadruple's 0.030224. This holds given the classical count of 156 cyclic 6-roots, and only for quadruples containing that pair, not for all quadruples. For the game the comparison is conclusive for the 14 triples with E > 0.0323999 and inconclusive for the other two.
