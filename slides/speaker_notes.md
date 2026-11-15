# Speaker notes: The missing fourth basis in dimension six

Caltech x SAIR Mathathon, Problem 124. This file contains the speaker script for each slide (slide numbers are the content-slide numbers shown on the slides; the title slide is slide 0), a timing table, and Q&A preparation.

## Timing table

| Slide | Headline | Time | Words in script | Words at 130 wpm |
|---|---|---|---|---|
| Title | The missing fourth basis in dimension six: what is verified, how far away it is, and how to see it | 0:40 | 85 | 87 |
| 1 | Unbiased bases are complementary measurements: certainty in one means pure chance in every other | 0:55 | 123 | 119 |
| 2 | In dimension six only three complementary bases are known, so state determination gets 15 of the 35 numbers it needs | 0:45 | 102 | 98 |
| 3 | Three 2026 computer proofs say N(6)=3; to our knowledge none is formally verified end to end, and they share a method | 1:20 | 171 | 173 |
| 4 | The OpenAI record checker misses every consistent in-range value change we tried | 1:00 | 130 | 130 |
| 5 | A full native rerun of the OpenAI pipeline reproduces its eight output files byte for byte | 0:30 | 68 | 65 |
| 6 | A 10^-7 threshold in the 2008 table admitted two certified near-misses, so "found numerically" is not "proved" | 1:20 | 177 | 173 |
| 7 | No pure state is unbiased to the local triple T0: its energy exceeds 0.0384999, 99.3% of the exact minimum | 2:00 | 257 | 260 |
| 8 | A one-vector bound becomes a bound on every fourth basis; Lean checks it as inequalities, given the energy bound | 2:00 | 243 | 260 |
| 9 | One explicit quadruple beats every completion of the local triple on both measures; another reaches bias 0.030224 | 1:30 | 190 | 195 |
| 10 | Hide and seek: 1,936 shots per setting expose every pure state, with 95% detection and at most 0.1% false alarm | 2:20 | 302 | 303 |
| 11 | In simulation, three local settings and modest gate noise suffice, while the game route needs about 10^8 rounds | 1:30 | 197 | 195 |
| 12 | Additional result: structure for order-six Hadamard matrices is proved, but the universal step toward N(6)=3 is open | 0:50 | 106 | 108 |
| 13 | Additional result: if a cited root count (H) holds, no four MUBs of C^10 contain the standard and Fourier bases | 1:00 | 129 | 130 |
| 14 | Every claim has a status; AI did most of the computing and first drafts, and we claim no line-by-line human refereeing | 1:20 | 176 | 173 |
| 15 | To our knowledge nothing is formal end to end, but the missing basis now has certified numbers and a laboratory test | 1:00 | 130 | 130 |
| **Total** | | **20:00** | 2586 | 2599 |

Sum of the per-slide times: 20:00 exactly. Check: 0:40 + 0:55 + 0:45 + 1:20 + 1:00 + 0:30 + 1:20 + 2:00 + 2:00 + 1:30 + 2:20 + 1:30 + 0:50 + 1:00 + 1:20 + 1:00 = 20:00. Title plus slides 1 to 11 take 15:50 (79 percent of the talk); the two additional results take 1:50. Backup slides are untimed and used only for questions. Slides 1 to 13 each carry a diagram or a chart; slides 14 and 15 are the status table and the summary.

## Title slide

**Headline on slide:** The missing fourth basis in dimension six: what is verified, how far away it is, and how to see it

**Time:** 0:40

Good morning. We are Ren Jie Tee, Xinrui Li and Raymond Fong, and this is our talk on Problem 124, mutually unbiased bases in dimension six. The title carries our three questions: how do we know, how far away is a fourth basis, and how would one see it. They are the main line of the talk. Two further results are marked as additional. Every claim carries a colored tag that says how we know it, and everything on a slide is in our report.

**If asked:** Q: Did you prove that N(6) is 3? A: No. We did not prove it and we did not verify the three 2026 proofs. We checked parts of them and turned their conclusion into numbers.

## Slide 1. What unbiased means

**Headline on slide:** Unbiased bases are complementary measurements: certainty in one means pure chance in every other

**Time:** 0:55

