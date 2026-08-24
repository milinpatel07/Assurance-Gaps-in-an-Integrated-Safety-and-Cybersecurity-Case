# CARLA Configuration Descriptions

Provenance: hand-written. These two files record parameters for a reader. No
module loads them, and nothing here was measured or generated.

`detector_config.yaml` describes the SECOND detector and the five-member deep
ensemble of the case study. `weather_grid.yaml` describes the 5x5 rain and fog
grid used for SOTIF triggering-condition coverage.

## What they are for

They exist so that a reader can see the case-study parameters in one place
without reading Python. The values that the pipeline actually uses live in
`src/`, hard-coded:

| Parameter | Documented here | Used by |
|---|---|---|
| Rain levels (mm/h) | `weather_grid.yaml` | `RAIN_LEVELS` in `src/evaluation/weather_conditions.py` |
| Visibility levels (m) | `weather_grid.yaml` | `VISIBILITY_LEVELS` in the same module |
| Triggering thresholds (20 mm/h, 200 m) | `weather_grid.yaml` | `WeatherCondition.from_physical_parameters()` |
| Voxel size, point-cloud range, voxel limits | `detector_config.yaml` | `KITTI_VOXEL_CONFIG` in `src/perception/voxelization.py` |
| Ensemble size | `detector_config.yaml` | `src/perception/deep_ensemble.py` |

The thresholds in the third row are choices made for this case study. ISO
21448:2022 Clause 7 covers identifying hazardous scenarios and triggering
conditions, and sets no numeric weather values. No number in either file comes
from a standard.

The agreement is checked. `tests/test_config_documentation.py` reads both YAML
files and compares them against the constants in `src/`, including the rain and
visibility levels, the voxel geometry, and the ensemble size. It also re-derives
the triggering split from the thresholds written in `weather_grid.yaml` and
requires 21 of the 25 conditions to come out triggering, which is what
`generate_weather_grid()` produces. Editing a value in these files changes no
behaviour, so a change here that is not mirrored in `src/` will fail that test.

Run it with:

```bash
pytest tests/test_config_documentation.py -v
```

`configs/case_study.yaml` and `configs/standards.yaml` at the repository root
are documentation in the same sense. The case-study file is covered by the same
test; `configs/standards.yaml` is prose about clauses and is not.

## The detector named here

`detector_config.yaml` describes SECOND, the architecture the WAISE paper names.
The measured results in `data/empirical_results/` come from PointPillars instead.
That substitution and its reason are stated in
`data/empirical_results/README.md`. The weather-grid evaluation in
`data/synthetic_illustrations/` runs no detector at all. It is a seeded
illustration, and `src/evaluation/carla_evaluator.py` never connects to CARLA.
