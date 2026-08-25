"""The one colour per standard, shared by every reader-facing surface.

This module is the single source of the four-standard palette. The interactive
GSN view consumes it now; the poster and the talk deck consume it rather than
defining their own. Decided by the authors on 2026-08-24.

Rationale, as recorded by the authors: the first three values darken the WAISE
paper's own Figure 2 tints (blue for the ISO/PAS 8800 base, orange for ISO
21448 at G7, red for ISO/SAE 21434 at G8) to daylight-contrast strength, so the
published figure and every generated view agree in hue. ISO 26262 gets green
because the paper leaves it uncoloured, and green is distinguishable from the
other three for the common forms of colour vision deficiency. Colour is never
the sole carrier: every swatch sits beside the standard's name.

Grey is reserved for undeveloped/gap nodes. There is no fifth accent colour.

Known defect, to be fixed in its own change: ``coverage_plots.py`` assigns blue
to ISO 26262, which conflicts with this palette and with the paper's Figure 2.
It must move to this module's values.
"""

from __future__ import annotations

STANDARD_COLORS: dict[str, str] = {
    "ISO26262": "#2E7D32",
    "ISO21448": "#E65100",
    "ISO21434": "#C62828",
    "ISOPAS8800": "#1565C0",
}

PLACEHOLDERS_PENDING = False

# Reserved for undeveloped/gap nodes (G9). Not a standard's colour.
# #757575 reaches 4.6:1 against white, where the previous #9E9E9E reached only
# 2.68:1 and fell below the 3:1 a meaningful interface element needs to stay
# legible in daylight. It matches the dashed borders already used for absences.
GAP_GREY = "#757575"

# Short display names, as used throughout the papers and this repository.
STANDARD_LABELS: dict[str, str] = {
    "ISO26262": "ISO 26262",
    "ISO21448": "ISO 21448",
    "ISO21434": "ISO/SAE 21434",
    "ISOPAS8800": "ISO/PAS 8800",
}