Two orthonormal bases of six-dimensional space are mutually unbiased, or unbiased for short, if every overlap between a vector of one and a vector of the other has squared modulus one sixth. The picture shows what that means: prepare a vector of the first basis and measure in that basis, and the outcome is certain; measure in the second or the third, and all six outcomes are equally likely. In a prime power dimension you can always find d plus one such bases. Six is the smallest dimension that is not a prime power. Three are easy to build there, no fourth was ever found, and Zauner conjectured in 1999 that three is the maximum. In 2026 three computer-assisted preprints claimed exactly this.

**If asked:** Q: Why is six special? A: It is the smallest dimension that is not a prime power; the standard constructions of d plus one bases use a finite field with d elements, and there is none with six.

## Slide 2. Why it matters: fifteen of thirty-five

**Headline on slide:** In dimension six only three complementary bases are known, so state determination gets 15 of the 35 numbers it needs

**Time:** 0:45

Why should anyone outside the field care? Count parameters. A state of a six-level system has thirty-six minus one, so thirty-five, real parameters. Measuring in one basis gives six probabilities that sum to one, so five independent numbers. A complete set of seven unbiased bases would give seven times five, exactly thirty-five, with no redundancy. That is why such sets give optimal state determination. Three bases give only fifteen. So in dimension six this route to optimal tomography is closed. All of this is cited background. Our three questions: how do we know, by how much, and what would a laboratory see?

**If asked:** Q: Why not just trust three independent proofs? A: They are not independent in method. One re-implements another, all three were AI-assisted according to their authors, and none is formal end to end. That is the next slide.

## Slide 3. What was proved: the trust map

**Headline on slide:** Three 2026 computer proofs say N(6)=3; to our knowledge none is formally verified end to end, and they share a method

**Time:** 1:20

This picture is a trust map of the three preprints, one column each: the computation in the middle, the Lean part at the bottom. Everything in it is cited, and reading is not verification: we did not re-derive any of the mathematics. All three are proofs by exhaustive cases. OpenAI covers the space with two hundred forty-nine thousand eight hundred seventy-eight seed centers and a graph search, in double precision with safety margins. By its own scope note its Lean part proves only that N of six is at most five; we read that note and did not rebuild the proof. Jaswal re-implements the same method with binary64 intervals and has no Lean; our description rests on a summary. Cardenes Wuttig and Tindall use two thousand seven hundred seventy-five balls plus one at the Fourier matrix, in Arb ball arithmetic, and their Lean theorem takes the numerical certificate as a hypothesis. To our knowledge, then, nothing is formal end to end, and the proofs share a method and a trusted base.

**If asked:** Q: Are you saying the proofs are wrong? A: No. We say what each rests on. We found no error, and we did not verify them.

## Slide 4. What we checked: the record checker

**Headline on slide:** The OpenAI record checker misses every consistent in-range value change we tried

**Time:** 1:00

So we checked what an outsider can check. OpenAI publishes its saved records and a checker. We ran the checker unmodified: it passes in four seconds. To learn what that pass means, we made twenty-six small corruptions of the saved records, one at a time: the squares on the slide. It caught seventeen and missed nine: two harmless, seven scope gaps. The misses include every in-range change of a stored value that we applied consistently, such as a phase, a radius, a stored bound or a seed center. The checker confirms bookkeeping and ranges and recomputes no inequality. We ran the test twice, with identical verdicts. The corruptions are our own choice, so seventeen of twenty-six is not a quality grade, and the misses concern the checker, not the theorem.

**If asked:** Q: Does 17 of 26 mean the proof is 65 percent right? A: No. The mutations were ours, not from the real run. They show what the checker does not check.

## Slide 5. What we checked: the full rerun

**Headline on slide:** A full native rerun of the OpenAI pipeline reproduces its eight output files byte for byte

**Time:** 0:30

Then we reran the computation itself. The boxes are the stages of OpenAI's pipeline. A partial rebuild covers the blue segments and is bit-identical. The green bar is a full native rerun: one hundred invocations, and all eight principal files are byte-identical to the released ones. A separate program re-certified the 27,188 root records at 128 bits. Byte agreement shows reproducibility, not that the covering lemmas are right.

**If asked:** Q: Does the rerun verify the proof? A: No. It shows that the published programs reproduce the published files on a different processor and compiler version. The mathematics of the covering is not checked by it. The native run was done once; its accounting check and the root re-certification were repeated on a second machine.

## Slide 6. The 2008 table: two certified near-misses

