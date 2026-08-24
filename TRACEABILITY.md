# Traceability Index

Where every claim in this repository comes from. One index, not scattered
footnotes.

Each row traces to exactly one of three kinds of source, and says which:

| Kind | Meaning |
|---|---|
| **PAPER** | A passage in one of the two papers. Cited by section or table. |
| **CLAUSE** | A clause in a named edition of a named standard. |
| **COMMAND** | A command in this repository that regenerates it. |

Anything that traces to none of the three does not belong here. Where the
repository asserts something rather than computing it, the row says so.

This file is generated. Do not edit it by hand:

```bash
python -m src.results.traceability_index
```

The two papers:

- WAISE 2026, GSN integration: `paper/waise2026/CR_Submission_WAISE_SafeCompAssuranceGaps_SafetySecurityCase_AI_Perception_HAD.tex`
- SAFECOMP 2026 position: `paper/safecomp2026-position/CR_position_paper.tex`

## 1. Standards and editions

Every CLAUSE row elsewhere in this index refers to one of these editions.

| Code id | Edition as cited | Year | Normative here | Clauses | Claims |
|---|---|---|---|---|---|
| `ISO21434` | ISO/SAE 21434:2021 — Road vehicles — Cybersecurity engineering | 2021 | yes | 8 | 9 |
| `ISO21448` | ISO 21448:2022 — Road vehicles — Safety of the intended functionality | 2022 | yes | 17 | 11 |
| `ISO26262` | ISO 26262:2018 — Road vehicles — Functional safety | 2018 | yes | 10 | 9 |
| `ISOPAS8800` | ISO/PAS 8800:2024 — Road vehicles — Safety and artificial intelligence | 2024 | yes | 10 | 8 |
| `TR5469` | ISO/IEC TR 5469:2024 — AI — Functional safety and AI systems | 2024 | no (informative) | 7 | 3 |

The four normative standards are the ones counted by goal-density and by
any claim in the papers about "all four standards". ISO/IEC TR 5469 is
informative and is excluded from those counts.

## 2. Identifier crosswalk, paper to code

The papers and the code name the same objects differently. A reader holding
the paper and reading the code needs this table.

| Paper | Code | Object | Where in the code |
|---|---|---|---|
| DP-1 | `I-1` | Incompatible risk classification frameworks | `src/analysis/decision_points.py` |
| DP-2 | `I-2` | Evidence type asymmetry at V&V | `src/analysis/decision_points.py` |
| DP-3 | `I-3` | AI error terminology differs across standards | `src/analysis/decision_points.py` |
| DP-4 | `I-4` | 'Validation' defined differently across standards | `src/analysis/decision_points.py` |
| DP-5 | `I-5` | Cybersecurity-SOTIF boundary undefined for adversarial inputs | `src/analysis/decision_points.py` |
| DP-6 | `I-6` | Monitoring scope overlap — three regimes on one component | `src/analysis/decision_points.py` |
| DP-7 | `I-7` | Data sufficiency threshold undefined | `src/analysis/decision_points.py` |
| F-1 | `Gap-1` | No AI-specific quantitative reliability target | `src/analysis/gaps.py` |
| F-2 | `Gap-2` | No complete OTA re-assurance workflow for AI | `src/analysis/gaps.py` |
| F-3 | `Gap-3` | Adversarial-SOTIF boundary unowned — adversarial inputs that exploit functional insufficiencies fall between G7 and G8 | `src/analysis/gaps.py` |
| F-4 | `Gap-4` | No cross-domain release decision criteria — four separate evidence sets with no combined evaluation | `src/analysis/gaps.py` |
| F-5 | `Gap-5` | Data acceptance threshold undefined — no standard prescribes when training data are sufficient | `src/analysis/gaps.py` |

The paper calls DP-N "decision points" and F-N "integration-induced
findings and open methodological problems". The code calls them
inconsistencies (`I-N`) and gaps (`Gap-N`). The numbers correspond exactly;
only the prefixes differ. `gsn/integrated_pattern.gsn.yaml` still tags G9
with the older "Gap-2" spelling.

## 3. Goals of the integrated pattern

