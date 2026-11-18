import random

from PIL import Image, ImageDraw

from .style import PAPER_LINED, PAPER_PLAIN, PAPER_SQUARED

PAGE_W, PAGE_H = 1240, 1754
MARGIN_TOP = 110
MARGIN_BOTTOM = 80
RED_MARGIN_X = 130
PLAIN_MARGIN_X = 100
TEXT_RIGHT = PAGE_W - 70

PAPER_BG = (252, 251, 247)
RULE_COLOR = (176, 190, 221)
MARGIN_LINE_COLOR = (196, 92, 92)
SQUARE_COLOR = (205, 216, 236)


def text_left_margin(paper_kind: str) -> int:
    if paper_kind == PAPER_PLAIN:
        return PLAIN_MARGIN_X
    return RED_MARGIN_X + 40


def _add_grain(img: Image.Image, alpha: float = 0.035) -> Image.Image:
    """Subtle per-pixel grain, blended toward random gray noise (no numpy needed)."""
    noise = Image.effect_noise(img.size, 40).convert("RGB")
    return Image.blend(img, noise, alpha)


def _add_vignette(img: Image.Image, strength: float = 0.12) -> Image.Image:
    """Darken the corners slightly, built from PIL's built-in radial gradient."""
    from PIL import ImageChops

    w, h = img.size
    grad = Image.radial_gradient("L").resize((w, h))  # 0 at center, ~255 at edges
    mask = grad.point(lambda g: max(0, 255 - int(strength * g)))
    mask_rgb = Image.merge("RGB", (mask, mask, mask))
    return ImageChops.multiply(img, mask_rgb)


def new_page(line_spacing: int, paper_kind: str = PAPER_LINED) -> Image.Image:
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_BG)
    draw = ImageDraw.Draw(img)

    if paper_kind == PAPER_SQUARED:
        step = line_spacing // 2
        for x in range(RED_MARGIN_X, TEXT_RIGHT, step):
            draw.line([(x, MARGIN_TOP - 20), (x, PAGE_H - MARGIN_BOTTOM)], fill=SQUARE_COLOR, width=1)
        for y in range(MARGIN_TOP, PAGE_H - MARGIN_BOTTOM, step):
            draw.line([(RED_MARGIN_X, y), (TEXT_RIGHT, y)], fill=SQUARE_COLOR, width=1)
        draw.line([(RED_MARGIN_X, 20), (RED_MARGIN_X, PAGE_H - 20)], fill=MARGIN_LINE_COLOR, width=2)
    elif paper_kind == PAPER_LINED:
        for y in range(MARGIN_TOP, PAGE_H - MARGIN_BOTTOM, line_spacing):
            draw.line([(40, y), (PAGE_W - 40, y)], fill=RULE_COLOR, width=1)
        draw.line([(RED_MARGIN_X, 20), (RED_MARGIN_X, PAGE_H - 20)], fill=MARGIN_LINE_COLOR, width=2)
    # PAPER_PLAIN: no rules, no margin line - just the blank sheet.

    img = _add_grain(img, alpha=0.035)
    img = _add_vignette(img, strength=0.12)
    return img


def finish_page(img: Image.Image, rng: random.Random) -> Image.Image:
    """Final photo-realism pass: tiny tilt + grain + soft blur."""
    from PIL import ImageFilter

    angle = rng.uniform(-0.5, 0.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=PAPER_BG)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    img = _add_grain(img, alpha=0.02)
    return img
