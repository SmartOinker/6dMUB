# Speaker notes: The missing fourth basis in dimension six

Caltech x SAIR Mathathon, Problem 124. Speaking rate planned at about 130 words per minute. Slide numbers are the content-slide numbers shown on the slides; the title slide is slide 0.

## Timing table

| Slide | Title | Time | Words in script | Words at 130 wpm |
|---|---|---|---|---|
| Title | The missing fourth basis in dimension six | 0:40 | 77 | 87 |
| 1 | In dimension six, three mutually unbiased bases are easy to build and a fourth has never been found | 2:00 | 248 | 260 |
| 2 | Three 2026 computer proofs say N(6)=3, and none is formally verified end to end | 1:30 | 202 | 195 |
| 3 | We reran what an outsider can rerun: the checker catches 17 of 26 corruptions, and the rerun is byte-identical | 1:20 | 175 | 173 |
| 4 | We can prove structure for order-six Hadamard matrices, but the universal step toward N(6)=3 is still open | 1:30 | 194 | 195 |
| 5 | No pure state hides from the local triple: its energy is at least 0.0385, which is 99.3% of the exact minimum | 1:30 | 200 | 195 |
| 6 | A 10^-7 threshold accepted two near-misses, so "found numerically" is not "proved" | 1:20 | 178 | 173 |
| 7 | One certified vector bound forces every fourth basis to be far from unbiased, farther than explicit quadruples | 2:10 | 277 | 282 |
| 8 | A chi-square test catches every pure state in about 239 shots per setting; the game needs about 9.4 x 10^7 rounds | 1:50 | 230 | 238 |
| 9 | Dimension ten with the same method: 34,940 cyclic roots funnel down to 1,136 candidate bases, and none extends | 1:20 | 181 | 173 |
| 10 | In dimension ten, no four MUBs contain the standard and Fourier bases, if the cited root count holds | 1:20 | 179 | 173 |
| 11 | Claims and status, in one table | 1:10 | 146 | 152 |
| 12 | AI did most of the computing and drafting, so every lower bound is a certificate with a short checker | 1:00 | 129 | 130 |
| 13 | Three questions, three answers, and what stays open | 1:20 | 181 | 173 |
| **Total** | | **20:00** | 2597 | |

Check: 0:40 + 2:00 + 1:30 + 1:20 + 1:30 + 1:30 + 1:20 + 2:10 + 1:50 + 1:20 + 1:20 + 1:10 + 1:00 + 1:20 = 20:00. Backup slides are untimed and used only for questions.

## Slide Title

**Headline on slide:** The missing fourth basis in dimension six

**Time:** 0:40

Good morning. We are Ren Jie Tee, Xinrui and Raymond Fong How, and this is our talk on Problem 124, mutually unbiased bases in dimension six. The title carries our three questions: what is verified, how far away is a fourth basis, and how would one see it. Every claim on every slide has a small colored tag saying how we know it, so you can see at a glance what is solid and what is not.

**If asked:** Q: Did you prove that N(6) is 3? A: No. We did not prove it and we did not verify the three 2026 proofs. We checked parts of them, and we turned their conclusion into numbers.

## Slide 1. The question

**Headline on slide:** In dimension six, three mutually unbiased bases are easy to build and a fourth has never been found

**Time:** 2:00

Two orthonormal bases of six-dimensional space are mutually unbiased if every overlap between a vector of one and a vector of the other has squared modulus one sixth. Physically they are complementary measurements: certainty in one means complete randomness in the other. In dimension six, write six as two times three, a qubit times a qutrit. Take the three qubit bases, the eigenbases of the Pauli operators Z, X and Y, and tensor them with three mutually unbiased qutrit bases: the standard basis, the Fourier basis F three, and a twisted Fourier basis D F three. That gives three mutually unbiased bases of the six-level system, and you can measure each one locally, with no entangling gate. The picture on the right shows these three settings, and the question mark is the fourth basis that nobody has found. In prime power dimensions you can always go all the way to d plus one bases. Six is the first dimension where this fails to be clear. Zauner conjectured in 1999 that three is the maximum. In 2026, three computer-assisted preprints claim to prove it. The next case of the same shape, dimension ten, is open. So we ask three questions about the claim: how do we know, by how much, and what would one see in a laboratory. Along the way we try to be precise about what is ours, what is prior work, and what is only numerical. Overclaiming would defeat the purpose of asking how we know.

**If asked:** Q: Why not just trust three independent proofs? A: They are not independent in method. One re-implements another, all three were AI-assisted according to their authors, and none is formal end to end. That is the next slide.

## Slide 2. What was proved: trust map