PAPER: Table 2 and Figure 2 of the WAISE paper. COMMAND: `python -m src.results.generate_all --seed 42 --scenes 50 --output output`

| Goal | Claim | Origin | Normative standards | Clause references |
|---|---|---|---|---|
| G1 | The AI-based perception component satisfies the integrated safety and cybersecurity req... | retained | ISO21434, ISO26262, ISOPAS8800 | ISO/PAS 8800 Annex B G1 (reformulated); ISO 26262-3 Cl.6 (ASIL context); ISO/SAE 21434 Cl.15 (TARA context) |
| G2 | The specification is sufficient for all applicable assurance domains: AI-specific compl... | retained | ISO21434, ISO21448, ISOPAS8800 | ISO/PAS 8800 Cl.5 (AI specification); ISO 21448 Table A.8 (17 specification items); ISO/SAE 21434 [RQ-06-01] (cybersecurity specification) |
| G3 | Training and test data are sufficient in quantity, distribution coverage, annotation qu... | retained | ISOPAS8800 | ISO/PAS 8800 Cl.8.4 (data quality); ISO/IEC TR 5469 Cl.9.3.2 (data linked to HARA, informative) |
| G4 | The AI design satisfies safety and cybersecurity requirements. Architecture decisions r... | retained | ISO21434, ISO21448, ISOPAS8800 | ISO/PAS 8800 Cl.7 (AI design principles); ISO 21448 Table A.9 (SOTIF design measures); ISO/SAE 21434 Cl.10 (cybersecurity control design) |
| G5 | Verification and validation evidence is sufficient across all assurance domains. Four e... | retained | ISO21434, ISO21448, ISO26262, ISOPAS8800 | ISO/PAS 8800 Cl.8-9 (AI V&V); ISO 26262-6 Cl.9 (MC/DC at ASIL D); ISO 21448 Cl.9-11 (scenario testing, triggering conditions); ISO/SAE 21434 Cl.10 (vulnerability analysis, pen testing) |
| G6 | Operational monitoring covers AI (OOD detection, distributional drift), SOTIF (field pe... | retained | ISO21434, ISO21448, ISOPAS8800 | ISO/PAS 8800 Cl.14 (AI monitoring); ISO 21448 Tables A.13-A.14 (field monitoring); ISO/SAE 21434 Cl.8 (continuous cybersecurity monitoring) |
| G7 | Residual risk from functional insufficiencies meets the acceptance criteria defined per... | new | ISO21448 | ISO 21448 Cl.6.5 (acceptance criteria); ISO 21448 Table A.10 (acceptance criteria evidence); ISO 21448 Annex A.1 (GSN, Example 2) |
| G8 | Cybersecurity risks identified through TARA are treated to an acceptable level. The saf... | new | ISO21434, ISO26262 | ISO/SAE 21434 Cl.3.1.11 (cybersecurity case); ISO/SAE 21434 Cl.15 (TARA); ISO/SAE 21434 [RQ-15-06] (safety bridge) |
| G9 | AI model modifications (OTA updates, retraining) are controlled with re-assurance crite... | undeveloped | (none) | ISO 26262-8 Cl.8 (change management, partial); ISO/PAS 8800 Cl.14.8.3 (partial re-approval, partial); ISO/IEC TR 5469 Table A.8 (change protocols, informative) |

G5 is the only goal drawing on all four normative standards. That is the
paper's central structural claim, and it is checked from both of the
repository's representations by
`tests/test_representation_consistency.py`.

## 4. Clause to node index

Every extracted claim, the clause it comes from, and the node it supports.
This is the machine-readable traceability the WAISE paper refers to in
Section 4.

| Standard | Clause | Claim | Node | Phase |
|---|---|---|---|---|
| `ISO21434` | Cl.10 | CLM-21434-CTRL-01 | G4 | Design / Training |
| `ISO21434` | Cl.10 | CLM-21434-VER-01 | G5 | Verification & Validation |
| `ISO21434` | Cl.15 | CLM-21434-TARA-01 | G1 | Concept / Requirements |
| `ISO21434` | Cl.15 | CLM-21434-TREAT-01 | G8 | Design / Training |
| `ISO21434` | Cl.15.8 | CLM-21434-RISK-01 | G8 | Concept / Requirements |
| `ISO21434` | Cl.3.1.11 | CLM-21434-CASE-01 | G8 | Verification & Validation |
| `ISO21434` | Cl.8 | CLM-21434-MON-01 | G6 | Operation / Monitoring |
| `ISO21434` | [RQ-06-01] | CLM-21434-SPEC-01 | G2 | Concept / Requirements |
| `ISO21434` | [RQ-15-06] | CLM-21434-BRIDGE-01 | G8 | Concept / Requirements |
| `ISO21448` | Cl.10 | CLM-21448-UNK-01 | G5 | Verification & Validation |
| `ISO21448` | Cl.11 | CLM-21448-VSTRAT-01 | G5 | Verification & Validation |
| `ISO21448` | Cl.12 | CLM-21448-REL-01 | G7 | Integration / Deployment |
| `ISO21448` | Cl.13 | CLM-21448-MON-01 | G6 | Operation / Monitoring |
| `ISO21448` | Cl.5 | CLM-21448-AREA-01 | G7 | Concept / Requirements |
| `ISO21448` | Cl.6.5 | CLM-21448-ACC-01 | G7 | Concept / Requirements |
| `ISO21448` | Cl.7 | CLM-21448-TRIG-01 | G2 | Concept / Requirements |
| `ISO21448` | Cl.9 | CLM-21448-VER-01 | G5 | Verification & Validation |
| `ISO21448` | Table A.10 | CLM-21448-RISK-01 | G7 | Verification & Validation |
| `ISO21448` | Table A.8 | CLM-21448-SPEC-01 | G2 | Concept / Requirements |
| `ISO21448` | Table A.9 | CLM-21448-DES-01 | G4 | Design / Training |
| `ISO26262` | Part 2, Cl.6.4 | CLM-26262-CASE-01 | G1 | Verification & Validation |
| `ISO26262` | Part 3, Cl.6 | CLM-26262-HARA-01 | G1 | Concept / Requirements |
| `ISO26262` | Part 3, Cl.6.4.3 | CLM-26262-CTRL-01 | G1 | Concept / Requirements |
| `ISO26262` | Part 4, Cl.6.4.3 | CLM-26262-TSC-01 | (out of scope) | Design / Training |
| `ISO26262` | Part 4, Cl.7 | CLM-26262-INTG-01 | G5 | Integration / Deployment |
| `ISO26262` | Part 4, Cl.8 | CLM-26262-SVAL-01 | G5 | Verification & Validation |
| `ISO26262` | Part 5, Cl.9 | CLM-26262-HWMET-01 | G5 | Verification & Validation |
| `ISO26262` | Part 6, Cl.9 | CLM-26262-MCDC-01 | G5 | Verification & Validation |
| `ISO26262` | Part 8, Cl.8 | CLM-26262-CHG-01 | G9 | Modification / Re-assurance |
| `ISOPAS8800` | Annex B | CLM-8800-G1 | G1 | Verification & Validation |
| `ISOPAS8800` | Annex B | CLM-8800-S1 | S1 | Verification & Validation |
| `ISOPAS8800` | Cl.14 | CLM-8800-G6 | G6 | Operation / Monitoring |
| `ISOPAS8800` | Cl.14.8.3 | CLM-8800-MOD-01 | G9 | Modification / Re-assurance |
| `ISOPAS8800` | Cl.5 | CLM-8800-G2 | G2 | Concept / Requirements |
| `ISOPAS8800` | Cl.7 | CLM-8800-G4 | G4 | Design / Training |
| `ISOPAS8800` | Cl.8.4 | CLM-8800-G3 | G3 | Design / Training |
| `ISOPAS8800` | Cl.9 | CLM-8800-G5 | G5 | Verification & Validation |
| `TR5469` | Cl.9.3.2 | CLM-TR5469-DATA-01 | G3 | Design / Training |
| `TR5469` | Cl.9.3.3 | CLM-TR5469-DATA-02 | G3 | Design / Training |
| `TR5469` | Table A.8 | CLM-TR5469-MOD-01 | G9 | Modification / Re-assurance |

### Claims deliberately outside the argument

**`CLM-26262-TSC-01`** (ISO26262 Part 4, Cl.6.4.3)

> A technical safety concept shall be derived from the functional safety concept.

System-level obligation. Cl.6.2 defines the technical safety concept as the technical safety requirements together with the system architectural design, and Cl.6.4.6.1 allocates those requirements to system, hardware or software as the implementing technology. That activity belongs to the encompassing system safety case (ISO 26262-2 Cl.6.4.8), above the AI component this pattern is scoped to. Neither G2 nor G4 declares ISO 26262 as a source, matching Table 2 of the WAISE paper.


## 5. Findings

PAPER: Table 4 of the WAISE paper. Lifecycle phases follow that table.

| Paper | Code | Lifecycle phase | Integration-induced | Partial coverage |
|---|---|---|---|---|
| F-1 | `Gap-1` | Concept, Verification | no | ISO 26262-5 Cl.9 (HW metrics: SPFM >= 99%, LFM >= 90%, PMHF < 10^-8 h^-1 — hardware only); ISO 21448 Cl.6.5 (qualitative acceptance criteria); ISO/IEC TR 5469 Cl.9.2.2 (non-separability acknowledged) |
| F-2 | `Gap-2` | Modification | no | ISO 26262-8 Cl.8 (change management — assumes conventional SW); ISO/PAS 8800 Cl.14.8.3 (partial re-approval — incomplete); ISO 24089 (software update engineering; specifies the update process, not re-assurance of a modified AI model's argument); ISO/IEC TR 5469 Table A.8 (change protocols — informative only) |
| F-3 | `Gap-3` | Verification, Operation | yes | ISO 21448 Cl.1 (explicitly excludes cybersecurity threats); ISO/SAE 21434 Cl.15 (includes adversarial scenarios) |
| F-4 | `Gap-4` | Integration | yes | ISO 26262-2 Cl.6.4 (functional safety assessment); ISO/SAE 21434 Cl.3.1.11 (cybersecurity case); ISO 21448 Cl.12 (SOTIF release decision) |
| F-5 | `Gap-5` | Design | no | ISO/PAS 8800 Cl.8.4, Annex B G3 (claim exists); ISO/IEC TR 5469 Cl.9.3.2 (data linked to HARA, informative); ISO/IEC TR 5469 Cl.9.3.3 (four criteria, informative) |

F-3 and F-4 are the integration-induced findings. F-3's invisibility from
any single standard is derived in `src/analysis/counterfactual.py`. F-4's
is derived there too, from a premise that module states as a premise rather
than proves. F-1, F-2 and F-5 are asserted, and that module says so.

## 6. Decision points

PAPER: Table 3 of the WAISE paper.

| Paper | Code | Type | Standards | GSN node |
|---|---|---|---|---|
| DP-1 | `I-1` | structural | ISO26262, ISO21448, ISO21434 | G1 |
| DP-2 | `I-2` | structural | ISO26262, ISO21448, ISOPAS8800, ISO21434 | G5 |
| DP-3 | `I-3` | terminological | ISO26262, ISO21448, TR5469 | G2, G7 |
| DP-4 | `I-4` | terminological | ISO26262, ISO21448, ISOPAS8800 | G5 |
| DP-5 | `I-5` | structural | ISO21448, ISO21434, TR5469 | G7, G8 |
| DP-6 | `I-6` | methodological | ISO21448, ISO21434, ISOPAS8800 | G6 |
| DP-7 | `I-7` | methodological | ISOPAS8800, TR5469 | G3 |

Split: 3 structural, 2 terminological, 2 methodological.

## 7. Artefacts and their provenance

Every artefact is measured, seeded, argued, or generated. No artefact is
left undeclared.

| Artefact | Provenance | Source |
|---|---|---|
| `output/analysis_results.json` | generated | COMMAND: `python -m src.results.generate_all --seed 42 --scenes 50 --output output` |
| `output/csv/*` | generated | COMMAND: `python -m src.results.generate_all --seed 42 --scenes 50 --output output` |
| `output/latex/*.tex` | generated | COMMAND: `python -m src.results.generate_all --seed 42 --scenes 50 --output output` |
| `output/figures/*` | generated | COMMAND: `python -m src.results.generate_all --seed 42 --scenes 50 --output output` |
| `docs/figures/*.png` | seeded and derived | COMMAND: as above. See `docs/figures/README.md` |
| `data/synthetic_illustrations/*` | seeded, seed 42 | COMMAND: as above. Not measurements. See that directory's README |
| `data/empirical_results/*` | measured | Trained PointPillars ensemble, external to this repository. Cited by neither paper. See that directory's README |
| `data/carla_configs/*.yaml` | hand-written | Documentation only. Checked against `src/` by `tests/test_config_documentation.py` |
| `configs/*.yaml` | hand-written | Documentation only. No code loads them |
| `gsn/*.gsn.yaml` | hand-written | Source for the rendered GSN diagrams |
| `gsn/*.svg` | generated | COMMAND: `make gsn`, or `gsn2x gsn/<file>.gsn.yaml` |

The one number in the WAISE paper's case study that comes from measurement
is the ensemble-disagreement AUROC at G5 evidence type (c), and the paper
attributes it to the VEHITS 2026 companion study, measured on simulated
ensemble outputs. Evidence types (a), (b) and (d) are marked not produced in
the paper's own Figure 2(b).

## 8. The position paper

The position paper is argued at clause level. No file in `src/` supports it,
and none is meant to. This is a fact about its scope, not a gap in the
repository. Its claims trace to CLAUSE and to PAPER, never to COMMAND.

| Claim | Kind | Source |
|---|---|---|
| A runtime anomaly carries no concern label | PAPER | Position paper, section on assignment and resolution; Figure 1 |
| Missing step 1: no clause assigns an unlabelled anomaly to a concern | PAPER + CLAUSE | Position paper, Table 1 footnote, over ISO 21448:2022, ISO/PAS 8800:2024, ISO/SAE 21434:2021 |
| Missing step 2: no clause resolves per-concern re-evaluations into one judgment | PAPER + CLAUSE | Position paper, Table 1 footnote, same three standards |
| ISO 21448 defines a SOTIF argument on a field result | CLAUSE | ISO 21448:2022 Clause 13.4 |
| ISO/SAE 21434 monitoring ends in risk treatment, with no re-evaluation of the cybersecurity case | CLAUSE | ISO/SAE 21434:2021, Clause 8 |
| Requirements R1 to R4 that a closing method must satisfy | PAPER | Position paper, section stating the position |
| No published incident is attributed to this ambiguity | PAPER | Stated by the authors in the position paper itself |

## 9. Known inconsistencies

Recorded here so a reader meets them rather than discovering them alone.

**DP-2 is typed differently in the paper's own table and prose.** Table 3
tags DP-2 "S, M". The prose calls it structural in three places: the
structural list "(DP-1, DP-2, DP-5)", the subsection heading "DP-2:
Evidence type asymmetry at V&V (structural decision point)", and the
discussion, "the evidence asymmetry at G5 (DP-2) is a structural property".
The last two are camera-ready additions. The authors resolved this in favour
of the prose, so the code types I-2 structural. This is an inconsistency
inside the camera-ready, not a defect in this repository.

**Test count.** The WAISE paper reports 193 tests. The suite has held at
192 since the findings were revised from six to five, which removed one
test (commit `4d782b0`), and has grown since with tests added after
publication. The paper was correct when written. No test was added or
removed here to make the numbers agree.

**Two representations of goal sources.** `source_standards` on each goal and
the claim-to-goal mapping are maintained separately. They agree everywhere
except G8 and G9, where the reasons are recorded in
`tests/test_representation_consistency.py` and enforced there.

**Architecture substitution.** The WAISE paper names SECOND as the
case-study architecture. The measured results in `data/empirical_results/`
use PointPillars. Both are OpenPCDet voxel single-stage detectors. The
substitution is stated in that directory's README and not in the paper.
Neither paper cites those files.