**Headline on slide:** A 10^-7 threshold in the 2008 table admitted two certified near-misses, so "found numerically" is not "proved"

**Time:** 1:20

Before 2026 the evidence against a fourth basis was numerical, chiefly a table of Brierley and Weigert from 2008. A shape such as five, four, four, one is a partial fourth basis: the standard basis plus groups of vectors, orthogonal within a group and unbiased across groups. In 2008 a shape counted as found when a least-squares function fell below ten to the minus seven. For two shapes we certified, in interval arithmetic, that the lowest points reached are strict local minima of the misfit with nonzero value: one point zero two five times ten to the minus three, and seven point three three times ten to the minus four. The 2008 function there is two point nine and one point five times ten to the minus eight, below the threshold. So these points pass the 2008 test without being solutions, and the two entries become undecided, not refuted. Conversely, the shape five, three, three, three exists, yet one random start in twenty thousand finds it. Searches both over-claim and under-claim, which is why we use certificates.

**If asked:** Q: So are those two shapes empty? A: We do not know. We certified that the points we found are not solutions. The misfit might vanish elsewhere.

## Slide 7. The energy and its certificates

**Headline on slide:** No pure state is unbiased to the local triple T0: its energy exceeds 0.0384999, 99.3% of the exact minimum

**Time:** 2:00

Now the number. Write six as two times three, a qubit and a qutrit. The local triple T zero tensors the three qubit bases, the eigenbases of the Pauli operators Z, X and Y, with the standard, Fourier and twisted Fourier qutrit bases. Each measurement is done on the qubit and the qutrit separately, with no entangling gate. By the McNulty and Weigert classification there are exactly two such product triples, T zero and a second one. For a state psi, the energy E is the sum, over the eighteen outcomes of the three measurements, of the squared deviation of the outcome probability from one sixth. E is zero exactly when psi is unbiased to all three bases, which is what a vector of a fourth basis would have to be. So how small can E be? Our degree-six sum-of-squares certificate is a polynomial identity with a three hundred sixty-four by three hundred sixty-four Gram matrix, checked by a roughly 120-line program in ball arithmetic with residual about two times ten to the minus twelve. It shows E above 0.0384999 for every unit vector. The exact minimum, four minus root six over forty, about 0.03876, is prior work of Erlwein, with a degree-eight certificate. So ours is an independent certificate of ninety-nine point three percent of his value, not a new bound on T zero. The same method adds the second product triple and all sixteen triples that contain the standard and Fourier bases: E above 0.0234999, given the classical count of one hundred fifty-six cyclic six-roots.

**If asked:** Q: Is 0.0385 new? A: No. Erlwein has the exact value (4 - sqrt 6)/40 = 0.03876. Ours is an independent certificate at degree six. What is new is the same certificate for the second product triple and the 16 Fourier-pair triples.

## Slide 8. From a vector to a basis, Lean-checked

**Headline on slide:** A one-vector bound becomes a bound on every fourth basis; Lean checks it as inequalities, given the energy bound

**Time:** 2:00

A bound on one vector is not yet a statement about a measurement, which uses a whole basis. Here is the bridge. The formula is an elementary inequality: the square root of p is at most its tangent line at one sixth, minus c star times the squared deviation, with c star equal to 0.61757 and more digits beyond. The proof is a few lines and is in the backup. Summing it over the thirty-six overlaps of two bases gives the theorem. If the energy is at least gamma on every unit vector, then any fourth orthonormal basis has bias at least the square root of gamma over eighteen, and game loss at least c star gamma over seventy-two. Bias is the largest deviation of a squared overlap from one sixth. Game loss is the shortfall, from the score of four unbiased bases, in a random-access-code game. With gamma equal to 0.0384999 this gives bias above 0.046248 and loss above three point three zero two times ten to the minus four for the local triple. Lean status: we built it locally, four files, 45 declarations, no sorry. It checks the cap inequality and the theorem as inequalities about orthonormal bases of C six, with the energy bound as a hypothesis. The game score is defined there by its formula; that this formula is the optimal success probability is cited. The energy bounds are outside Lean, and we did not run the competition's build.

**If asked:** Q: Does this show that no fourth basis exists? A: No. It concerns fourth bases added to triples whose one-vector bound is certified. For all quadruples we have no certified lower bound, and that is open.

## Slide 9. The design lesson

**Headline on slide:** One explicit quadruple beats every completion of the local triple on both measures; another reaches bias 0.030224

**Time:** 1:30

Now compare with explicit sets. A quadruple is four bases. We found two quadruples numerically, one minimizing the bias and one maximizing the game score, and evaluated them in interval arithmetic, with the stored matrices corrected to exactly unitary ones and bounds rounded up. Quadruple two, the game-optimized one, has game loss at most 2.357826 times ten to the minus four, written 2.358, and bias at most 0.040599. With E above 0.0384999, every completion of T zero has bias above 0.046248 and game loss above 3.302 times ten to the minus four. So this one quadruple beats every completion on both measures. Quadruple one, the bias-optimized one, has the lowest bias we found, at most 0.030224. That is the design lesson: no bias-optimal and no game-optimal quadruple contains T zero. For the bias the argument is short: a bound E above gamma forces bias above the square root of gamma over eighteen, which exceeds 0.030224 as soon as gamma is 0.016443. Both product triples clear that threshold; the analytic bound one over seventy-two does not. For the second product triple the bias lesson holds, but the game comparison is inconclusive.

**If asked:** Q: Does this say anything about all quadruples? A: Only that explicit quadruples beat every completion of the triples we examined: one on both measures for T0, and the bias-optimal one on bias. A certified lower bound over all quadruples is open.

## Slide 10. Hide and seek

**Headline on slide:** Hide and seek: 1,936 shots per setting expose every pure state, with 95% detection and at most 0.1% false alarm

**Time:** 2:20

What would this look like in a laboratory? Play hide and seek. A hider prepares the same pure state of a qubit and a qutrit again and again, with ideal measurements and independent copies, and tries to look like white noise to the three local measurements. A referee takes N shots in each setting and computes a statistic T: the fraction of pairs of shots with equal outcomes, summed over the three settings, minus one half. T is an unbiased estimator of the energy, and Pearson's chi-square statistic equals fifteen plus six times N minus one times T, exactly. The table has the theorem. With 1,936 shots per setting, every pure state is flagged as not white noise with probability at least ninety-five percent, and the false-alarm probability is at most point one percent. With 5,142 shots the detection is ninety-nine percent. No large-sample approximation is used: the proof is Hoeffding's variance formula for U-statistics and Cantelli's inequality, in the backup. The third row is the practical figure: 239 shots for ninety-nine percent at point one percent, from a noncentral chi-square model. That is an approximation checked by simulation, and optimistic below a hundred shots, so it is not a theorem. The guarantee is larger because Chebyshev-type bounds are conservative. What is new? Not the test: it is the classical collision test of Goldreich and Ron, and Paninski. Ours is feeding it the certified energy gap, which gives a guarantee for every pure state. A badly mixed state can still have small energy, so the test separates pure states from white noise, not every state from white noise, and a real experiment needs a calibration run. In Lean we checked only the identity, four elementary inequalities of the variance bound and the arithmetic of all five shot counts, not the probability statements.

**If asked:** Q: Is the detection test new? A: No, the test is classical. What is new is feeding it the certified energy gap, which gives a finite-sample guarantee for every pure state with three fixed local settings, assuming ideal measurements and independent identical copies.

## Slide 11. Circuits, noise, control and the game

**Headline on slide:** In simulation, three local settings and modest gate noise suffice, while the game route needs about 10^8 rounds

**Time:** 1:30

Four more facts about the experiment, all from simulation. First, a purity witness: if the statistics are exactly uniform in the three settings, the largest eigenvalue of the state is at most 0.8232, so the state is not pure, by a definite margin. Second, circuits. Every setting is a product measurement, so no entangling gate between the qubit and the qutrit is needed. In a noise simulation, the total number of shots for fifty percent detection at five-sigma false alarm, in the large-sample model, is 589 for ideal gates, 646 at one percent two-qubit error and 1,500 at ten percent. Third, the dimension-four control: for two qubits with settings ZZ, XX and YY the state (1,1,i,-i)/2 is exactly uniform in all three, because a complete set of bases exists there. The referee never catches it, the dashed line. This is what a complete set looks like to the test. Fourth, the game: resolving the loss of our explicit quadruple takes about nine point three seven times ten to the seven rounds. The two experiments answer different questions. No hardware run was performed; the repository has only a rehearsal on a simulated noise model, which is not evidence.

**If asked:** Q: Why should a quantum-information person care? A: Because it turns an abstract no-go claim into a test that needs three local measurements and a few thousand shots, and tells them how much gate noise it tolerates, while the game route needs about 10^8 rounds.

## Slide 12. Additional result: structure theory

**Headline on slide:** Additional result: structure for order-six Hadamard matrices is proved, but the universal step toward N(6)=3 is open

**Time:** 0:50

Additional result, unused by the three answers. For an order-six Hadamard matrix H, take the entrywise cube. Its rank is at most two exactly for the Fourier family, its transpose or the Tao class, and its squared norm is at most eighteen outside the Tao class: both proved, with cited ingredients. The degree-four relaxation of the energy has optimum exactly zero. E above one over seventy-two is Lean-checked in our structure project. Also: the known family is a genus-ten surface with no unknown branch attached, a written proof in the supplement whose finite parts are Lean-checked; disjoint components are not excluded. The universal step is open.

**If asked:** Q: Does the cubic norm cap prove N(6)=3? A: No. Whether norm 18 forces cube rank two is not proved, and neither is the universal step. Nothing in this section yet bounds the number of MUBs.

## Slide 13. Additional result: dimension ten

**Headline on slide:** Additional result: if a cited root count (H) holds, no four MUBs of C^10 contain the standard and Fourier bases

**Time:** 1:00

Also additional. Vectors unbiased to the standard and the Fourier basis of dimension ten correspond to unimodular cyclic ten-roots. Hypothesis H: there are at most 34,940 cyclic ten-roots, a cited count that we did not verify. All 34,940 roots are certified in the repository: 3,040 unimodular. Those form 1,136 candidate bases. Assuming H, for every vector and every candidate basis some basis vector is at least 0.04178 away from unbiased, so no four bases contain the pair. The table shows dimension six as a calibration. To our reading, the dimension-ten example of Grassl, McNulty, Mista and Paterek concerns a triple of this kind, which they handle without a root-count hypothesis; we did not reproduce it. There is no certified energy bound in dimension ten; the numerical minimum is 0.0202.

**If asked:** Q: Is dimension ten a theorem? A: Yes, as a computer-assisted theorem conditional only on H, the cited count, which we did not verify. The roots themselves are certified in the repository, and the theorem says nothing about N(10).

## Slide 14. Claims, status, AI use and how it was checked

**Headline on slide:** Every claim has a status; AI did most of the computing and first drafts, and we claim no line-by-line human refereeing

**Time:** 1:20

The whole talk, by status. Proved here: the bridge theorem, the detection guarantee and the purity witness. Lean-checked here: the cap inequality, the bridge theorem as inequalities given the energy bound, and the shot arithmetic; not the energy bounds or any probability statement. Interval-certified: the energy bounds, the 2008 near-misses, the explicit quadruples and the 34,940 roots. Computed: the mutation test, the partial rebuild and the 239-shot rule of thumb. Also Lean-checked, in the structure project: E above one over seventy-two. Run once, with logs in the repository: the full native rerun. Proved in the supplement: the six-phase bound. Cited: the exact minimum and the absence of an end-to-end formal proof. Conditional: dimension ten. Open: the universal step and a bound over all triples. AI use: Claude, Codex and open-weight agents did most of the computing and first drafts. Each certified bound is checked by a short certificate checker not reviewed by a second person, and fresh AI reviewers attacked the report in six logged rounds, about 180 findings. We do not claim line-by-line human refereeing.

**If asked:** Q: Which claims are Lean-verified? A: See the table: the lemma's inequality and the bridge theorem, in the root project, and E above 1/72, in the structure project; both have their build logs in the repository. The energy certificates and dimension ten are not formalized.

## Slide 15. Summary

**Headline on slide:** To our knowledge nothing is formal end to end, but the missing basis now has certified numbers and a laboratory test

**Time:** 1:00

To summarize. How do we know? To our knowledge nothing is formal end to end. The record checker catches seventeen of twenty-six corruptions, and two 2008 entries are certified near-misses. By how much? Every pure state has energy above 0.0384999 against the local triple, and every fourth basis added to it has bias above 0.046248. One explicit quadruple does better on both measures, so the best quadruple does not contain the local triple. What would a laboratory see? With 1,936 shots per setting, assuming ideal measurements, every pure state is exposed, with 95 percent detection, 0.1 percent false alarm. We did no hardware run. Open: a certified bound over all triples and quadruples, the universal step, hypothesis H, and a hardware run. Thank you; we are happy to take questions.

