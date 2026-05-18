# Empirical Results

This directory holds empirical evaluation results for the deep-ensemble uncertainty
signal used as verification and monitoring evidence in the integrated GSN argument
pattern. These are real measurements from trained models, in contrast to the
deterministic seeded outputs in `data/synthetic_illustrations/`.

## 1. Provenance

The detector is PointPillars, a voxel-based single-stage 3D object detector, trained
with the OpenPCDet framework. Uncertainty is obtained from a deep ensemble of five
members trained independently. Two datasets are used: KITTI (classes `Car`,
`Pedestrian`, `Cyclist`) and nuScenes.

Three training configurations are represented:

| Configuration | Ensemble members | Training | Role |
|---------------|------------------|----------|------|
| KITTI v1   | shared seed          | 80 epochs | controlled-experiment failure-mode baseline |
| KITTI v2   | per-member seeds 1-5 | 10 epochs | working ensemble |
| nuScenes   | per-member seeds 1-5 | 10 epochs | second-dataset generalisation |

The deep ensemble uses five members with per-member seeds 1-5 in the KITTI v2 and
nuScenes configurations. The per-member softmax baseline files for KITTI v2 and
nuScenes record seeds 1-4 plus the across-seed mean; the KITTI v1 baseline file
records seeds 1-5 plus the mean.

## 2. The three-way controlled experiment

A deep ensemble quantifies uncertainty through disagreement between members. If all
members are trained from the same random seed (KITTI v1), they converge to near-
identical functions, their disagreement carries little information, and the frame-
level uncertainty score does not separate error frames from clean frames. For
KITTI v1 the mean and exceedance strategies (S2, S3) reach AUROC 0.28 and 0.27,
below the 0.5 random baseline.

Training each member from a distinct seed, 1 through 5 (KITTI v2), restores member
diversity. On the `severe` frame-label type the five strategies reach AUROC
0.67-0.82. Repeating the per-member-seed scheme on nuScenes reaches AUROC 0.45-0.85
on the `any` frame-label type, which indicates the signal is not specific to KITTI.

The contrast between KITTI v1 and KITTI v2 shows that per-member seed diversity is a
necessary condition for the deep-ensemble uncertainty signal to be informative. The
three configurations together are the empirical evidence: a measurable failure mode
(v1) and a measurable success regime (v2, nuScenes).

The five aggregation strategies convert per-object uncertainty into a per-frame
score: S1 worst case (maximum), S2 mean, S3 exceedance count, S4 class-weighted,
S5 range-weighted. The frame-label types are `severe`, `any`, `FN` (frames
containing a false negative), and `FP` (frames containing a false positive);
nuScenes results omit `severe`. AUROC depends strongly on the frame-label type. For
the KITTI v2 ensemble: `severe` 0.67-0.82, `any` 0.996-0.999, `FP` 0.997-1.000,
`FN` 0.54-0.59. The `any` and `FP` types are near-saturated; `FN`, the safety-
relevant case of a missed object, is the hardest and sits just above random.

## 3. Mapping to the integrated GSN pattern

`kitti_v2_evidence/` and `nuscenes_evidence/` support G5 (V&V sufficiency evidence,
ISO/PAS 8800 Cl. 8-9). The headline AUROC values, each with a 95% confidence
interval, are the AI-specific verification metric: they quantify how well the
ensemble uncertainty score discriminates error frames. They are reported per frame-
label type because the metric is informative for `severe` frames and weak for `FN`
frames, and the G5 sufficiency argument has to expose that scope.

`controlled_experiment/` holds the KITTI v1 failure-mode arm, including the runtime-
monitor evidence: missed-detection rate (MDR) and false-alarm rate (MFAR) at four
score thresholds, at IoU matching thresholds 0.5 and 0.7. This maps to G6 (runtime
monitoring, ISO/PAS 8800 Cl. 14). Because the v1 members lack diversity, the monitor
AUROC is 0.25-0.50 and no threshold yields a usable MDR/MFAR pair. These files
document that ensemble diversity is required for the runtime monitor to be
informative.

