# Assurance Gaps in an Integrated Safety and Cybersecurity Case

Milin Patel and Rolf Jung, Kempten University of Applied Sciences.
Supplementary material for two SAFECOMP 2026 papers, both accepted.

Four standards apply at once to an AI perception component in a driverless
vehicle, and each one prescribes its own evidence. This repository builds the
single argument the four jointly imply, in the notation certification engineers
use, and reports what the combination exposes.

**Start here:** [the argument, one node at a time](docs/gsn_view.html) (works on
a phone) · [what it found](#what-it-found) · [reproduce it](#reproduce-it)

[![Open the anomaly walk in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/milinpatel07/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/blob/main/notebooks/anomaly_walk.ipynb)

## What it found

One node carries all four standards at once: the goal claiming that verification
and validation are sufficient. The four standards ask for four kinds of evidence
there, on four scales that do not convert into one another: a pass/fail coverage
figure, a count of scenarios, a statistical uncertainty score, and an attack
success rate. No standard says how to combine them into one judgement. An
engineer can complete every prescribed activity and still be unable to state
whether the evidence together is enough.

![The integrated argument: nine goals, with the four standards meeting at G5](docs/figures/integrated_gsn.png)

## The two papers

| Paper | Question | Backed by code? |
|---|---|---|
| [`paper/waise2026/`](paper/waise2026/) | What does combining the four standards expose at design time? | Yes, `src/` |
| [`paper/safecomp2026-position/`](paper/safecomp2026-position/) | An alarm fires in service. Which concern owns it? | No, and none is meant to |

The WAISE paper builds the nine-goal pattern, extending ISO/PAS 8800 Annex B
from six goals. It catalogues seven decision points, where the standards hand a
choice to the project rather than prescribe one, and five findings, two of which
appear only once the standards are combined. The `src/` code produces all three
sets and the test suite checks them against the paper.

The position paper argues at clause level that no standard assigns a runtime
anomaly to a concern, so a service alarm caused by weather and one caused by an
attack are indistinguishable in the assurance argument. It is argued from clause
text, not from code.

The four standards are ISO 26262 (functional safety), ISO 21448 (hazards that
arise while the function works as designed), ISO/SAE 21434 (cybersecurity) and
ISO/PAS 8800 (safety of AI). The case study is a LiDAR 3D object detector for
cars, pedestrians and cyclists in a vehicle with no driver to fall back on.

**Follow one anomaly yourself.** `notebooks/anomaly_walk.ipynb` takes a single
runtime alarm and asks each standard, clause by clause, whether it owns it. The
walk ends without an answer. That is the position paper's argument, executable.

**One problem, two lifecycle points.** Each paper reports the same junction:
evidence on scales that do not convert into one another, and no clause saying
how to combine it. [`docs/seam.html`](docs/seam.html) sets the two side by side.
That connection is a synthesis drawn here, not a claim either paper makes.

## Reproduce it

```bash
pip install -r requirements.lock && pip install -e . --no-deps
make reproduce
```

`make reproduce` regenerates every artefact both papers use, then diffs the
result against the copies committed here. It prints a diff and fails if anything
drifted. [REPRODUCING.md](REPRODUCING.md) covers the details, including the
Windows path-length trap and what the lockfile pins. PyTorch is not required.

## What each file is, and how far to trust it

Every artefact declares its provenance, because the four kinds are not
interchangeable:

| Kind | Where | What it means |
|---|---|---|
| Argued | `src/`, `gsn/` | The method and the argument, as described in the WAISE paper |
| Generated | `TRACEABILITY.md`, `docs/gsn_view.html`, `output/` | Rebuilt by a command; a test fails if the committed copy is stale |
| Seeded | `data/synthetic_illustrations/` | Deterministic output at seed 42. Illustrations of the pipeline, not measurements |
| Measured | `data/empirical_results/` | Real measurements from trained models. They support a paper in preparation, and neither paper here claims them |

[TRACEABILITY.md](TRACEABILITY.md) is the index: every number, table and figure
traces to a passage in a paper, a clause in a named standard edition, or a
command that regenerates it. It also carries the identifier crosswalk, since the
papers write DP-2 and F-3 where the code writes `I-2` and `Gap-3`.

[ERRATA.md](ERRATA.md) records what this work found about the camera-ready
papers, including one place where a table and the prose disagree with each other.

## Map

```
paper/waise2026/            Camera-ready source of the GSN pattern paper
paper/safecomp2026-position/  Camera-ready source of the position paper
src/                        The five-step method: claims, GSN, decision points, findings
gsn/                        The argument in YAML, rendered by gsn2x
tests/                      285 tests, including the paper's own claims
data/                       Seeded illustrations and measured results, each with a README
docs/                       The interactive argument view, figures, reference tables
notebooks/                  The analysis as a runnable notebook
Makefile                    reproduce, test, results, gsn, traceability, gsn-view
```

## Citation

Cite the papers, not this repository:

```bibtex
@inproceedings{PatelJungWAISE2026,
  author    = {Patel, Milin and Jung, Rolf},
  title     = {Integrating Cybersecurity into the {AI} Safety Assurance Argument:
               A {GSN} Pattern for {AI}-Based Perception Components in
               Highly Automated Driving},
  booktitle = {WAISE 2026 Workshop at SAFECOMP 2026},
  series    = {LNCS},
  publisher = {Springer},
  year      = {2026}
}

@inproceedings{PatelJungPosition2026,
  author    = {Patel, Milin and Jung, Rolf},
  title     = {Operational Safety and Cybersecurity Assurance for {AI}-Based
               Perception in Highly Automated Driving},
  booktitle = {SAFECOMP 2026},
  year      = {2026}
}
```

[CITATION.cff](CITATION.cff) carries the same details in machine-readable form.

## This page

The poster's QR code resolves to
<https://milinpatel07.github.io/Assurance-Gaps-in-an-Integrated-Safety-and-Cybersecurity-Case/>,
which GitHub Pages serves from [`docs/`](docs/). It carries four panels: the
interactive argument, the seam between the two papers, the traceability index,
and the papers themselves.

## Archive

Release `v1.0.0` is the camera-ready snapshot. `.zenodo.json` holds the archive
metadata, so publishing a GitHub release with the Zenodo integration enabled
mints a DOI without further editing. The DOI is added here once minted; no DOI
is claimed before it exists.

## License

MIT.
