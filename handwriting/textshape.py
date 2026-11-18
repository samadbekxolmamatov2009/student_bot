from dataclasses import dataclass
from PIL import ImageFont

HEADING = "heading"
BULLET = "bullet"
PARA = "para"


@dataclass
class Block:
    kind: str
    text: str


def parse_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    para_lines: list[str] = []

    def flush():
        if para_lines:
            blocks.append(Block(PARA, " ".join(para_lines)))
            para_lines.clear()

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("# "):
            flush()
            blocks.append(Block(HEADING, line[2:].strip()))
        elif line.startswith(("- ", "* ")):
            flush()
            blocks.append(Block(BULLET, line[2:].strip()))
        else:
            para_lines.append(line)
    flush()
    return blocks


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if font.getlength(candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