`three_way_comparison/` holds the headline three-configuration table and the
corresponding figures.

## 4. Relationship to the submitted WAISE paper

Section 3.1 of the paper names SECOND as the example case study architecture. The
empirical evaluation here uses PointPillars. Both are voxel-based single-stage 3D
object detectors implemented in OpenPCDet. The deep ensemble methodology
(Lakshminarayanan et al., 2017) and the use of ensemble uncertainty as evidence at
G5 and G6 do not depend on the detector backbone. PointPillars was used here because
trained weights and the experimental infrastructure were available from the parent
project (paper P5). The paper text is unchanged; this directory states the detector
substitution directly.

## 5. File-by-file description

### three_way_comparison/
- `three_way_summary.csv` - columns `strategy, kitti_v1_baseline, kitti_v1_ensemble,
  kitti_v2_baseline, kitti_v2_ensemble, nuscenes_baseline, nuscenes_ensemble`; one
  row per strategy S1-S5; each cell is `auroc [ci_lo, ci_hi]` or `n/a`. The frame-
  label type is not uniform across columns: the `kitti_v1_*` and `nuscenes_*`
  columns use the `any` type, the `kitti_v2_*` columns use the `severe` type
  (KITTI v2 `any` is saturated near 1.0). `kitti_v1_ensemble` is `n/a` for S1 and S4.
- `fig_03_three_config_auroc.pdf` - ensemble AUROC for the three configurations
  across the five strategies, with 95% CI error bars and a 0.5 reference line.
- `fig_06_baseline_vs_ensemble.pdf` - per-member softmax baseline against the deep
  ensemble for KITTI v2 and nuScenes, across the five strategies.
- `fig_04_controlled_experiment.pdf` - KITTI v1 against KITTI v2 across the five
  strategies; annotates the S2 change from 0.28 to 0.72.
- `T1_three_way_auroc.pdf` - verification figure for the three-configuration
  ensemble comparison; AUROC for `any`-error frame discrimination, KITTI v1 / v2 /
  nuScenes, five strategies, 95% CI error bars.
- `T2_baseline_vs_ensemble.pdf` - verification figure comparing the single-model
  softmax baseline against the deep-ensemble monitor for all three configurations
  (six series); a superset of `fig_06`, which omits the KITTI v1 pair.

### kitti_v2_evidence/
- `headline_metrics.csv` - columns `strategy, label, auroc, ci_lo, ci_hi, note`;
  KITTI v2 ensemble; 5 strategies x 4 frame-label types (`severe, any, FN, FP`) =
  20 rows; AUROC range 0.544 (`FN`) to 1.000 (`FP`).
- `baseline_softmax_metrics.csv` - columns `seed, strategy, label, auroc, ci_lo,
  ci_hi, note`; per-member softmax baseline on KITTI v2; seeds 1-4 and the across-
  seed `mean`; labels `severe` and `any`; 50 rows; across-seed mean AUROC
  0.36-0.63.
- `auroc_heatmap.pdf` - AUROC heatmap across configurations, strategies, and frame-
  label types.
- `auroc_false_negative.pdf` - AUROC for `FN`-frame discrimination, KITTI v2 vs
  nuScenes.

### nuscenes_evidence/
- `headline_metrics.csv` - same column schema as the KITTI v2 headline; nuScenes
  ensemble; 5 strategies x 3 frame-label types (`any, FN, FP`; no `severe`) = 15
  rows; AUROC range 0.454 to 0.987.
- `baseline_softmax_metrics.csv` - same schema as the KITTI v2 baseline; nuScenes
  per-member softmax baseline; seeds 1-4 and `mean`; label `any` only; 25 rows;
  across-seed mean AUROC 0.08-0.62.
- `kitti_v1_vs_nuscenes.csv` - per-strategy baseline and ensemble AUROC with CIs for
  KITTI and nuScenes. The KITTI columns hold the KITTI v1 values (baseline
  0.70-0.79, ensemble 0.27-0.47, blank for S1 and S4); the nuScenes columns hold
  the nuScenes baseline and ensemble. The KITTI side of this file is the v1
  configuration, which the filename states.