**If asked:** Q: What is the one thing you would do next? A: A certified energy bound over all mutually unbiased triples of C six, to which the bridge theorem and the finite-sample theorem then apply unchanged.

## Backup slides (untimed)

B1 proof of the square-root lemma; B2 the finite-sample theorem, statement and proof sketch; B3 the degree-six certificate method and what the checker trusts (E > 0.03849999999 from the nominal level 0.0385 minus S <= 2.189e-12); B4 what is Lean-checked and what is not; B5 the second product triple and the 16 Fourier-pair triples (E > 0.0323999 for 12, E > 0.0234999 for 2, E > 0.0384999 for 2; every fourth basis added to any of them has bias above 0.036132, above 0.030224); B6 phase-ball radius; B7 six-phase bound and quartic obstruction; B8 mutation-test table.

## Q&A preparation

**1. Is the detection test new?**

No. The test is the classical collision test for uniformity (Goldreich and Ron; Paninski), analyzed with Hoeffding's variance formula for U-statistics and Cantelli's inequality. The qualitative idea that strongly unextendible triples separate pure states from some mixed states is due to Grassl, McNulty, Mista and Paterek (2017). What is new is feeding the test the certified energy gap: that turns it into a finite-sample guarantee for every pure qubit-qutrit state with three fixed local settings (1,936 shots per setting for 95 percent detection at 0.1 percent false alarm), under ideal measurements and independent identical preparations. We also give a purity witness: exactly uniform statistics force the largest eigenvalue of the state to be at most 0.8232.

**2. Why 1,936 and not 239?**

Guarantee versus approximation. 1,936 shots per setting come from the finite-sample theorem and its corollary: no large-sample approximation, a Chebyshev-type (Cantelli) bound, so it is conservative (5,142 shots for 99 percent). The figure 239 is the large-sample rule of thumb (99 percent detection, 0.1 percent false alarm), from a noncentral chi-square model with 15 degrees of freedom. It is an approximation, checked by simulation, and optimistic below N = 100 (model 0.108 against simulated 0.098 at N = 50). The two answer different questions: 239 is what an experimentalist should expect, 1,936 is what we can prove.

**3. Is 0.0385 new?**

No. The exact minimum (4 - sqrt6)/40 = 0.03876 on the canonical triple is prior work of Erlwein, with a degree-eight certificate. Our certified inequality E > 0.0384999 (nominal level 0.0385) is an independent degree-six certificate, 99.3 percent of his value, not a new bound on that triple. What the same pipeline adds, to our knowledge: certified bounds E > 0.0234999 for the second product triple and for all 16 triples containing the standard and Fourier bases (given the classical count of 156 cyclic 6-roots), the bridge from one vector to a whole basis, and the detection guarantee.

**4. What exactly is Lean-verified?**

Two Lean developments. (1) We built the project MUB6Bridge (four files, 45 declarations) locally with Lean v4.35.0 and Mathlib v4.35.0, with no sorry and only the axioms propext, Classical.choice and Quot.sound: the inequality of the square-root lemma (sqrt_le_quadratic_cap, not its equality cases), the bridge theorem for orthonormal bases of C^6 (bridge_bias, bridge_game), the numerical corollary as an implication (corollary_T0, corollary_T1: if every unit vector has energy at least 0.03849999999 then deviation above 0.046248 and game loss above 3.302e-4), gameScore_le (no four bases score above 1/2 + sqrt6/12), the arithmetic of the bias and game numbers, the identity X^2 = 15 + 6(N-1)T, four elementary inequalities of the variance bound and the arithmetic of all five shot counts (shots_T0 and others). In Lean the game score is defined by its formula; that the formula is the optimal success probability is cited. The competition's automated build has not been run by us. (2) The structure project lean_structure (46 modules, 394 theorems, Lean v4.35.0, same Mathlib) contains E > 1/72 and the structure declarations; its build log, axiom log and source hashes are in the repository, and a script checks them against the sources. It is separate from the root project, so a build of the repository root does not compile it. Not formalized: the energy certificates, the probability statements (variance formula, Cantelli), the purity witness, the dimension-ten theorem, the certificate checker. The Lean part of the OpenAI proof covers N(6) <= 5 only; nothing is formal end to end.

