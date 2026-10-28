# Errata and divergences

This file records the discrepancies between this repository and the WAISE
paper (Patel and Jung, "Integrating Cybersecurity Into the AI Safety Assurance
Argument: A GSN Pattern for AI-Based Perception Components in Highly Automated
Driving", WAISE 2026, workshop at SAFECOMP 2026). Two entries record places
where the WAISE camera-ready disagrees with itself (entries 1 and 6), and one
records a clause it cites for an activity the standard places elsewhere
(entry 5). No entry concerns the position paper (Patel and Jung, "Operational
Safety and Cybersecurity Assurance of AI-Based Perception in Highly Automated
Driving", SAFECOMP 2026).

Each entry states what the paper says, what the repository holds, how the
difference was found, and how it was resolved, or that it is still open.
Section, table and figure numbers follow the published paper
([doi:10.1007/978-3-032-35506-5_55](https://doi.org/10.1007/978-3-032-35506-5_55)).

Entries 3, 5, 6 and 7 were found on 2026-08-24 while building the interactive
GSN view, by checking each displayed clause and finding against the standard
and the paper.

The repository's rule for these cases: never change a published paper, and never
change the code to match a paper without recording it here. Where the paper
disagrees with itself, the authors decide which statement wins and the code
records the decision at the point of use. Where the paper carries content the
code lacked, the code adopts it. Where the two diverge and no decision has been
taken, the entry says so.

## 1. DP-2 is typed "S, M" in Table 4 and structural in the prose

Table 4 types DP-2 "S, M": structural and methodological. The prose treats
DP-2 as structural in three places: the type definitions (Section 3.2, Step 4),
the classification sentence grouping DP-1, DP-2 and DP-5 as structural (Section
5.1, first paragraph), and the statement that the evidence asymmetry at G5 "is
a structural property of the applicable standards" (Section 6.1). The last
two are camera-ready additions.

Found by comparing Table 4 of the paper against
[`src/analysis/decision_points.py`](src/analysis/decision_points.py). Resolved
by the authors in favour of the prose: DP-2 is structural. The code types `I-2`
structural, the paper's 3/2/2 type split holds, and the reasoning is recorded
at the definition of `I-2`. The Table 4 cell stands uncorrected in the
published paper; this entry is its erratum.

## 2. Findings-table classifications the code had not adopted

Table 5 carries three classifications that the code did not yet hold:

- F-1 lists two lifecycle phases, Concept and Verification. The code carried
  Verification only.
- F-3 lists Verification and Operation. The code carried Verification only.
- F-2's related-clauses cell includes ISO 24089. The code's partial-coverage
  list did not.

Found by comparing Table 5 of the paper against
[`src/analysis/findings.py`](src/analysis/findings.py). Adopted in commit `21a9ecb`: F-1 and F-3 gained
`additional_lifecycle_phases`, leaving the primary phase and every existing
caller unchanged, and F-2's partial coverage gained ISO 24089.

## 3. F-1 and F-5 titles the code had not adopted

The camera-ready retitled two findings and softened their claims. F-1 became
"Quantitative acceptance criteria for AI components" (Table 5); the body
states that ISO 21448 Cl.6.5 establishes the framework and defers quantitative
values to context, and that no published method derives application-specific
targets (Section 5.2, F-1). F-5 became "Data acceptance criteria for AI
components" (Table 5); the body states that ISO/PAS 8800 Cl.8.4 and ISO/IEC TR
5469 Cl.9.3.3 prescribe frameworks and criteria but defer thresholds to context
(Section 5.2, F-5). The code still described F-1 as "No AI-specific
quantitative reliability target" and F-5 as "no standard prescribes when
training data are sufficient", which the paper's own F-5 paragraph contradicts.

Found in the 2026-08-24 check of each displayed finding against the
camera-ready wording. Adopted in commit `6bc81ca`: both descriptions in
[`src/analysis/findings.py`](src/analysis/findings.py) now carry the camera-ready
titles and the deferral framing.

## 4. The paper reports 193 tests; after commit `4d782b0` the suite held 192

The WAISE paper reports 193 tests. That count was correct when the paper was
written. The finding classification was later revised from six findings to
five, which removed one test (commit `4d782b0`), and the suite held 192 tests
until new tests were added for later work. The number in the paper was not
changed to match, and no test was added to make the count agree.

## 5. Table 3 cites Cl.9 for triggering-condition identification

The DP-5 worked example, Table 3, cites "Triggering condition
identification (Cl.9)". ISO 21448 places the identification of hazardous
scenarios and triggering conditions in Cl.7; Cl.9 belongs to the verification
clauses. The repository
([`src/standards/iso21448.py`](src/standards/iso21448.py)) uses Cl.7 for
identification. The paper cites no clause for identification outside Table 3.

Found in the 2026-08-24 check of each displayed clause against the standard
and the paper. The repository is correct and unchanged; the table cell is the
erratum.

## 6. Table 2 lists ISO 26262-4 Cl.8 among G5's added claims; G5's clause references do not

Table 2 gives G5's added claims as "21448 Cl.9-11;
21434 Cl.10 (cyber verification); 26262-4 Cl.8". Fig. 1(b) and the DP-2 row of
Table 4 name ISO 26262-6 Cl.9 (MC/DC) as the ISO 26262 contribution at G5. So
the paper cites two different ISO 26262 clauses for G5 in different places.

The repository's claim index maps an ISO 26262-4 Cl.8 claim
(`CLM-26262-SVAL-01`) to G5 ([`TRACEABILITY.md`](TRACEABILITY.md), section 4),
but G5's clause references and its evidence type (a) name only ISO 26262-6 Cl.9,
following Fig. 1(b) and Table 4.

Found in the 2026-08-24 check of each displayed clause against the standard and
the paper. Unresolved: whether ISO 26262-4 Cl.8 (integration and testing)
should join G5's clause references is a decision for the authors.

## 7. The paper cites ISO/PAS 8800 Cl.6.2 at G2; the repository uses Cl.5

The G2 prose (Section 4.2) cites ISO/PAS 8800 Cl.6.2 (semantic and syntactic
input space). The repository's G2 cites ISO/PAS 8800 Cl.5 (AI specification),
which resolves in [`src/standards/iso8800.py`](src/standards/iso8800.py) and is
used consistently in [`TRACEABILITY.md`](TRACEABILITY.md). Table 2's source
cell for G2 says only "8800 Annex B", so neither reading contradicts the table.

Found in the 2026-08-24 check of each displayed clause against the standard and
the paper. Unresolved: this is a divergence, not a contradiction, and the
authors decide which clause the repository should cite.
