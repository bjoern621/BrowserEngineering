from tkinter.font import Font
from typing import List, Tuple, Literal

from common.constants import VSTEP
from common.font_cache import get_font
from draw_commands.DrawRect import DrawRect
from draw_commands.DrawText import DrawText
from draw_commands.DrawInstruction import DrawInstruction
from layout.layout_element import LayoutElement
from nodes.tag_element import TAGElement
from nodes.html_element import HTMLElement
from nodes.text import Text

BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]


class BlockLayout(LayoutElement):
    """A class to represent the layout of a block element in an HTML document. BlockLayout represents blocks of text like paragraphs, headings, etc., and are stacked vertically on the canvas."""

    def __init__(
        self,
        node: HTMLElement,
        width: float,
        parent: LayoutElement,
        previous_sibling: LayoutElement | None,
    ):
        super().__init__(node, parent, previous_sibling)

        self.display_list: list[tuple[float, float, str, Font]] = (
            []
        )  # A list of tuples containing (x, y, text, font) for painting
        self.width = width

    def paint(self) -> list[DrawInstruction]:
        cmds: list[DrawInstruction] = []

        if isinstance(self.node, TAGElement) and self.node.tag_name == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(word, x, y, font))

        return cmds

    def layout(self) -> None:
        assert self.parent is not None, "BlockLayout parent is None."

        self.x: float = self.parent.x
        self.width: float = self.parent.width
        if self.previous_sibling:
            self.y: float = self.previous_sibling.y + self.previous_sibling.height
        else:
            self.y: float = self.parent.y

        mode = self.layout_mode()

        if mode == "block":
            self.layout_intermediate()
        elif mode == "inline":
            self.cursor_x, self.cursor_y = 0, 0
            self.weight: Literal["normal", "bold"] = "normal"
            self.style: Literal["roman", "italic"] = "roman"
            self.size = 14
            self.underline = False

            self.line: List[Tuple[float, str, Font]] = []

            self.recursive(self.node)

            # Flush the last line
            self.flush()

            self.height: float = self.cursor_y
        else:
            raise ValueError(f"Unknown layout mode: {mode}")

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height: float = sum([child.height for child in self.children])

    def layout_intermediate(self):
        """
        Layout the block element as an intermediate block, which means it contains other block elements.
        """
        previous = None
        for child in self.node.children:
            next = BlockLayout(child, self.width, self, previous)
            self.children.append(next)
            previous = next

    def layout_mode(self):
        """
        Determine the layout mode of this block.
        Returns "inline" if this is a block layout laying out text inline (i.e., a text node potentially wrapping to multiple lines, <b>, <i>, etc.), or "block" if it is a block layout that contains other block elements (i.e. <p>, <h1>).

        """
        if isinstance(self.node, Text):
            return "inline"
        elif any(
            [
                isinstance(child, TAGElement) and child.tag_name in BLOCK_ELEMENTS
                for child in self.node.children
            ]
        ):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

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

    def recursive(self, node: HTMLElement):
        """Recursively processes the (root) node and its children for layout."""

        if isinstance(node, Text):
            for word in node.text.split():
                self.word(word)
        elif isinstance(node, TAGElement):
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
        max_width = self.width

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

        for rel_x, word, font in self.line:
            assert self.x is not None, "BlockLayout x coordinate is not set."
            assert self.y is not None, "BlockLayout y coordinate is not set."
            x: float = self.x + rel_x
            y: float = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = 0
        self.line = []