**Headline on slide:** Three 2026 computer proofs say N(6)=3, and none is formally verified end to end

**Time:** 1:30

This table is a trust map of the three preprints. All entries are cited, we did not re-derive them. OpenAI covers the space of candidate vectors with about two hundred fifty thousand seed centers and runs a graph search to exclude two further bases. It uses ordinary double precision with safety margins. Its Lean development proves only that N of six is at most five. The reduction from five to three rests on computation outside Lean. Jaswal re-implements the same method with interval arithmetic and has no Lean. Cardenes Wuttig and Tindall use a different global reduction, a connectedness argument, with ball arithmetic and an independent checker. Their Lean theorem takes the numerical certificate as a hypothesis. So, to our reading, nothing is formally verified end to end, the three proofs share an ancestor, and floating point is still in the trusted base of all three. The grey box at the bottom is the legend for the tags you will see for the rest of the talk. Proved means we proved it by hand. Interval-certified means a short program checked it in ball arithmetic. Numerical means a local search only. Conditional means it depends on a stated hypothesis, and open means unproved.

**If asked:** Q: Are you saying the proofs are wrong? A: No. We say what each rests on. We found no error, and we did not verify them.

## Slide 3. What we checked

**Headline on slide:** We reran what an outsider can rerun: the checker catches 17 of 26 corruptions, and the rerun is byte-identical

**Time:** 1:20

So we checked what an outsider can check. OpenAI's record checker runs unmodified and reproduces the counts of the preprint. To learn what its pass means, we made twenty-six small corruptions of the saved records, one at a time. It caught seventeen and missed nine. The misses tell us the checker confirms bookkeeping: counts, ranges, file structure. It does not recompute any inequality. That is a statement about the checker, not a flaw in the theorem. Our teammate on workstream C then did a full native rerun: one hundred invocations, eight principal output files byte-identical to the released ones, and twenty-seven thousand root records re-certified in 128-bit ball arithmetic. We did not re-run that ourselves, so we say so. Byte agreement shows reproducibility, not that the covering lemmas are right. We also partially rebuilt the C plus plus programs on a second machine and got identical outputs. Finally we redid the Fourier pair special case from scratch: one hundred fifty-six roots, forty-eight unimodular vectors, sixteen candidate bases, and no fourth, given the classical root count.

**If asked:** Q: Does 17 of 26 mean the proof is 65 percent right? A: No. The mutations were ours, not from the real run. They show what the checker does not check.

## Slide 4. Toward a proof a human can read

**Headline on slide:** We can prove structure for order-six Hadamard matrices, but the universal step toward N(6)=3 is still open

**Time:** 1:30

Our second theme is structure, from workstream B. The computer proofs split on a Hadamard matrix H of order six. The entrywise cube of H has a rank, and we proved a criterion: that rank is at most two exactly when H is in the Fourier family, a transpose of it, or the cubic Tao matrix. One ingredient is a cited classification. Second, for every order-six Hadamard matrix outside the Tao class, the squared operator norm of the cube is at most eighteen, with a trace bound that is an equality exactly when the cube has rank two. Cube rank two forces norm eighteen. Whether norm eighteen forces cube rank two is open. Third, a degree-four sum-of-squares relaxation of the energy cannot give any positive bound: its optimum is exactly zero, with a rank sixty-three pseudomoment matrix checked in exact arithmetic. The last box is the step that would finish the argument: a universal vanishing of residual products on all compatible triples. It is unproved. Nothing here yet bounds the number of mutually unbiased bases. We report it as progress on structure, and we do not present it as a route we have completed.

**If asked:** Q: Is the cubic cap new? A: The reduction and the cap are workstream B's. They use the Schur product device, which is classical, and a cited Fourier condition. We do not claim priority beyond that.

## Slide 5. No hidden state

**Headline on slide:** No pure state hides from the local triple: its energy is at least 0.0385, which is 99.3% of the exact minimum

**Time:** 1:30

Now the number. For a state psi, the energy E is the sum, over the eighteen outcomes of the three local measurements, of the squared deviation of the outcome probability from one sixth. E is zero exactly when the state is unbiased to all three bases, which is what a fourth basis vector would have to be. So the question is how small E can be. The number line shows what is known. At degree four, sum-of-squares certificates give nothing: zero. An analytic bound of one over seventy-two, about 0.0139, was built in Lean by a teammate; we report it and did not re-run the build. Our degree-six certificate, checked in interval arithmetic, gives 0.0385. And the exact minimum, four minus root six over forty, about 0.03876, is prior work of Erlwein at degree eight. So our 0.0385 is an independent certificate of ninety-nine point three percent of Erlwein's exact value, at lower degree. It is not a new bound. What is new is that it comes from a separate pipeline, and the same pipeline runs on other triples. The degree-four obstruction on the previous slide explains why the ladder starts at zero: you need degree six to see anything.

