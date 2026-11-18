from dataclasses import dataclass, field
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fonts"

INK_BLUE = (26, 58, 148)
INK_BLACK = (33, 33, 38)

PAPER_LINED = "lined"
PAPER_SQUARED = "squared"


@dataclass
class HandwritingStyle:
    """One student's 'handwriting' — font + paper + ink combination."""

    name: str
    font_path: Path
    font_size: int = 40
    heading_font_size: int = 50
    line_spacing: int = 52
    ink_color: tuple = INK_BLUE
    paper: str = PAPER_LINED
    jitter_rotation: float = 2.6
    jitter_baseline: float = 2.2
    jitter_spacing: float = 0.10


STYLES: dict[str, HandwritingStyle] = {
    "patrick": HandwritingStyle(
        name="Odatiy qalam",
        font_path=FONTS_DIR / "PatrickHand-Regular.ttf",
        font_size=40,
        heading_font_size=50,
        line_spacing=52,
        ink_color=INK_BLUE,
        paper=PAPER_LINED,
    ),
    "caveat": HandwritingStyle(
        name="Yozma qalam",
        font_path=FONTS_DIR / "Caveat-Regular.ttf",
        font_size=46,
        heading_font_size=58,
        line_spacing=50,
        ink_color=INK_BLUE,
        paper=PAPER_LINED,
    ),
    "patrick_squared": HandwritingStyle(
        name="Katakli daftar",
        font_path=FONTS_DIR / "PatrickHand-Regular.ttf",
        font_size=38,
        heading_font_size=48,
        line_spacing=50,
        ink_color=INK_BLUE,
        paper=PAPER_SQUARED,
    ),
}

DEFAULT_STYLE_KEY = "patrick"
