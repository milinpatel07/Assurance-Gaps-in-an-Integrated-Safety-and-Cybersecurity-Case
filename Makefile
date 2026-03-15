# Makefile for reproducible generation of all results
# Assurance Gaps in an Integrated Safety and Cybersecurity Case
# for an AI-Based Perception Component in Highly Automated Driving
#
# Usage:
#   make install      — Install dependencies
#   make results      — Generate all results (JSON, CSV, LaTeX, figures)
#   make test         — Run the test suite
#   make gsn          — Render GSN diagrams from YAML (requires gsn2x)
#   make figures      — Generate figures only
#   make latex        — Generate LaTeX tables only
#   make clean        — Remove generated output
#   make all          — Install, test, and generate results
#
# Reproducibility:
#   All evaluation results are deterministic given SEED=42 and SCENES=50.
#   To reproduce with different parameters:
#     make results SEED=123 SCENES=100

PYTHON   ?= python
SEED     ?= 42
SCENES   ?= 50
OUTDIR   ?= output
GSN2X    ?= gsn/gsn2x

.PHONY: all install test results figures latex gsn gsn-install clean help

all: install test results

help:
	@echo "Available targets:"
	@echo "  install      — Install project dependencies"
	@echo "  test         — Run test suite (pytest)"
	@echo "  results      — Generate all results (JSON, CSV, LaTeX, figures)"
	@echo "  gsn          — Render GSN diagrams from YAML via gsn2x"
	@echo "  gsn-install  — Download gsn2x binary for Linux"
	@echo "  figures      — Generate visualization figures only"
	@echo "  latex        — Generate LaTeX tables only"
	@echo "  clean        — Remove generated output directory"
	@echo "  all          — install + test + results"
	@echo ""
	@echo "Parameters:"
	@echo "  SEED=$(SEED)       Random seed for evaluation"
	@echo "  SCENES=$(SCENES)     Scenes per weather condition"
	@echo "  OUTDIR=$(OUTDIR)    Output directory"

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

results: $(OUTDIR)/analysis_results.json

$(OUTDIR)/analysis_results.json:
	$(PYTHON) -m src.results.generate_all \
		--seed $(SEED) \
		--scenes $(SCENES) \
		--output $(OUTDIR)

figures: $(OUTDIR)/figures/integrated_gsn.png

$(OUTDIR)/figures/integrated_gsn.png:
	$(PYTHON) -m src.results.generate_all \
		--seed $(SEED) \
		--scenes $(SCENES) \
		--output $(OUTDIR)

latex: $(OUTDIR)/latex/table1_standards.tex

$(OUTDIR)/latex/table1_standards.tex:
	$(PYTHON) -m src.results.generate_all \
		--seed $(SEED) \
		--scenes $(SCENES) \
		--output $(OUTDIR)

# ── GSN diagram rendering via gsn2x ──────────────────────────────
# GSN YAML files in gsn/ are the single source of truth for the
# argument structure. gsn2x renders them to SVG following the
# GSN Community Standard v3.

gsn-install:
	@echo "Downloading gsn2x v4.2.3..."
	curl -sL "https://github.com/jonasthewolf/gsn2x/releases/download/v4.2.3/gsn2x-Linux" \
		-o $(GSN2X) && chmod +x $(GSN2X)
	@echo "Installed: $$($(GSN2X) --version)"

gsn: gsn/integrated_pattern.gsn.svg gsn/evidence_convergence.gsn.svg

gsn/integrated_pattern.gsn.svg: gsn/integrated_pattern.gsn.yaml
	$(GSN2X) $<
	@rm -f evidence.md

gsn/evidence_convergence.gsn.svg: gsn/evidence_convergence.gsn.yaml
	$(GSN2X) $<
	@rm -f evidence.md

clean:
	rm -rf $(OUTDIR)
	rm -f gsn/*.svg
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
