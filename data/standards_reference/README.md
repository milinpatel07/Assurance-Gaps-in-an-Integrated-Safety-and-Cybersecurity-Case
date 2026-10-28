# Standards and case-study reference (documentation only)

Provenance: hand-written. `standards.yaml` lists the four standards (ISO 26262,
ISO 21448, ISO/SAE 21434, ISO/PAS 8800) and the informative technical report
ISO/IEC TR 5469, each with its edition, scope, relevance to the case study and
the parts or clauses the analysis draws on. `case_study.yaml` describes the case
study: the HARA result, the TARA threat scenarios, the detector and deep-ensemble
configuration and the evaluation settings. No module in `src/` loads either
file; the code holds its own copy of the values it uses.
`tests/test_config_documentation.py` checks the voxel size, voxel limit, class
names and ensemble size in `case_study.yaml`; `standards.yaml` is not checked.