**If asked:** Q: Is 0.0385 new? A: No. Erlwein has the exact value. Ours is an independent certificate at degree six, and we also certified 0.0235 for the second product triple, which Erlwein lists as open.

## Slide 6. Why certificates

**Headline on slide:** A 10^-7 threshold accepted two near-misses, so "found numerically" is not "proved"

**Time:** 1:20

Why bother with certificates? Because of a table from 2008. Brierley and Weigert searched for partial fourth bases, called constellations, and counted a shape as found when a misfit function fell below ten to the minus seven. We reran the search and picked out two shapes, five-four-four-one and five-five-three-one. With interval arithmetic we proved that the lowest points the search reaches are strict local minima of the misfit with nonzero value. The misfit values are one point zero two five times ten to the minus three and seven point three three times ten to the minus four. Their 2008 function values are two point nine and one point five times ten to the minus eight, below the threshold. So the 2008 test cannot tell a near-miss from a solution. This does not prove those shapes empty. The converse also holds: a shape that exists, five-three-three-three, was found in one of twenty thousand of our random starts. Thirteen shapes of the table remain undecided. The lesson is that a threshold on a misfit cannot separate nearly exists from exists.

**If asked:** Q: So are those two shapes empty? A: We do not know. We proved the points we found are not solutions. The misfit might vanish elsewhere.

## Slide 7. From a vector to a basis

**Headline on slide:** One certified vector bound forces every fourth basis to be far from unbiased, farther than explicit quadruples

**Time:** 2:10

A bound on one vector is not yet a statement about a measurement. Here is the bridge. The formula at the top is an elementary inequality: the square root of p is at most its tangent line at one sixth, minus c star times the squared deviation, where c star is about 0.6176. It is proved in a few lines, and the proof is in the backup. Summing it over the overlaps of two bases gives the theorem. If the energy is at least gamma on every unit vector, then every fourth basis has bias at least the square root of gamma over eighteen, and loses at least c star gamma over seventy-two in the random-access game, compared with four mutually unbiased bases. With gamma equal to 0.0385, the bias exceeds 0.046 and the game loss exceeds three point three times ten to the minus four. Now compare with explicit sets. We found two quadruples of bases numerically and certified their numbers in interval arithmetic: bias at most 0.0302 and game loss at most two point three six times ten to the minus four. Both are better than any completion of the perfect triple. That is the design lesson: the best approximate quadruples are not completions of the perfect local triple. This is for the canonical product triple. For the second product triple, the bias lesson holds but the game comparison is inconclusive. The game loss is the shortfall from the value of four mutually unbiased bases, about 0.7041. Our bias and loss lower bounds hold for every fourth basis, not only for the explicit ones, because the proof uses only the energy bound on single vectors.

**If asked:** Q: Does this show no fourth basis exists? A: No. It concerns quadruples that contain our exact triple. We have no certified lower bound for all quadruples, and that is an open problem.

## Slide 8. Hide and seek

**Headline on slide:** A chi-square test catches every pure state in about 239 shots per setting; the game needs about 9.4 x 10^7 rounds

**Time:** 1:50

What would this look like in a laboratory? Play hide and seek. A hider prepares the same pure state again and again and tries to look like white noise to the three local measurements. A referee takes N shots per setting and runs a chi-square test for uniformity. The detectability per shot is the energy, so our certified floor on the energy gives a floor on detection for every pure state. The curve on the left is that floor, the circles are simulations of the best hider. At about two hundred thirty-nine shots per setting, detection is ninety-nine percent at false-alarm rate point one percent. The dashed line is a control in dimension four, where a hiding state exists. It is never caught. The table shows total shots for fifty percent detection at five-sigma false alarm, under depolarizing noise on the two-qubit gates: 589 without noise, 594 at point one percent, 646 at one percent, and 1,500 at ten percent. By contrast, seeing the shortfall in the four-basis game needs about nine point four times ten to the seven rounds, about five orders of magnitude more. This matters because it says the missing basis is visible with a few hundred shots, not a hundred million rounds. Two honest limits: the shot counts are a large-sample chi-square approximation checked by simulation, not a finite-sample theorem, and no hardware run was done.

**If asked:** Q: Is 239 shots rigorous? A: No. The energy bound is rigorous. The shot count uses the large-sample chi-square law, checked by Monte Carlo. Also, the test catches pure states only, since a mixed state can hide.

## Slide 9. Ten, same method

