from tkinter.font import Font
from typing import List, Tuple, Literal

from constants import HSTEP, VSTEP
from font_cache import get_font
from element import Element
from node import Node
from text import Text

FONTS = {}


class Layout:
    """Layout text for display on the canvas. It creates a display list of tuples with x, y coordinates, the string to render and a Font. The coordinates are page coordinates."""

    def __init__(self, node: Node, width: int):
        self.display_list: List[Tuple[float, float, str, Font]] = []
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight: Literal["normal", "bold"] = "normal"
        self.style: Literal["roman", "italic"] = "roman"
        self.width = width
        self.size = 14
        self.underline = False

        self.line: List[Tuple[float, str, Font]] = []

        self.recursive(node)

        # Flush the last line
        self.flush()

    def open_tag(self, tag: str):
        """Process opening tags relevant for layout."""

        match tag:
            case "i":
                self.style = "italic"
            case "b":
                self.weight = "bold"
            case "small":
                self.size -= 2
            case "big":
                self.size += 4
            case "u":
                self.underline = True
            case "br":
                self.flush()
            case _:
                # Skip unknown tags for layout
                _ = None

    def close_tag(self, tag: str):
        """Process closing tags relevant for layout."""

        match tag:
            case "i":
                self.style = "roman"
            case "b":
                self.weight = "normal"
            case "small":
                self.size += 2
            case "big":
                self.size -= 4
            case "u":
                self.underline = False
            case "p":
                self.flush()
                self.cursor_y += VSTEP
            case _:
                # Skip unknown tags for layout
                _ = None

    def recursive(self, node: Node):
        """Recursively processes the (root) node and its children for layout."""

        if isinstance(node, Text):
            for word in node.text.split():
                self.word(word)
        elif isinstance(node, Element):
            self.open_tag(node.tag_name)
            for child in node.children:
                self.recursive(child)
            self.close_tag(node.tag_name)

    def word(self, word: str):
        """Add a word to the current line, wrapping to the next line if necessary."""

        font = get_font(
            size=self.size,
            weight=self.weight,
            slant=self.style,
            underline=self.underline,
        )

        w = font.measure(word)

        screen_x_position_after_word = self.cursor_x + w
        max_width = self.width - HSTEP

        if screen_x_position_after_word > max_width:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        """
        Flush the current line to the display list.
        This is called when a line is full or when a <br> tag is encountered.
        It calculates the baseline for the line and adjusts the y-coordinate for each word.
        It is the second part of the two-part layout process.
        """

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
