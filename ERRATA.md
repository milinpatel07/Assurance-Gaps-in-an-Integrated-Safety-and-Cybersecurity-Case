# Errata and Divergences

Discrepancies between the camera-ready papers and this repository, and one
internal inconsistency inside the WAISE camera-ready itself. Each entry states
what the paper says, what the repository holds, how the difference was found,
and how it was resolved. Line numbers refer to
`paper/waise2026/CR_Submission_WAISE_SafeCompAssuranceGaps_SafetySecurityCase_AI_Perception_HAD.tex`.

The repository's rule for these cases: never change a paper source, and never
silently absorb a difference. Where the paper is internally inconsistent, the
authors decide which statement wins and the code records the decision at the
point of use. Where the paper carries content the code lacked, the code absorbs
it. Where the two diverge and no decision has been taken, the entry says so.

## 1. DP-2 is typed "S, M" in Table 3 and structural in the prose

Table 3 (`tab:inconsistencies`, line 410) types DP-2 "S, M": structural and
methodological. The prose treats DP-2 as structural in three places: the type
definitions (line 216), the classification sentence grouping DP-1, DP-2 and
DP-5 as structural (line 372), and the statement that the evidence asymmetry at
G5 "is a structural property of the applicable standards" (line 469). The last
two are camera-ready additions.

Found by the standards-practitioner review in iteration 1, comparing the
paper's Table 3 against `src/analysis/decision_points.py`. Resolved by the
authors in favour of the prose: DP-2 is structural. The code types `I-2`
structural, the paper's 3/2/2 type split holds, and the reasoning is recorded
at the definition of `I-2`. The Table 3 cell stands uncorrected in the
published paper; this entry is its erratum.

## 2. Findings table classifications the code had not absorbed

Table 4 (`tab:gaps`) carries three classifications that predated this
repository's data:

- F-1 lists two lifecycle phases, Concept and Verification. The code carried
  Verification only.
- F-3 lists Verification and Operation. The code carried Verification only.
- F-2's related-clauses cell includes ISO 24089. The code's partial-coverage
  list did not.

Found by the standards-practitioner review in iteration 1, confirmed
independently by the support reviewer. Absorbed in commit `21a9ecb`: F-1 and
F-3 gained `additional_lifecycle_phases`, leaving the primary phase and every
existing caller unchanged, and F-2's partial coverage gained ISO 24089.

## 3. F-1 and F-5 titles the code had not absorbed

The camera-ready retitled two findings and softened their claims. F-1 became
"Quantitative acceptance criteria for AI components" (line 453); the body
states that ISO 21448 Cl.6.5 establishes the framework and defers quantitative
values to context, and that no published method derives application-specific
targets (line 435). F-5 became "Data acceptance criteria for AI components"
(line 455); the body states that ISO/PAS 8800 Cl.8.4 and ISO/IEC TR 5469
Cl.9.3.3 prescribe frameworks and criteria but defer thresholds to context
(line 439). The code still described F-1 as "No AI-specific quantitative
reliability target" and F-5 as "no standard prescribes when training data are
sufficient", which the paper's own line 439 contradicts.

Found by the scope-fidelity and standards-practitioner reviews of the
interactive GSN view, 2026-08-24. Absorbed in commit `6bc81ca`: both
descriptions in `src/analysis/gaps.py` now carry the camera-ready titles and
the deferral framing.

## 4. The paper reports 193 tests; the suite holds 192 at that baseline

The WAISE paper reports 193 tests. That count was correct when the paper was
written. The gap classification was later revised from six findings to five,
which removed one test (commit `4d782b0`), and the suite held at 192 from then
until later additions. The number in the paper was not changed to match, and no
test was added to make the count agree.

Recorded in `README.md` before this file existed; restated here so the errata
are in one place.

## 5. Table `tab:dp5` cites Cl.9 for triggering-condition identification

The DP-5 worked example (line 390) cites "Triggering condition identification
(Cl.9)". ISO 21448 places the identification of hazardous scenarios and
triggering conditions in Cl.7; Cl.9 belongs to the verification clauses. The
paper's own Table 2 and the repository (`src/standards/iso21448.py`, Cl.7)
use Cl.7 for identification.

Found by the standards-practitioner review of the interactive GSN view,
2026-08-24. The repository is correct and unchanged; the table cell is the
erratum.

## 6. Table 2 lists ISO 26262-4 Cl.8 at G5; the repository does not

Table 2 (`tab:goals`, line 349) gives G5's added claims as "21448 Cl.9-11;
21434 Cl.10 (cyber verification); 26262-4 Cl.8". The repository's G5 carries
ISO 26262-6 Cl.9 (MC/DC) as its ISO 26262 contribution, which matches the
paper's Figure 2(b) (line 307) and the DP-2 row of Table 3 (line 410). So the
paper cites two different ISO 26262 clauses for G5 in different places, and
the repository follows the figure and Table 3 rather than Table 2.

Found by the standards-practitioner review of the interactive GSN view,
2026-08-24. Unresolved: whether ISO 26262-4 Cl.8 (integration and testing)
should join G5's clause references is a decision for the authors.

## 7. The paper cites ISO/PAS 8800 Cl.6.2 at G2; the repository uses Cl.5

The G2 prose (line 326) cites ISO/PAS 8800 Cl.6.2 (semantic and syntactic
input space). The repository's G2 cites ISO/PAS 8800 Cl.5 (AI specification),
which resolves in `src/standards/iso8800.py` and is used consistently in
`TRACEABILITY.md`. Table 2's source cell for G2 says only "8800 Annex B", so
neither reading contradicts the table.

Found by the standards-practitioner review of the interactive GSN view,
2026-08-24. Unresolved: a divergence, not a contradiction, and the authors
decide which clause the repository should cite.
