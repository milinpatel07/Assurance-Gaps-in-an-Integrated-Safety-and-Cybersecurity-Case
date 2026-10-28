"""SOTIF triggering conditions: the weather grid of the case study.

The WAISE paper's case study (Section 3.1) names rain, fog and reduced
visibility as SOTIF-relevant triggering conditions. This module defines a grid
over them: rain (0 to 100 mm/h) and fog (visibility 10 to 500 m) at controlled
levels, the input to ISO 21448 Cl.9-11 triggering-condition coverage. The
levels, their names and the triggering thresholds are choices of this
repository, documented in data/case_study_parameters/weather_grid.yaml.

The weather parameters are defined independently so they can be varied in a
controlled grid. Each condition also carries the CARLA weather parameters it
would map to; nothing in this repository connects to CARLA.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass
class WeatherCondition:
    """A single weather configuration of the grid.

    Attributes:
        name: Human-readable name (e.g., "heavy_rain_dense_fog"), built from the
            level names in weather_grid.yaml.
        rain_intensity: Rain intensity in mm/h (0 = no rain, 100 = extreme).
        fog_density: Fog density as visibility in metres (500 = clear,
            10 = very dense).
        sun_altitude: Sun altitude angle in degrees (-90 to 90).
        wetness: Road wetness (0 to 1).
        carla_cloudiness: CARLA cloudiness parameter (0 to 100).
        carla_precipitation: CARLA precipitation parameter (0 to 100).
        carla_fog_density: CARLA fog density parameter (0 to 100).
        carla_fog_distance: CARLA fog start distance in metres.
        sotif_triggering: Whether this condition is a SOTIF triggering condition.
        sotif_description: Description of the SOTIF relevance.
    """

    name: str
    rain_intensity: float  # mm/h
    fog_density: float  # visibility in metres
    sun_altitude: float = 45.0
    wetness: float = 0.0
    carla_cloudiness: float = 0.0
    carla_precipitation: float = 0.0
    carla_fog_density: float = 0.0
    carla_fog_distance: float = 500.0
    sotif_triggering: bool = False
    sotif_description: str = ""

    @classmethod
    def from_parameters(
        cls,
        rain_mm_h: float,
        visibility_m: float,
        sun_altitude: float = 45.0,
    ) -> "WeatherCondition":
        """Create a weather condition from physical parameters.

        Maps physical parameters (rain in mm/h, visibility in m) to the
        CARLA weather parameters they would correspond to.
        """
        # Map rain intensity to CARLA parameters
        carla_precip = min(100.0, rain_mm_h)
        wetness = min(1.0, rain_mm_h / 50.0)
        cloudiness = min(100.0, rain_mm_h * 2)

        # Map visibility to CARLA fog parameters
        # CARLA fog_density: 0 = clear, 100 = dense
        if visibility_m >= 500:
            carla_fog = 0.0
        else:
            carla_fog = max(0.0, min(100.0, (500.0 - visibility_m) / 5.0))

        # Determine SOTIF triggering condition
        is_triggering = rain_mm_h > 20 or visibility_m < 200

        # Build the name from the level names in weather_grid.yaml:
        # rain 0 none, 10 light, 25 moderate, 50 heavy, 100 extreme;
        # visibility 500 clear, 200 light, 100 moderate, 50 dense, 10 very dense.
        # Values between grid levels fall into the nearer named band.
        rain_level = (
            "no_rain" if rain_mm_h == 0
            else "light_rain" if rain_mm_h <= 20
            else "moderate_rain" if rain_mm_h <= 40
            else "heavy_rain" if rain_mm_h <= 75
            else "extreme_rain"
        )
        fog_level = (
            "clear" if visibility_m >= 500
            else "light_fog" if visibility_m >= 200
            else "moderate_fog" if visibility_m >= 100
            else "dense_fog" if visibility_m >= 30
            else "very_dense_fog"
        )
        name = f"{rain_level}_{fog_level}"

        sotif_desc = ""
        if is_triggering:
            reasons = []
            if rain_mm_h > 20:
                reasons.append(
                    f"rain ({rain_mm_h} mm/h) reduces LiDAR point density "
                    "through absorption and scattering"
                )
            if visibility_m < 200:
                reasons.append(
                    f"fog (visibility {visibility_m}m) causes spurious "
                    "reflections and reduced range"
                )
            sotif_desc = "; ".join(reasons)

        return cls(
            name=name,
            rain_intensity=rain_mm_h,
            fog_density=visibility_m,
            sun_altitude=sun_altitude,
            wetness=wetness,
            carla_cloudiness=cloudiness,
            carla_precipitation=carla_precip,
            carla_fog_density=carla_fog,
            carla_fog_distance=visibility_m,
            sotif_triggering=is_triggering,
            sotif_description=sotif_desc,
        )


# ── Standard weather grid for evaluation ─────────────────────────────

# Rain intensities (mm/h): 5 levels
RAIN_LEVELS = [0, 10, 25, 50, 100]

# Visibility (metres): 5 levels
VISIBILITY_LEVELS = [500, 200, 100, 50, 10]

# Sun altitudes for additional variation
SUN_ALTITUDES = [45.0, 15.0, -5.0]  # Day, dusk, night


def generate_weather_grid(
    rain_levels: list[float] | None = None,
    visibility_levels: list[float] | None = None,
    sun_altitudes: list[float] | None = None,
) -> list[WeatherCondition]:
    """Generate the parametric weather grid.

    Default: 5 rain levels x 5 fog levels = 25 combinations. With sun altitude
    variation: 5 x 5 x 3 = 75 conditions.

    Args:
        rain_levels: Rain intensities in mm/h. Default: [0, 10, 25, 50, 100].
        visibility_levels: Visibility distances in m. Default: [500, 200, 100, 50, 10].
        sun_altitudes: Sun altitude angles. Default: [45.0] (daytime only).

    Returns:
        List of WeatherCondition instances covering the grid.
    """
    rain_levels = rain_levels or RAIN_LEVELS
    visibility_levels = visibility_levels or VISIBILITY_LEVELS
    sun_altitudes = sun_altitudes or [45.0]

    conditions = []
    for rain, vis, sun in product(rain_levels, visibility_levels, sun_altitudes):
        cond = WeatherCondition.from_parameters(rain, vis, sun)
        conditions.append(cond)

    return conditions


def get_triggering_conditions(
    conditions: list[WeatherCondition],
) -> list[WeatherCondition]:
    """Filter for SOTIF triggering conditions (ISO 21448 Cl.7)."""
    return [c for c in conditions if c.sotif_triggering]


def compute_triggering_coverage(
    conditions: list[WeatherCondition],
) -> dict:
    """Compute triggering condition coverage statistics.

    This is part of the scenario-based testing evidence at G5
    (ISO 21448 Cl.9-11).
    """
    total = len(conditions)
    triggering = [c for c in conditions if c.sotif_triggering]
    non_triggering = [c for c in conditions if not c.sotif_triggering]

    rain_triggering = set()
    fog_triggering = set()
    for c in triggering:
        if c.rain_intensity > 20:
            rain_triggering.add(c.rain_intensity)
        if c.fog_density < 200:
            fog_triggering.add(c.fog_density)

    return {
        "total_conditions": total,
        "triggering_conditions": len(triggering),
        "non_triggering_conditions": len(non_triggering),
        "triggering_fraction": len(triggering) / total if total > 0 else 0,
        "rain_triggering_levels": sorted(rain_triggering),
        "fog_triggering_levels": sorted(fog_triggering),
    }
