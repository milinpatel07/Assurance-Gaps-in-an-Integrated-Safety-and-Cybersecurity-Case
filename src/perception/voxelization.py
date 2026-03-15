"""Voxelization of LiDAR point clouds for the SECOND architecture.

Converts raw 3D point clouds into a voxel grid representation that serves
as input to the sparse convolutional backbone. This is the first stage of
the SECOND detection pipeline.

Reference: Yan et al., "SECOND: Sparsely Embedded Convolutional Detection",
Sensors 18(10), 3337 (2018).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class VoxelConfig:
    """Configuration for the voxelization process.

    Attributes:
        point_cloud_range: [x_min, y_min, z_min, x_max, y_max, z_max] in meters.
        voxel_size: [dx, dy, dz] voxel dimensions in meters.
        max_points_per_voxel: Maximum number of points retained per voxel.
        max_voxels: Maximum total number of non-empty voxels.
    """

    point_cloud_range: list[float]
    voxel_size: list[float]
    max_points_per_voxel: int = 35
    max_voxels: int = 20000

    @property
    def grid_size(self) -> np.ndarray:
        """Compute the voxel grid dimensions."""
        pc_range = np.array(self.point_cloud_range)
        vs = np.array(self.voxel_size)
        return np.round((pc_range[3:] - pc_range[:3]) / vs).astype(np.int64)


# Default config for KITTI-like LiDAR range
KITTI_VOXEL_CONFIG = VoxelConfig(
    point_cloud_range=[0, -39.68, -3, 69.12, 39.68, 1],
    voxel_size=[0.16, 0.16, 4],
    max_points_per_voxel=35,
    max_voxels=20000,
)


def voxelize(points: np.ndarray, config: VoxelConfig) -> dict:
    """Convert a point cloud to voxel representation.

    Args:
        points: (N, 4) array of [x, y, z, intensity] points.
        config: Voxelization configuration.

    Returns:
        Dictionary with:
        - 'voxels': (M, T, 4) array of voxel point features
        - 'coordinates': (M, 3) array of voxel grid coordinates
        - 'num_points': (M,) array of point counts per voxel
        where M <= max_voxels, T = max_points_per_voxel.
    """
    pc_range = np.array(config.point_cloud_range)
    voxel_size = np.array(config.voxel_size)
    grid_size = config.grid_size

    # Filter points within range
    mask = np.all(points[:, :3] >= pc_range[:3], axis=1) & np.all(
        points[:, :3] < pc_range[3:], axis=1
    )
    points = points[mask]

    # Compute voxel coordinates for each point
    coords = np.floor((points[:, :3] - pc_range[:3]) / voxel_size).astype(np.int64)

    # Clip to grid boundaries
    coords = np.clip(coords, 0, grid_size - 1)

    # Group points by voxel using a dictionary
    voxel_dict: dict[tuple, list[int]] = {}
    for i in range(len(coords)):
        key = (coords[i, 0], coords[i, 1], coords[i, 2])
        if key not in voxel_dict:
            voxel_dict[key] = []
        if len(voxel_dict[key]) < config.max_points_per_voxel:
            voxel_dict[key].append(i)

    # Limit total voxels
    voxel_keys = list(voxel_dict.keys())[: config.max_voxels]
    num_voxels = len(voxel_keys)

    # Build output arrays
    voxels = np.zeros(
        (num_voxels, config.max_points_per_voxel, points.shape[1]),
        dtype=np.float32,
    )
    coordinates = np.zeros((num_voxels, 3), dtype=np.int64)
    num_points_per_voxel = np.zeros(num_voxels, dtype=np.int64)

    for idx, key in enumerate(voxel_keys):
        point_indices = voxel_dict[key]
        n = len(point_indices)
        voxels[idx, :n] = points[point_indices]
        coordinates[idx] = key
        num_points_per_voxel[idx] = n

    return {
        "voxels": voxels,
        "coordinates": coordinates,
        "num_points": num_points_per_voxel,
    }
