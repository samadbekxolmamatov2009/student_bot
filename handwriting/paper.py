import numpy as np
from PIL import Image, ImageDraw

from .style import PAPER_LINED, PAPER_SQUARED

PAGE_W, PAGE_H = 1240, 1754
MARGIN_TOP = 110
MARGIN_BOTTOM = 80
RED_MARGIN_X = 130
TEXT_RIGHT = PAGE_W - 70

PAPER_BG = (250, 247, 238)
RULE_COLOR = (176, 190, 221)
MARGIN_LINE_COLOR = (196, 92, 92)
SQUARE_COLOR = (205, 216, 236)


def _add_grain(img: Image.Image, strength: int = 6) -> Image.Image:
    arr = np.asarray(img).astype(np.int16)
    noise = np.random.randint(-strength, strength + 1, arr.shape[:2])
    arr[..., 0] += noise
    arr[..., 1] += noise
    arr[..., 2] += noise
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _add_vignette(img: Image.Image, strength: float = 0.18) -> Image.Image:
    w, h = img.size
    y, x = np.ogrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((x - cx) / (w / 2)) ** 2 + ((y - cy) / (h / 2)) ** 2)
    mask = np.clip(1 - strength * np.clip(dist - 0.55, 0, None), 0, 1)
    arr = np.asarray(img).astype(np.float32)
    arr *= mask[..., None]
    return Image.fromarray(arr.astype(np.uint8))


def new_page(line_spacing: int, paper_kind: str = PAPER_LINED) -> Image.Image:
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_BG)
    draw = ImageDraw.Draw(img)

    if paper_kind == PAPER_SQUARED:
        step = line_spacing // 2
        for x in range(RED_MARGIN_X, TEXT_RIGHT, step):
            draw.line([(x, MARGIN_TOP - 20), (x, PAGE_H - MARGIN_BOTTOM)], fill=SQUARE_COLOR, width=1)
        for y in range(MARGIN_TOP, PAGE_H - MARGIN_BOTTOM, step):
            draw.line([(RED_MARGIN_X, y), (TEXT_RIGHT, y)], fill=SQUARE_COLOR, width=1)
    else:
        for y in range(MARGIN_TOP, PAGE_H - MARGIN_BOTTOM, line_spacing):
            draw.line([(40, y), (PAGE_W - 40, y)], fill=RULE_COLOR, width=1)

    draw.line([(RED_MARGIN_X, 20), (RED_MARGIN_X, PAGE_H - 20)], fill=MARGIN_LINE_COLOR, width=2)

    img = _add_grain(img, strength=5)
    img = _add_vignette(img, strength=0.12)
    return img


def finish_page(img: Image.Image, rng) -> Image.Image:
    """Final photo-realism pass: tiny tilt + grain + soft blur."""
    from PIL import ImageFilter

    angle = rng.uniform(-0.5, 0.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=PAPER_BG)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    img = _add_grain(img, strength=3)
    return img