**Headline on slide:** Dimension ten with the same method: 34,940 cyclic roots funnel down to 1,136 candidate bases, and none extends

**Time:** 1:20

Now dimension ten, with the same method. A vector unbiased to the standard basis and the Fourier basis corresponds to a unimodular cyclic ten-root. Cyclic ten-roots are the solutions of a polynomial system; the literature reports 34,940 of them. We enclosed each one in a certified box using Krawczyk tests in ball arithmetic. Of those, 3,040 are unimodular, so they are the vectors we need. Among them, 57,680 pairs could be orthogonal, and they form exactly 1,136 candidate bases. No pair of candidate bases is mutually unbiased, and no vector is unbiased to a candidate triple. On the right is the calibration: the same pipeline in dimension six returns the known counts, 156, 48 and 16. The bars are drawn on a log scale, so dimension ten is wider but the shape is the same. All the certified steps depend on one hypothesis, the cited root count, which we come to on the next slide. The shape in dimension ten is the same as in dimension six, only wider at the top by a bit more than two orders of magnitude.

**If asked:** Q: Why trust the pipeline? A: Because in dimension six it reproduces Grassl's known result, and in dimension seven it recovers the complete set of eight bases.

## Slide 10. Ten: theorem and limits

**Headline on slide:** In dimension ten, no four MUBs contain the standard and Fourier bases, if the cited root count holds

**Time:** 1:20

Here is the dimension ten theorem, and it is conditional. Hypothesis H: the system has at most 34,940 solutions. That count is a Groebner basis computation attributed to Faugere, known to us only through a table in the literature, and we did not verify it. Assuming H, for every vector unbiased to I and the Fourier basis, and for each of the 1,136 candidate bases, some vector of the basis has squared overlap at least 0.04178 away from one tenth. So no triple extends, and no four mutually unbiased bases of C ten contain the standard and Fourier bases. Limits. It covers only triples containing that pair. Without H, our fallback of at most a thousand further isolated roots rests on a mixed-volume value, 35,940, that we did not verify independently. A search from 1.2 million random starts always landed on the certified list, which is evidence for H, not a proof. And there is no certified energy bound in dimension ten. Numerically, the product triple there has minimum energy about 0.02, but that is a local-minimization estimate only.

**If asked:** Q: Is the dimension-ten result a theorem? A: Yes, as a conditional computer-assisted theorem: it assumes the cited root count, which we did not verify.

## Slide 11. Claims and status

**Headline on slide:** Claims and status, in one table

**Time:** 1:10

This table is the whole talk in one place. Read down the status column. Cited: that no end-to-end formal proof exists, to our reading, and the exact minimum, which is Erlwein's. Computed: the checker test, the byte-identical rerun by workstream C, which we did not re-run, and the shot counts. Proved: the cube-rank criterion and cubic cap by workstream B, and our bridge theorem, from certified inputs. Lean-checked as reported: one over seventy-two, built by a teammate. Interval-certified: the energy bounds and the 2008 near-misses. Conditional: dimension ten. Open: the universal step. The report has a longer table with the supporting file for every row. The who column uses our three workstreams: A for the certificates, bridge, detection test and dimension ten, B for structure theory and Lean, and C for the explanatory audit and full rerun. The cited rows are prior work and not ours.

**If asked:** Q: Which claims are formally verified? A: Only the energy bound one over seventy-two, in Lean, by a teammate, and we did not re-run it. The bridge lemma has an unbuilt Lean draft only, so we make no Lean claim for it.

## Slide 12. AI use and limits

**Headline on slide:** AI did most of the computing and drafting, so every lower bound is a certificate with a short checker

**Time:** 1:00

We used AI heavily: Claude for workstream A, Codex for B and C, and open-weight agents on the event platform. The team chose the questions and reviewed the outputs. Because of that, we never rely on a model's word. Every lower bound is a certificate checked by a short program in ball arithmetic. We calibrated on known answers: ninety-nine point three percent of Erlwein's value, the counts 156, 48 and 16, and the dimension-four control that is never caught. We recomputed results with separate code, and ran three rounds of hostile review. What was not checked: we verified none of the three 2026 proofs, no human read the certificate checkers or the dimension-ten code line by line, Lean covers only one over seventy-two, and there was no hardware run.

**If asked:** Q: Could the certificate checker itself be wrong? A: Yes. It is about 100 lines and no second person has reviewed it. Its output agrees with Erlwein's independent exact value to 0.7 percent, which is our main external check.

## Slide 13. Summary

**Headline on slide:** Three questions, three answers, and what stays open

**Time:** 1:20

