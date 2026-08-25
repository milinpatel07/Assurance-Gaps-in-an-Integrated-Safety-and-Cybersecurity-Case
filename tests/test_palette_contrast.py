"""The palette has to survive a phone screen in daylight.

Every colour in ``standard_colors.py`` reaches a reader outdoors, at arm's
length, on a screen fighting the sun. These tests hold the palette to the
WCAG 2.1 contrast minimum for a meaningful interface element, 3:1 against the
background it sits on, and check that the four standard colours stay
distinguishable from one another.

Colour is never the only carrier in these pages: every swatch sits beside the
name of its standard. The ratios matter anyway, because a reader who cannot see
the difference loses the grouping the colours provide.
"""

from __future__ import annotations

import itertools
import math

import pytest

from src.visualization.standard_colors import (
    GAP_GREY,
    STANDARD_COLORS,
    STANDARD_LABELS,
)

WHITE = "#FFFFFF"
PANEL_GREY = "#F5F5F5"

# WCAG 2.1, 1.4.11: interface components and graphical objects need 3:1.
UI_MINIMUM = 3.0


def _relative_luminance(hex_colour: str) -> float:
    raw = hex_colour.lstrip("#")
    channels = [int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    ]
    red, green, blue = linear
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: str, second: str) -> float:
    high = max(_relative_luminance(first), _relative_luminance(second))
    low = min(_relative_luminance(first), _relative_luminance(second))
    return (high + 0.05) / (low + 0.05)


def _to_lab(hex_colour: str) -> tuple[float, float, float]:
    """CIE L*a*b* under D65, for perceptual distance."""
    raw = hex_colour.lstrip("#")
    channels = [int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    ]
    red, green, blue = linear
    x = (red * 0.4124 + green * 0.3576 + blue * 0.1805) / 0.95047
    y = red * 0.2126 + green * 0.7152 + blue * 0.0722
    z = (red * 0.0193 + green * 0.1192 + blue * 0.9505) / 1.08883

    def pivot(value: float) -> float:
        return value ** (1 / 3) if value > 0.008856 else 7.787 * value + 16 / 116

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def perceptual_distance(first: str, second: str) -> float:
    """CIE76 delta E. Two colours above about 20 are clearly different.

    Contrast ratio cannot answer this question: it compares luminance alone, so
    the red and the blue in this palette score 1.02 against each other while
    being obvious to any reader. Distinguishing categorical colours is a
    question about hue, which needs a perceptual space.
    """
    return math.sqrt(
        sum((a - b) ** 2 for a, b in zip(_to_lab(first), _to_lab(second)))
    )


class TestContrastAgainstBackground:
    @pytest.mark.parametrize("standard", sorted(STANDARD_COLORS))
    def test_each_standard_colour_is_visible_on_white(self, standard):
        ratio = contrast_ratio(STANDARD_COLORS[standard], WHITE)
        assert ratio >= UI_MINIMUM, (
            f"{standard} ({STANDARD_COLORS[standard]}) reaches only "
            f"{ratio:.2f}:1 on white, below the {UI_MINIMUM}:1 an interface "
            "element needs to stay legible in daylight."
        )

    def test_the_gap_grey_is_visible_on_both_backgrounds(self):
        """It marks an absence, so a reader has to see that it is there."""
        for background, name in ((WHITE, "white"), (PANEL_GREY, "panel grey")):
            ratio = contrast_ratio(GAP_GREY, background)
            assert ratio >= UI_MINIMUM, (
                f"the gap grey {GAP_GREY} reaches only {ratio:.2f}:1 on "
                f"{name}."
            )


class TestColoursStayDistinguishable:
    @pytest.mark.parametrize(
        "first,second", list(itertools.combinations(sorted(STANDARD_COLORS), 2))
    )
    def test_no_two_standard_colours_are_near_neighbours(self, first, second):
        """Adjacent chips must not read as one another."""
        distance = perceptual_distance(
            STANDARD_COLORS[first], STANDARD_COLORS[second]
        )
        assert distance > 20.0, (
            f"{first} and {second} are too close to tell apart: delta E "
            f"{distance:.1f} between {STANDARD_COLORS[first]} and "
            f"{STANDARD_COLORS[second]}."
        )

    def test_the_gap_grey_is_distinct_from_every_standard(self):
        for standard, colour in sorted(STANDARD_COLORS.items()):
            distance = perceptual_distance(colour, GAP_GREY)
            assert distance > 20.0, (
                f"the gap grey is too close to {standard}: delta E "
                f"{distance:.1f}."
            )

    def test_no_standard_uses_the_gap_grey(self):
        """Grey means undeveloped. A standard wearing it would say the wrong
        thing."""
        assert GAP_GREY not in STANDARD_COLORS.values()

    def test_every_colour_has_a_label_to_sit_beside(self):
        """Colour is never the sole carrier of meaning."""
        assert set(STANDARD_COLORS) == set(STANDARD_LABELS)
