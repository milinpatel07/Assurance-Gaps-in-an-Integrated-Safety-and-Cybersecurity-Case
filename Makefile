# Makefile for reproducible generation of all results
# Assurance Gaps in an Integrated Safety and Cybersecurity Case
# for an AI-Based Perception Component in Highly Automated Driving
#
# Run `make help` for every target and parameter.
#
# Reproducibility:
#   All outputs are deterministic given SEED=42 and SCENES=50.
#   To generate with different parameters:
#     make results SEED=123 SCENES=100
#   results, figures and latex always rerun the generator, so the new
#   parameters take effect even when output/ already exists.

PYTHON   ?= python
SEED     ?= 42
SCENES   ?= 50
OUTDIR   ?= output
GSN2X    ?= gsn/gsn2x

.PHONY: all install test results figures latex gsn gsn-install traceability \
        argument landing comparison playground numbers notebook pages reproduce \
        verify-refs clean help

all: install test results

help:
	@echo "Available targets:"
	@echo "  install        Install project dependencies (editable, with dev extras)"
	@echo "  test           Run the test suite (pytest)"
	@echo "  results        Generate all results (JSON, CSV, LaTeX, figures) into OUTDIR"
	@echo "  figures        Same as results: the generator writes figures with everything else"
	@echo "  latex          Same as results: the generator writes LaTeX tables with everything else"
	@echo "  gsn            Render the GSN diagrams from YAML via gsn2x"
	@echo "  gsn-install    Download the gsn2x binary for this platform"
	@echo "  traceability   Regenerate TRACEABILITY.md and its machine-readable export"
	@echo "  argument       Regenerate docs/argument.html (interactive GSN view)"
	@echo "  landing        Regenerate docs/index.html (start page)"
	@echo "  comparison     Regenerate docs/design-time-and-operation.html"
	@echo "  playground     Regenerate docs/g5-playground.html (G5 playground)"
	@echo "  numbers        Regenerate docs/numbers.html (where the numbers come from)"
	@echo "  notebook       Regenerate the G5 and runtime-anomaly notebooks"
	@echo "  pages          Regenerate every reader-facing generated page"
	@echo "  verify-refs    Regenerate into OUTDIR/_refcheck and diff against the committed references"
	@echo "  reproduce      results, then verify-refs"
	@echo "  clean          Remove the output directory, rendered GSN SVGs and Python caches"
	@echo "  all            install, test, results"
	@echo "  help           Show this list"
	@echo ""
	@echo "Parameters:"
	@echo "  SEED=$(SEED)       Random seed for the synthetic weather-grid illustration"
	@echo "  SCENES=$(SCENES)     Synthetic scenes per weather condition"
	@echo "  OUTDIR=$(OUTDIR)    Output directory"

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

# Regenerate the traceability index and its machine-readable export. Use
# --check in CI to fail on a stale copy.
traceability:
	$(PYTHON) -m src.results.traceability_index
	$(PYTHON) -m src.results.traceability_export

# Regenerate the interactive GSN view. Use --check in CI to fail on a stale copy.
argument:
	$(PYTHON) -m src.visualization.argument_page

# Regenerate the start page (the poster's QR target).
landing:
	$(PYTHON) -m src.visualization.landing_page

# Regenerate the design-time and operation comparison page.
comparison:
	$(PYTHON) -m src.visualization.comparison_page

# Regenerate the interactive G5 playground.
playground:
	$(PYTHON) -m src.visualization.playground_page

# Regenerate the page that explains where each count comes from.
numbers:
	$(PYTHON) -m src.visualization.numbers_page

# Regenerate the notebooks.
notebook:
	$(PYTHON) -m src.visualization.anomaly_notebook
	$(PYTHON) -m src.visualization.g5_notebook

# Every reader-facing generated page.
pages: argument landing comparison playground numbers notebook

# ── Reproducibility ──────────────────────────────────────────────
# One command from clone to every artefact the WAISE paper uses and every
# generated page, then check that the committed references match what the code
# generates today. A non-empty diff
# means a source changed without its references: fix the cause; never edit a
# reference by hand. data/empirical_results/ is excluded by declaration: its
# inputs belong to a paper in preparation (see that directory's README).
reproduce: results verify-refs

verify-refs:
	$(PYTHON) -m src.results.generate_all --seed $(SEED) --scenes $(SCENES) \
		--output $(OUTDIR)/_refcheck > /dev/null
	diff $(OUTDIR)/_refcheck/csv/gaps.csv data/synthetic_illustrations/gaps.csv
	diff $(OUTDIR)/_refcheck/csv/decision_points.csv data/synthetic_illustrations/decision_points.csv
	diff $(OUTDIR)/_refcheck/csv/weather_evaluation.csv data/synthetic_illustrations/weather_evaluation_seed42.csv
	diff $(OUTDIR)/_refcheck/summary_report.txt data/synthetic_illustrations/summary_report_seed42.txt
	$(PYTHON) -m src.results.traceability_index --check
	$(PYTHON) -m src.results.traceability_export --check
	$(PYTHON) -m src.visualization.argument_page --check
	$(PYTHON) -m src.visualization.landing_page --check
	$(PYTHON) -m src.visualization.comparison_page --check
	$(PYTHON) -m src.visualization.playground_page --check
	$(PYTHON) -m src.visualization.numbers_page --check
	$(PYTHON) -m src.visualization.anomaly_notebook --check
	$(PYTHON) -m src.visualization.g5_notebook --check
	@echo "All committed references match regeneration."

# results, figures and latex are phony: each run regenerates everything, so a
# changed SEED or SCENES always takes effect.
results figures latex:
	$(PYTHON) -m src.results.generate_all \
		--seed $(SEED) \
		--scenes $(SCENES) \
		--output $(OUTDIR)

# ── GSN diagram rendering via gsn2x ──────────────────────────────
# GSN YAML files in gsn/ are the single source of truth for the
# argument structure. gsn2x renders them to SVG following the
# GSN Community Standard v3.

# The release publishes one binary per platform: gsn2x-Linux, gsn2x-macOS and
# gsn2x-Windows.exe. The asset below is chosen for the current platform.
GSN2X_VERSION ?= v4.2.3

UNAME_S := $(shell uname -s)
ifeq ($(OS),Windows_NT)
    GSN2X_ASSET := gsn2x-Windows.exe
    GSN2X_BIN   := $(GSN2X).exe
else ifeq ($(UNAME_S),Darwin)
    GSN2X_ASSET := gsn2x-macOS
    GSN2X_BIN   := $(GSN2X)
else
    GSN2X_ASSET := gsn2x-Linux
    GSN2X_BIN   := $(GSN2X)
endif

gsn-install:
	@echo "Downloading gsn2x $(GSN2X_VERSION) asset $(GSN2X_ASSET)..."
	curl -fsSL "https://github.com/jonasthewolf/gsn2x/releases/download/$(GSN2X_VERSION)/$(GSN2X_ASSET)" \
		-o "$(GSN2X_BIN)"
	@chmod +x "$(GSN2X_BIN)" 2>/dev/null || true
	@echo "Installed: $$("$(GSN2X_BIN)" --version)"

# If gsn2x is already on the PATH, skip the download and use it:
#   make gsn GSN2X=gsn2x

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
