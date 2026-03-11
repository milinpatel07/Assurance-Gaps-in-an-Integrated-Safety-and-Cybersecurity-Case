# Makefile for reproducible generation of all results
# Assurance Gaps in an Integrated Safety and Cybersecurity Case
# for an AI-Based Perception Component in Highly Automated Driving
#
# Usage:
#   make install      — Install dependencies
#   make results      — Generate all results (JSON, CSV, LaTeX, figures)
#   make test         — Run the test suite
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

.PHONY: all install test results figures latex clean help

all: install test results

help:
	@echo "Available targets:"
	@echo "  install   — Install project dependencies"
	@echo "  test      — Run test suite (pytest)"
	@echo "  results   — Generate all results (JSON, CSV, LaTeX, figures)"
	@echo "  figures   — Generate visualization figures only"
	@echo "  latex     — Generate LaTeX tables only"
	@echo "  clean     — Remove generated output directory"
	@echo "  all       — install + test + results"
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

clean:
	rm -rf $(OUTDIR)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
