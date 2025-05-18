from tkinter.font import Font
from typing import List, Tuple, Literal

from constants import HSTEP, VSTEP
from font_cache import get_font
from tag import Tag
from text import Text

FONTS = {}


class Layout:
    """Layout text for display on the canvas. It creates a display list of tuples with x, y coordinates, the string to render and a Font. The coordinates are page coordinates."""

    def __init__(self, tokens: List[Text | Tag], width: int):
        self.display_list: List[Tuple[float, float, str, Font]] = []
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight: Literal["normal", "bold"] = "normal"
        self.style: Literal["roman", "italic"] = "roman"
        self.width = width
        self.size = 14
        self.underline = False

        self.line: List[Tuple[float, str, Font]] = []

        for tok in tokens:
            self.token(tok)

        # Flush the last line
        self.flush()

    def token(self, tok: Text | Tag):
        if isinstance(tok, Tag):
            match tok.tag_name:
                case "i":
                    self.style = "italic"
                case "/i":
                    self.style = "roman"
                case "b":
                    self.weight = "bold"
                case "/b":
                    self.weight = "normal"
                case "small":
                    self.size -= 2
                case "/small":
                    self.size += 2
                case "big":
                    self.size += 4
                case "/big":
                    self.size -= 4
                case "u":
                    self.underline = True
                case "/u":
                    self.underline = False
                case "br":
                    self.flush()
                case "br /":
                    self.flush()
                case "/p":
                    self.flush()
                    self.cursor_y += VSTEP
                case _:
                    # Skip unknown tags for layout
                    _ = None
        elif isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

    def word(self, word: str):
        font = get_font(
            size=self.size,
            weight=self.weight,
            slant=self.style,
            underline=self.underline,
        )

        w = font.measure(word)

        if self.cursor_x + w > self.width - HSTEP:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for _x, _word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])

        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []
