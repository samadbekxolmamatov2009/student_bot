import random

from PIL import Image, ImageDraw, ImageFont

from . import paper
from .style import HandwritingStyle
from .textshape import BULLET, HEADING, PARA, parse_blocks, wrap_text

TEXT_LEFT = paper.RED_MARGIN_X + 40
PARA_INDENT = 60
BULLET_INDENT = 50
BULLET_CONT_INDENT = 78


def _jitter_color(base: tuple, rng: random.Random) -> tuple:
    factor = rng.uniform(0.85, 1.08)
    r, g, b = base
    return tuple(max(0, min(255, int(c * factor + rng.uniform(-8, 8)))) for c in (r, g, b))


class _GlyphWriter:
    def __init__(self, font: ImageFont.FreeTypeFont, style: HandwritingStyle, rng: random.Random):
        self.font = font
        self.style = style
        self.rng = rng
        ascent, descent = font.getmetrics()
        self.ascent = ascent
        self.descent = descent
        self.tile_w = int(font.size * 1.3) + 12
        self.tile_h = ascent + descent + 16
        self.local_x = 6
        self.local_y = 8

    def line_width(self, text: str) -> float:
        return self.font.getlength(text)

    def draw(self, canvas: Image.Image, x: float, y_baseline: float, text: str) -> float:
        rng = self.rng
        cursor_x = x
        y_ascender_top = y_baseline - self.ascent
        for ch in text:
            if ch == " ":
                cursor_x += self.font.getlength(" ") * rng.uniform(0.9, 1.25)
                continue
            tile = Image.new("RGBA", (self.tile_w, self.tile_h), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tile)
            color = _jitter_color(self.style.ink_color, rng)
            tdraw.text((self.local_x, self.local_y), ch, font=self.font, fill=color)
            if rng.random() < 0.07:
                tdraw.text((self.local_x + 1, self.local_y), ch, font=self.font, fill=color)
            angle = rng.uniform(-self.style.jitter_rotation, self.style.jitter_rotation)
            tile = tile.rotate(
                angle,
                resample=Image.BICUBIC,
                center=(self.local_x, self.local_y + self.ascent // 2),
            )
            dy = rng.uniform(-self.style.jitter_baseline, self.style.jitter_baseline)
            paste_x = int(round(cursor_x - self.local_x))
            paste_y = int(round(y_ascender_top - self.local_y + dy))
            canvas.alpha_composite(tile, (paste_x, paste_y))
            advance = self.font.getlength(ch) * (1 + rng.uniform(-self.style.jitter_spacing, self.style.jitter_spacing))
            cursor_x += advance
        return cursor_x

    def wavy_underline(self, canvas: Image.Image, x0: float, x1: float, y: float):
        rng = self.rng
        draw = ImageDraw.Draw(canvas)
        color = _jitter_color(self.style.ink_color, rng)
        step = 14
        x = x0
        prev_y = y + rng.uniform(-1, 1)
        points = [(x, prev_y)]
        while x < x1:
            x += step
            points.append((min(x, x1), y + rng.uniform(-1.5, 1.5)))
        draw.line(points, fill=color, width=2, joint="curve")


def _build_layout_lines(text: str, writer_normal: _GlyphWriter, writer_heading: _GlyphWriter, max_width: float):
    lines = []
    for block in parse_blocks(text):
        if block.kind == HEADING:
            wrapped = wrap_text(block.text, writer_heading.font, max_width)
            for i, line in enumerate(wrapped):
                lines.append({
                    "writer": writer_heading, "text": line, "indent": 0,
                    "gap_before": 30 if i == 0 else 4, "centered": True,
                    "underline": i == len(wrapped) - 1,
                    "pitch": writer_heading.font.size + 22,
                })
        elif block.kind == BULLET:
            wrapped = wrap_text(block.text, writer_normal.font, max_width - BULLET_INDENT)
            for i, line in enumerate(wrapped):
                prefix = "– " if i == 0 else ""
                lines.append({
                    "writer": writer_normal, "text": prefix + line,
                    "indent": BULLET_INDENT if i == 0 else BULLET_CONT_INDENT,
                    "gap_before": 10 if i == 0 else 0, "centered": False,
                    "underline": False, "pitch": writer_normal.style.line_spacing,
                })
        else:
            wrapped = wrap_text(block.text, writer_normal.font, max_width)
            for i, line in enumerate(wrapped):
                lines.append({
                    "writer": writer_normal, "text": line,
                    "indent": PARA_INDENT if i == 0 else 0,
                    "gap_before": 14 if i == 0 else 0, "centered": False,
                    "underline": False, "pitch": writer_normal.style.line_spacing,
                })
    return lines


def _paginate(lines: list[dict]) -> list[list[tuple]]:
    pages: list[list[tuple]] = []
    page: list[tuple] = []
    y = paper.MARGIN_TOP
    bottom_limit = paper.PAGE_H - paper.MARGIN_BOTTOM
    for line in lines:
        needed = line["gap_before"] + line["pitch"]
        if y + needed > bottom_limit and page:
            pages.append(page)
            page = []
            y = paper.MARGIN_TOP
        y += line["gap_before"]
        page.append((y, line))
        y += line["pitch"]
    if page:
        pages.append(page)
    return pages


def render_notes(text: str, style: HandwritingStyle, seed: int | None = None) -> list[Image.Image]:
    rng = random.Random(seed)
    font_normal = ImageFont.truetype(str(style.font_path), style.font_size)
    font_heading = ImageFont.truetype(str(style.font_path), style.heading_font_size)

    writer_normal = _GlyphWriter(font_normal, style, rng)
    writer_heading = _GlyphWriter(font_heading, style, rng)

    max_width = paper.TEXT_RIGHT - TEXT_LEFT
    layout_lines = _build_layout_lines(text, writer_normal, writer_heading, max_width)
    pages = _paginate(layout_lines)

    images = []
    for page_lines in pages:
        bg = paper.new_page(style.line_spacing, style.paper).convert("RGBA")
        for y_baseline, line in page_lines:
            writer: _GlyphWriter = line["writer"]
            text_line = line["text"]
            if line["centered"]:
                width = writer.line_width(text_line)
                x = TEXT_LEFT + max(0, (max_width - width) / 2)
            else:
                x = TEXT_LEFT + line["indent"]
            end_x = writer.draw(bg, x, y_baseline, text_line)
            if line["underline"]:
                writer.wavy_underline(bg, x, end_x, y_baseline + 8)
        final = bg.convert("RGB")
        final = paper.finish_page(final, rng)
        images.append(final)

    return images or [paper.new_page(style.line_spacing, style.paper)]
