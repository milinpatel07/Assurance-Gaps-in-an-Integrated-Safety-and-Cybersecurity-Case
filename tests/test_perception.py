"""Tests for the perception module (voxelization and deep ensemble)."""

import pytest
import numpy as np

from src.perception.voxelization import (
    VoxelConfig,
    KITTI_VOXEL_CONFIG,
    voxelize,
)
from src.perception.deep_ensemble import (
    EnsembleConfig,
    Detection3D,
    EnsemblePrediction,
    compute_box_iou_3d,
    compute_geometric_divergence,
    match_detections_across_members,
    aggregate_ensemble_predictions,
    compute_ensemble_auroc,
)


class TestVoxelization:
    """Test voxelization of LiDAR point clouds."""

    def test_grid_size_computation(self):
        config = KITTI_VOXEL_CONFIG
        grid = config.grid_size
        assert grid.shape == (3,)
        assert all(g > 0 for g in grid)

    def test_voxelize_empty_cloud(self):
        config = KITTI_VOXEL_CONFIG
        points = np.zeros((0, 4), dtype=np.float32)
        result = voxelize(points, config)
        assert result["voxels"].shape[0] == 0

    def test_voxelize_single_point(self):
        config = KITTI_VOXEL_CONFIG
        points = np.array([[10.0, 0.0, 0.0, 0.5]], dtype=np.float32)
        result = voxelize(points, config)
        assert result["voxels"].shape[0] == 1
        assert result["num_points"][0] == 1

    def test_voxelize_multiple_points(self):
        config = KITTI_VOXEL_CONFIG
        rng = np.random.RandomState(42)
        points = rng.uniform(
            low=[5, -10, -1, 0],
            high=[50, 10, 0.5, 1],
            size=(1000, 4),
        ).astype(np.float32)
        result = voxelize(points, config)
        assert result["voxels"].shape[0] > 0
        assert result["voxels"].shape[2] == 4
        assert np.all(result["num_points"] > 0)


class TestBoxIoU:
    """Test 3D bounding box IoU computation."""

    def test_identical_boxes(self):
        box = np.array([0, 0, 0, 2, 2, 2, 0], dtype=np.float32)
        assert compute_box_iou_3d(box, box) == pytest.approx(1.0)

    def test_no_overlap(self):
        box_a = np.array([0, 0, 0, 1, 1, 1, 0], dtype=np.float32)
        box_b = np.array([10, 10, 10, 1, 1, 1, 0], dtype=np.float32)
        assert compute_box_iou_3d(box_a, box_b) == pytest.approx(0.0)

    def test_partial_overlap(self):
        box_a = np.array([0, 0, 0, 2, 2, 2, 0], dtype=np.float32)
        box_b = np.array([1, 0, 0, 2, 2, 2, 0], dtype=np.float32)
        iou = compute_box_iou_3d(box_a, box_b)
        assert 0 < iou < 1


class TestGeometricDivergence:
    """Test the geometric divergence metric."""

    def test_single_box(self):
        boxes = [np.array([0, 0, 0, 2, 2, 2, 0])]
        assert compute_geometric_divergence(boxes) == 0.0

    def test_identical_boxes(self):
        box = np.array([0, 0, 0, 2, 2, 2, 0])
        boxes = [box, box, box]
        assert compute_geometric_divergence(boxes) == pytest.approx(0.0)

    def test_divergent_boxes(self):
        boxes = [
            np.array([0, 0, 0, 2, 2, 2, 0]),
            np.array([10, 10, 10, 2, 2, 2, 0]),
        ]
        div = compute_geometric_divergence(boxes)
        assert div == pytest.approx(1.0)  # No overlap

    def test_moderate_divergence(self):
        boxes = [
            np.array([0, 0, 0, 2, 2, 2, 0]),
            np.array([0.5, 0, 0, 2, 2, 2, 0]),
            np.array([0, 0.5, 0, 2, 2, 2, 0]),
        ]
        div = compute_geometric_divergence(boxes)
        assert 0 < div < 1


class TestEnsembleAggregation:
    """Test ensemble prediction aggregation."""

    def test_aggregate_matching_detections(self):
        config = EnsembleConfig(num_members=3)
        # Three members detect the same object at similar locations
        member_dets = [
            [Detection3D(box=np.array([10, 0, 0, 2, 4, 1.5, 0]), score=0.9, class_id=0)],
            [Detection3D(box=np.array([10.1, 0.1, 0, 2, 4, 1.5, 0]), score=0.85, class_id=0)],
            [Detection3D(box=np.array([9.9, -0.1, 0, 2, 4, 1.5, 0]), score=0.88, class_id=0)],
        ]
        preds = aggregate_ensemble_predictions(member_dets, config)
        assert len(preds) >= 1
        # The matched prediction should have low divergence
        assert preds[0].geometric_divergence < 0.3

    def test_uncertain_detection(self):
        config = EnsembleConfig(num_members=3, divergence_threshold=0.3)
        # Members strongly disagree
        member_dets = [
            [Detection3D(box=np.array([10, 0, 0, 2, 4, 1.5, 0]), score=0.9, class_id=0)],
            [Detection3D(box=np.array([20, 0, 0, 2, 4, 1.5, 0]), score=0.7, class_id=0)],
            [Detection3D(box=np.array([30, 0, 0, 2, 4, 1.5, 0]), score=0.6, class_id=0)],
        ]
        preds = aggregate_ensemble_predictions(member_dets, config)
        # At least one should be flagged as uncertain due to high divergence
        assert any(p.is_uncertain for p in preds) or len(preds) > 1


class TestAUROC:
    """Test AUROC computation for OOD detection."""

    def test_perfect_separation(self):
        preds = [
            EnsemblePrediction(
                mean_box=np.zeros(7), box_variance=np.zeros(7),
                mean_score=0.9, geometric_divergence=d,
                num_agreeing_members=5, class_id=0,
            )
            for d in [0.1, 0.2, 0.3, 0.8, 0.9, 1.0]
        ]
        labels = [False, False, False, True, True, True]
        auroc = compute_ensemble_auroc(preds, labels)
        assert auroc == pytest.approx(1.0)

    def test_random_predictions(self):
        rng = np.random.RandomState(42)
        preds = [
            EnsemblePrediction(
                mean_box=np.zeros(7), box_variance=np.zeros(7),
                mean_score=0.9, geometric_divergence=rng.uniform(0, 1),
                num_agreeing_members=5, class_id=0,
            )
            for _ in range(100)
        ]
        labels = [rng.random() > 0.5 for _ in range(100)]
        auroc = compute_ensemble_auroc(preds, labels)
        # Random should be around 0.5
        assert 0.3 < auroc < 0.7