To summarize. How do we know? None of the three proofs is formal end to end. The record checker catches seventeen of twenty-six corruptions, a rerun is byte-identical, and two entries of the 2008 table are certified near-misses. By how much? Every pure state has energy at least 0.0385, and every fourth basis added to the local triple has bias above 0.046 and game loss above three point three times ten to the minus four. Dimension ten gives the same flavor of result, conditionally. What would one see? About two hundred forty shots per setting, against nine point four times ten to the seven game rounds, with the caveats that it is a large-sample approximation and no hardware run was done. What is open: the universal step in the structure theory, hypothesis H in dimension ten, a lower bound over all quadruples, a hardware run, and a formal proof of the bridge theorem. The main message is that checking and quantifying a result can add value even when the result itself is settled. Thank you. We are happy to take questions.

**If asked:** Q: What is the one thing you would do next? A: A certified lower bound on bias and game loss over all quadruples. The bridge theorem gives the last step once an energy bound over all triples is available.

## Backup slides (untimed)

B1 proof of the square-root lemma; B2 degree-six certificate method and what the checker trusts; B3 sharp phase-ball radius; B4 six-phase bound and quartic SOS obstruction; B5 second product triple and the Fourier pair (16 triples, all with interval-certified energy at least 0.0235, so every fourth basis added to any of them has bias above 0.0361, above 0.0302); B6 mutation-test breakdown.

## Q&A preparation

**1. Is 0.0385 new?**

No. The exact minimum (4 - sqrt6)/40 = 0.03876 on the canonical triple is prior work of Erlwein, with a degree-eight certificate. Our 0.0385 is an independent interval-certified bound at degree six, 99.3 percent of his value. What is new is the pipeline running on the second product triple (0.0235), the bridge from one vector to a whole basis, and the detection test built on it.

**2. Is the dimension-ten result a theorem?**

It is a computer-assisted theorem conditional on hypothesis (H), the cited count of at most 34,940 cyclic 10-roots, which we did not verify. The statement on the slide carries the hypothesis. The fallback of at most 1,000 further isolated roots rests on a mixed-volume value 35,940 that we also did not verify independently. A numerical search from 1.2 million starts supports (H) but does not prove it.

**3. Did you verify the OpenAI proof?**

No. We reran its record checker, tested it with 26 corruptions (17 detected), and partially rebuilt it. A teammate did a full native rerun that we did not re-run, with byte-identical output files. Reproducing outputs does not check the mathematics connecting them to the theorem.

**4. Is your bridge lemma in Lean?**

No. There is only an unbuilt Lean draft, and we make no Lean claim for it. The proof is a few lines of algebra on the page, and we tested it numerically on 1.8 million random probability vectors.

**5. 239 shots: is that rigorous?**

The energy bound behind it is interval-certified. The shot count itself uses the large-sample chi-square approximation to Pearson's statistic, checked by Monte Carlo simulation. It is not a finite-sample theorem. It covers pure states only, since a mixed state such as the maximally mixed state hides perfectly, and no hardware run was done.

**6. Is anything formally verified end to end?**

No, to our reading. OpenAI's Lean development proves N(6) <= 5 only. The other Lean theorem takes the numerical certificate as a hypothesis. Our own Lean content is E > 1/72, built by a teammate and not re-run by the assembling workstream.

**7. Why do the explicit quadruples matter?**

They give certified upper bounds on the best possible bias (0.0302) and game loss (2.36e-4). Since every completion of the canonical triple is worse (bias above 0.046, loss above 3.3e-4), the best approximate quadruples are not completions of the perfect local triple. For the second product triple the bias lesson holds but the game comparison is inconclusive (2.015e-4 against 2.358e-4).

**8. Does the cubic norm cap prove N(6)=3?**

No. We proved the cap for order-six Hadamard matrices outside the Tao class, and that the trace bound is an equality exactly when the cube rank is two. Whether norm equality forces cube rank two is open, and so is the universal step that would finish the argument.

**9. What do the 2008 near-miss values mean?**

The values 1.02497683851953e-3 and 7.32788656303688e-4 are the misfit mu = ||r||_2 at certified strict local minima. The 2008 function F = mu^2/36 there is 2.9e-8 and 1.5e-8, below the 2008 threshold 1e-7. So the 2008 criterion accepts them. We did not prove the shapes empty.

**10. What does the Fourier-pair result add?**

All 16 triples that complete {I, F_6} have interval-certified energy at least 0.0235 (12 triples at least 0.0324, 2 at least 0.0235, 2 at least 0.0385), so every fourth basis added to any of them has bias above 0.0361, which exceeds the explicit quadruple's 0.0302. This is for quadruples containing that pair, not all quadruples.
