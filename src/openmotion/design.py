"""Small reusable design primitives; use directly or replace for a project's art direction."""

from pathlib import Path
from functools import lru_cache

import manimpango
from manim import Text, RoundedRectangle, CubicBezier, RIGHT
import numpy as np


FONT_PATH = Path(__file__).parent / "assets/fonts/AtkinsonHyperlegible-Regular.ttf"
FONT_FAMILY = "Atkinson Hyperlegible"


@lru_cache(maxsize=1)
def register_font() -> str:
    if not manimpango.register_font(str(FONT_PATH)):
        raise RuntimeError(f"Cannot register bundled font: {FONT_PATH}")
    return FONT_FAMILY


def text(value: str, size=28, color="#F4F1E9", max_width=None):
    result = Text(value, font=register_font(), font_size=size, color=color)
    if max_width is not None and result.width > max_width:
        result.scale_to_fit_width(max_width)
    return result


def panel(width, height, stroke="#29384C", fill="#111E2E"):
    return RoundedRectangle(
        width=width, height=height, corner_radius=0.14,
        stroke_color=stroke, stroke_width=1, fill_color=fill, fill_opacity=1,
    )


def connector(start, end, color="#67E8C1", width=2):
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    offset = RIGHT * (end[0] - start[0]) * 0.48
    return CubicBezier(
        start, start + offset, end - offset, end,
        stroke_color=color, stroke_width=width, fill_opacity=0,
    )
