"""SECOND single-stage 3D object detector.

Implements the SECOND architecture (Yan et al., 2018) for voxel-based
LiDAR 3D object detection. The architecture consists of:
1. Voxel Feature Encoder (VFE): mean pooling of point features per voxel
2. Sparse Convolutional Middle Extractor: 3D sparse convolutions
3. Region Proposal Network (RPN): 2D convolutional detection head

For the case study, the entire detection pipeline from point cloud input
to 3D bounding box output is learned (Section 3.1).

Reference: Yan et al., "SECOND: Sparsely Embedded Convolutional Detection",
Sensors 18(10), 3337 (2018).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class DetectionConfig:
    """Configuration for the SECOND detector."""

    num_classes: int = 3  # Car, Pedestrian, Cyclist
    voxel_size: list[float] = field(default_factory=lambda: [0.16, 0.16, 4.0])
    point_cloud_range: list[float] = field(
        default_factory=lambda: [0, -39.68, -3, 69.12, 39.68, 1]
    )
    max_points_per_voxel: int = 35
    max_voxels: int = 20000
    vfe_out_channels: int = 64
    middle_channels: list[int] = field(default_factory=lambda: [64, 64, 128])
    rpn_in_channels: int = 256
    rpn_out_channels: int = 256
    num_anchor_per_loc: int = 2  # 0 and 90 degree rotations
    box_code_size: int = 7  # x, y, z, w, l, h, theta


@dataclass
class Detection3D:
    """A single 3D bounding box detection.

    Attributes:
        box: [x, y, z, w, l, h, theta] — center, dimensions, rotation.
        score: Detection confidence score.
        class_id: Predicted class index.
        class_name: Predicted class name.
    """

    box: np.ndarray  # (7,)
    score: float
    class_id: int
    class_name: str = ""


if TORCH_AVAILABLE:

    class VoxelFeatureEncoder(nn.Module):
        """Simple mean VFE: averages point features per voxel.

        Input: (M, T, C) voxel features, (M,) point counts
        Output: (M, C) voxel-level features
        """

        def __init__(self, in_channels: int = 4, out_channels: int = 64):
            super().__init__()
            self.linear = nn.Linear(in_channels, out_channels, bias=False)
            self.norm = nn.BatchNorm1d(out_channels)

        def forward(
            self, voxels: torch.Tensor, num_points: torch.Tensor
        ) -> torch.Tensor:
            # Mean pooling over points in each voxel
            points_mean = voxels.sum(dim=1) / num_points.unsqueeze(-1).float().clamp(min=1)
            x = self.linear(points_mean)
            x = self.norm(x)
            x = torch.relu(x)
            return x

    class SimplifiedMiddleExtractor(nn.Module):
        """Simplified 2D convolutional middle extractor.

        Replaces the sparse 3D convolutions of the original SECOND with
        2D convolutions on the BEV (bird's eye view) projection. This
        avoids the spconv dependency while preserving the architecture.
        """

        def __init__(
            self,
            in_channels: int = 64,
            grid_x: int = 432,
            grid_y: int = 496,
        ):
            super().__init__()
            self.grid_x = grid_x
            self.grid_y = grid_y
            self.in_channels = in_channels

            self.conv_layers = nn.Sequential(
                nn.Conv2d(in_channels, 64, 3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 128, 3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.Conv2d(128, 256, 3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(256),
                nn.ReLU(inplace=True),
            )

        def forward(
            self,
            voxel_features: torch.Tensor,
            coordinates: torch.Tensor,
            batch_size: int = 1,
        ) -> torch.Tensor:
            # Scatter voxel features onto BEV grid
            bev = torch.zeros(
                batch_size,
                self.in_channels,
                self.grid_y,
                self.grid_x,
                device=voxel_features.device,
                dtype=voxel_features.dtype,
            )

            # Use coordinates to scatter
            coords = coordinates.long()
            batch_idx = torch.zeros(len(coords), dtype=torch.long, device=coords.device)
            x_idx = coords[:, 0].clamp(0, self.grid_x - 1)
            y_idx = coords[:, 1].clamp(0, self.grid_y - 1)

            bev[batch_idx, :, y_idx, x_idx] = voxel_features

            return self.conv_layers(bev)

    class RPNHead(nn.Module):
        """Region Proposal Network head for 3D detection.

        Predicts class scores, bounding box regression, and direction
        for each anchor location on the BEV feature map.
        """

        def __init__(
            self,
            in_channels: int = 256,
            num_classes: int = 3,
            num_anchor_per_loc: int = 2,
            box_code_size: int = 7,
        ):
            super().__init__()

            self.conv_cls = nn.Conv2d(
                in_channels, num_anchor_per_loc * num_classes, 1
            )
            self.conv_box = nn.Conv2d(
                in_channels, num_anchor_per_loc * box_code_size, 1
            )
            self.conv_dir = nn.Conv2d(in_channels, num_anchor_per_loc * 2, 1)

        def forward(
            self, x: torch.Tensor
        ) -> dict[str, torch.Tensor]:
            cls_preds = self.conv_cls(x)
            box_preds = self.conv_box(x)
            dir_preds = self.conv_dir(x)
            return {
                "cls_preds": cls_preds,
                "box_preds": box_preds,
                "dir_preds": dir_preds,
            }

    class SECONDDetector(nn.Module):
        """SECOND voxel-based single-stage 3D object detector.

        Complete detection pipeline from voxel features to 3D bounding boxes.
        """

        def __init__(self, config: Optional[DetectionConfig] = None):
            super().__init__()
            self.config = config or DetectionConfig()

            grid_size = np.round(
                (
                    np.array(self.config.point_cloud_range[3:])
                    - np.array(self.config.point_cloud_range[:3])
                )
                / np.array(self.config.voxel_size)
            ).astype(int)

            self.vfe = VoxelFeatureEncoder(
                in_channels=4, out_channels=self.config.vfe_out_channels
            )
            self.middle = SimplifiedMiddleExtractor(
                in_channels=self.config.vfe_out_channels,
                grid_x=int(grid_size[0]),
                grid_y=int(grid_size[1]),
            )
            self.rpn = RPNHead(
                in_channels=self.config.rpn_in_channels,
                num_classes=self.config.num_classes,
                num_anchor_per_loc=self.config.num_anchor_per_loc,
                box_code_size=self.config.box_code_size,
            )

        def forward(
            self,
            voxels: torch.Tensor,
            coordinates: torch.Tensor,
            num_points: torch.Tensor,
        ) -> dict[str, torch.Tensor]:
            """Forward pass through the full detection pipeline.

            Args:
                voxels: (M, T, 4) voxel point features.
                coordinates: (M, 3) voxel grid coordinates.
                num_points: (M,) point counts per voxel.

            Returns:
                Dictionary with 'cls_preds', 'box_preds', 'dir_preds'.
            """
            voxel_features = self.vfe(voxels, num_points)
            bev_features = self.middle(voxel_features, coordinates)
            predictions = self.rpn(bev_features)
            return predictions

else:
    # Stub classes when PyTorch is not available
    class SECONDDetector:  # type: ignore[no-redef]
        """Stub: PyTorch not available."""

        def __init__(self, config=None):
            raise ImportError(
                "PyTorch is required for SECONDDetector. "
                "Install with: pip install torch"
            )