**5. Is dimension ten a theorem?**

Only conditionally: it is a computer-assisted theorem that depends only on hypothesis (H), the cited count of at most 34,940 cyclic 10-roots (Fuhr and Rzeszotnik, crediting Faugere), which we did not verify. All 34,940 roots are regenerated and certified inside the repository (3,040 unimodular, 31,900 certified not unimodular), and the margin 0.04178 is certified in ball arithmetic. Without (H), the mixed-volume value 35,940 (one PHCpack run, not in the repository) would allow up to 1,000 further isolated roots and does not exclude positive-dimensional solution sets. To our reading, the dimension-ten example of Grassl, McNulty, Mista and Paterek (2017) concerns a triple of this kind, which they handle without a root-count hypothesis; we did not reproduce it. There is no certified energy bound in dimension ten (numerical minimum 0.0202 for the product-basis orbit; 17 of the other 18 orbits lower, down to 0.0022, one slightly higher at 0.0207; numerical only), and the theorem says nothing about N(10).

**6. Did you verify the 2026 proofs?**

No. We mapped what each rests on (two from their repositories, one from summaries), reran OpenAI's record checker, corrupted its saved records on purpose (17 of 26 detected, run twice with identical verdicts), and rebuilt the seed cover, one stage-A shard and two stage-C batches bit for bit on the preprint's own toolchain (most stages not rerun). We also did a full native rerun with 8 principal files byte-identical and re-certified 27,188 root records; the native run was done once, and its accounting check and the root re-certification were repeated on a second machine. Reproducing outputs does not check the mathematics that connects them to the theorem.

**7. What did a human check?**

We do not claim line-by-line human refereeing of every proof. The team chose the problem and the three questions, set the constraints on what may be claimed, and directed the work. The proofs were written with AI assistance and cross-read by AI agents and scripts; certificates are checked by separate short checkers in ball arithmetic; every claim that is not a citation was recomputed at least once by another program (exceptions: the full native rerun, which was run once, the written proofs of the six-phase bound and of the known-family geometry, and the mixed-volume value; and two single-run records). The hostile review rounds were done by fresh AI reviewers and are logged. The certificate checker (about 120 lines) has not been reviewed by a second person.

**8. What is the single most novel thing?**

The conversion of a certified one-vector gap into a statement about whole fourth bases and about shots: the bridge theorem with explicit constants, Lean-checked only as inequalities about orthonormal bases of C^6 given the energy bound as a hypothesis, and the finite-sample detection guarantee built on it. The design lesson that follows (no bias-optimal and no game-optimal quadruple contains the local triple) is the most surprising consequence. The energy bound itself is not new for the local triple, and the test is classical.

**9. Why should a quantum-information person care?**

Because the open question becomes operational. A complete set of seven unbiased bases would give optimal tomography of a six-level state; three give 15 of 35 numbers. Our results say how far a fourth basis must be from unbiased, and how many shots of three local measurements, with no entangling gate, expose any pure state that tries to pass as white noise. That is a test an experiment could run, with a white-noise calibration run, though we did no hardware run.

**10. What would you do with two more days?**

First, a certified energy bound over all mutually unbiased triples of C^6, which come in continuous families; the bridge theorem and the finite-sample theorem would then apply unchanged and give bounds for all quadruples containing a triple. Second, have a person review the certificate checker and the Lean statements line by line. Third, verify hypothesis (H) independently, for instance by a certified homotopy count. Fourth, run the detection test on hardware with a white-noise calibration run.

**11. What do the 2008 near-miss values mean?**

The values 1.02497683851953e-3 and 7.32788656303688e-4 are the misfit mu = ||r||_2 at certified strict local minima of the shapes {5,4,4,1} and {5,5,3,1}. The 2008 function F = mu^2/36 there is 2.9e-8 and 1.5e-8, below the 2008 threshold 1e-7. So the 2008 acceptance test accepts them, and the two entries become undecided, not refuted. We did not prove the shapes empty, and we certified only the lowest level found for each shape.

**12. Does the structure theory prove N(6)=3?**

No. It is an additional result. We proved the cube-rank criterion and the cap ||H^o3||^2 <= 18 outside the Tao class (each with a cited ingredient), and the exact degree-four obstruction. Whether norm 18 forces cube rank two is not proved, and neither is the universal step that would finish the argument. Nothing in that section bounds the number of MUBs.

