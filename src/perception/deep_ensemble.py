"""Deep ensemble for uncertainty quantification in 3D object detection.

Implements the deep ensemble approach (Lakshminarayanan et al., 2017)
applied to the SECOND detector. Independently trained ensemble members
produce separate 3D bounding box predictions. Geometric divergence
between members quantifies prediction uncertainty.

This component is relevant to two nodes in the integrated GSN:
- G5 (verification): one form of AI-specific evaluation evidence
  as prescribed by ISO/PAS 8800 Clauses 8-9
- G6 (monitoring): one form of runtime OOD indicator
  as prescribed by ISO/PAS 8800 Clause 14

Reference: Lakshminarayanan et al., "Simple and Scalable Predictive
Uncertainty Estimation Using Deep Ensembles", NeurIPS 2017.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from src.perception.second_detector import DetectionConfig, Detection3D


@dataclass
class EnsembleConfig:
    """Configuration for the deep ensemble.

    Attributes:
        num_members: Number of independently trained ensemble members.
        detection_config: Configuration for each SECOND detector.
        nms_threshold: Non-maximum suppression IoU threshold.
        score_threshold: Minimum score for detections.
        divergence_threshold: Geometric divergence threshold for OOD detection.
    """

    num_members: int = 5
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    nms_threshold: float = 0.1
    score_threshold: float = 0.3
    divergence_threshold: float = 0.5


@dataclass
class EnsemblePrediction:
    """Aggregated prediction from the deep ensemble.

    Attributes:
        mean_box: Mean 3D bounding box across ensemble members.
        box_variance: Variance of each box parameter across members.
        mean_score: Mean confidence score.
        geometric_divergence: Divergence measure between member predictions.
        num_agreeing_members: How many members detected this object.
        class_id: Predicted class.
        class_name: Predicted class name.
        is_uncertain: Whether divergence exceeds threshold (OOD indicator).
        member_boxes: Individual predictions from each member.
    """

    mean_box: np.ndarray
    box_variance: np.ndarray
    mean_score: float
    geometric_divergence: float
    num_agreeing_members: int
    class_id: int
    class_name: str = ""
    is_uncertain: bool = False
    member_boxes: list[np.ndarray] = field(default_factory=list)


def compute_box_iou_3d(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """Compute approximate 3D IoU between two axis-aligned boxes.

    Boxes are [x, y, z, w, l, h, theta]. Rotation is ignored for
    the approximate IoU used in ensemble matching.
    """
    # Extract centers and dimensions
    xa, ya, za = box_a[0], box_a[1], box_a[2]
    wa, la, ha = box_a[3], box_a[4], box_a[5]
    xb, yb, zb = box_b[0], box_b[1], box_b[2]
    wb, lb, hb = box_b[3], box_b[4], box_b[5]

    # Compute axis-aligned intersection
    x_overlap = max(0, min(xa + wa / 2, xb + wb / 2) - max(xa - wa / 2, xb - wb / 2))
    y_overlap = max(0, min(ya + la / 2, yb + lb / 2) - max(ya - la / 2, yb - lb / 2))
    z_overlap = max(0, min(za + ha / 2, zb + hb / 2) - max(za - ha / 2, zb - hb / 2))

    intersection = x_overlap * y_overlap * z_overlap
    vol_a = wa * la * ha
    vol_b = wb * lb * hb
    union = vol_a + vol_b - intersection

    if union < 1e-6:
        return 0.0
    return intersection / union


def compute_geometric_divergence(boxes: list[np.ndarray]) -> float:
    """Compute geometric divergence across ensemble member predictions.

    The divergence measures how much ensemble members disagree about the
    geometry (position, size, orientation) of a detected object.
    High divergence = high uncertainty = potential OOD input.

    Method: average pairwise (1 - IoU) across all ensemble member pairs.

    Args:
        boxes: List of (7,) bounding boxes from different ensemble members.

    Returns:
        Divergence in [0, 1]. 0 = perfect agreement, 1 = no overlap.
    """
    if len(boxes) < 2:
        return 0.0

    n = len(boxes)
    total_distance = 0.0
    num_pairs = 0

    for i in range(n):
        for j in range(i + 1, n):
            iou = compute_box_iou_3d(boxes[i], boxes[j])
            total_distance += 1.0 - iou
            num_pairs += 1

    return total_distance / num_pairs if num_pairs > 0 else 0.0


def match_detections_across_members(
    member_detections: list[list[Detection3D]],
    iou_threshold: float = 0.3,
) -> list[list[tuple[int, Detection3D]]]:
    """Match detections across ensemble members by spatial proximity.

    Uses greedy matching based on 3D IoU to associate detections from
    different ensemble members that correspond to the same physical object.

    Args:
        member_detections: List of detection lists, one per ensemble member.
        iou_threshold: Minimum IoU for two detections to be considered matched.

    Returns:
        List of matched groups. Each group is a list of (member_idx, Detection3D).
    """
    if not member_detections or not member_detections[0]:
        return []

    # Use first member as reference
    groups: list[list[tuple[int, Detection3D]]] = []
    for det in member_detections[0]:
        groups.append([(0, det)])

    # Match subsequent members
    for m_idx in range(1, len(member_detections)):
        used = set()
        for g_idx, group in enumerate(groups):
            ref_box = group[0][1].box
            best_iou = -1.0
            best_det_idx = -1

            for d_idx, det in enumerate(member_detections[m_idx]):
                if d_idx in used:
                    continue
                iou = compute_box_iou_3d(ref_box, det.box)
                if iou > iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_det_idx = d_idx

            if best_det_idx >= 0:
                group.append((m_idx, member_detections[m_idx][best_det_idx]))
                used.add(best_det_idx)

        # Unmatched detections from this member start new groups
        for d_idx, det in enumerate(member_detections[m_idx]):
            if d_idx not in used:
                groups.append([(m_idx, det)])

    return groups


def aggregate_ensemble_predictions(
    member_detections: list[list[Detection3D]],
    config: EnsembleConfig,
) -> list[EnsemblePrediction]:
    """Aggregate predictions from all ensemble members.

    This is the main function that produces the uncertainty-aware detections
    used as evidence for G5 and G6 in the integrated GSN.

    Args:
        member_detections: Detections from each ensemble member.
        config: Ensemble configuration.

    Returns:
        List of aggregated predictions with uncertainty metrics.
    """
    matched_groups = match_detections_across_members(
        member_detections, iou_threshold=config.nms_threshold
    )

    predictions = []
    for group in matched_groups:
        boxes = [det.box for _, det in group]
        scores = [det.score for _, det in group]
        class_ids = [det.class_id for _, det in group]

        boxes_array = np.array(boxes)
        mean_box = np.mean(boxes_array, axis=0)
        box_variance = np.var(boxes_array, axis=0)
        mean_score = np.mean(scores)
        divergence = compute_geometric_divergence(boxes)

        # Majority vote for class
        class_id = max(set(class_ids), key=class_ids.count)

        pred = EnsemblePrediction(
            mean_box=mean_box,
            box_variance=box_variance,
            mean_score=mean_score,
            geometric_divergence=divergence,
            num_agreeing_members=len(group),
            class_id=class_id,
            is_uncertain=divergence > config.divergence_threshold,
            member_boxes=boxes,
        )
        predictions.append(pred)

    # Filter by score
    predictions = [p for p in predictions if p.mean_score >= config.score_threshold]

    return predictions


def compute_ensemble_auroc(
    predictions: list[EnsemblePrediction],
    ground_truth_is_ood: list[bool],
) -> float:
    """Compute AUROC for OOD detection using geometric divergence.

    This metric is the case study instance of the AI-specific evaluation
    evidence at G5 (ISO/PAS 8800 Cl.8-9). It has no standard-defined
    threshold corresponding to ASIL D (Gap-1).

    Args:
        predictions: Ensemble predictions with divergence values.
        ground_truth_is_ood: Whether each prediction is truly OOD.

    Returns:
        Area Under the ROC Curve for OOD detection.
    """
    if not predictions or not ground_truth_is_ood:
        return 0.0

    # Simple AUROC computation via the Wilcoxon-Mann-Whitney statistic
    ood_scores = [
        p.geometric_divergence
        for p, is_ood in zip(predictions, ground_truth_is_ood)
        if is_ood
    ]
    id_scores = [
        p.geometric_divergence
        for p, is_ood in zip(predictions, ground_truth_is_ood)
        if not is_ood
    ]

    if not ood_scores or not id_scores:
        return 0.5  # No discrimination possible

    n_ood = len(ood_scores)
    n_id = len(id_scores)
    count = sum(
        1 for ood_s in ood_scores for id_s in id_scores if ood_s > id_s
    )
    count += 0.5 * sum(
        1 for ood_s in ood_scores for id_s in id_scores if ood_s == id_s
    )

    return count / (n_ood * n_id)