### controlled_experiment/
- `kitti_v1_metrics.csv` - columns `metric, strategy, value`; KITTI v1 ensemble;
  AUROC by frame-label type (`FN, FP, any`), by class (`Car, Pedestrian, Cyclist`),
  and by distance band (`0_20, 20_40, 40_80` m); the Spearman correlation between
  the S2 score and frame error count (-0.382); two frame ids. AUROC range 0.249 to
  0.553.
- `kitti_v1_baseline_softmax.csv` - columns `method, metric, value`; per-member
  softmax baseline for KITTI v1; seeds 1-5 and the across-seed mean; `value` is
  `point [ci_lo, ci_hi]`; AUROC 0.693 to 0.812.
- `kitti_v1_mdr_mfar_iou0.5.csv`, `kitti_v1_mdr_mfar_iou0.7.csv` - columns
  `strategy, threshold_name, threshold, MDR, MFAR, AUROC`; KITTI v1 runtime monitor
  operating points at IoU matching thresholds 0.5 and 0.7; four score thresholds
  per strategy (`theta_emp, theta_0.01, theta_0.05, theta_0.10`).

## 6. Reproduction

The detector follows the PointPillars architecture (Lang et al., 2019), trained
with OpenPCDet (OpenPCDet Development Team, 2020). A deep ensemble
(Lakshminarayanan et al., 2017) is built by training five members independently. In
the KITTI v1 configuration the five members share one random seed and train for
80 epochs; in the KITTI v2 and nuScenes configurations each member uses a distinct
seed, 1 through 5, and trains for 10 epochs. Inference produces per-object
detections and per-object uncertainty from ensemble disagreement. The five frame-
level aggregation strategies S1-S5 reduce per-object uncertainty to a per-frame
score: S1 maximum, S2 mean, S3 exceedance count, S4 class-weighted, S5 range-
weighted. AUROC is computed against frame error labels.

The exact training and evaluation scripts used to produce these specific CSVs and
figures are part of paper P5 (in preparation by the same author). Once P5 is
published, this README will be updated with a direct citation and the precise
command sequence.

## 7. Limitations

This evidence is measured on the KITTI and nuScenes recorded datasets, not on the
CARLA weather-degraded scenarios described in paper Section 3.1. The CARLA weather-
grid evaluation in the paper is illustrated, not measured: `src/evaluation/
carla_evaluator.py` produces it from a deterministic seeded function (see
`data/synthetic_illustrations/`). The two pipelines are complementary - the
empirical results here show the uncertainty signal is informative on real data
under a proper experimental design, and the synthetic illustration shows the
analysis workflow under the SOTIF triggering-condition framing. Neither replaces
the other. The `FN`-frame AUROC near 0.55 also bounds the current strength of the
signal for the safety-relevant missed-detection case.

## 8. Citations

- Lang, A. H., Vora, S., Caesar, H., Zhou, L., Yang, J., Beijbom, O. (2019).
  PointPillars: Fast Encoders for Object Detection from Point Clouds. CVPR 2019.
- Lakshminarayanan, B., Pritzel, A., Blundell, C. (2017). Simple and Scalable
  Predictive Uncertainty Estimation Using Deep Ensembles. NeurIPS 2017.
- OpenPCDet Development Team (2020). OpenPCDet: An Open-source Toolbox for 3D Object
  Detection from Point Clouds. https://github.com/open-mmlab/OpenPCDet
- Geiger, A., Lenz, P., Urtasun, R. (2012). Are we ready for autonomous driving?
  The KITTI vision benchmark suite. CVPR 2012.
- Caesar, H., Bankiti, V., Lang, A. H., Vora, S., Liong, V. E., Xu, Q., Krishnan, A.,
  Pan, Y., Baldan, G., Beijbom, O. (2020). nuScenes: A multimodal dataset for
  autonomous driving. CVPR 2020.
- Paper P5 - Patel, M. Runtime monitoring project, in preparation by the same
  author. Full citation to be added on publication.
