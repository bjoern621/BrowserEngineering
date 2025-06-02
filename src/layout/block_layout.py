from tkinter.font import Font
from typing import List, Tuple

from common.font_cache import get_font
from draw_commands.DrawRect import DrawRect
from draw_commands.DrawText import DrawText
from draw_commands.DrawInstruction import DrawInstruction
from layout.layout_element import LayoutElement
from nodes.tag_element import TAGElement
from nodes.html_element import HTMLElement
from nodes.text_element import TextElement

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

        self.display_list: list[tuple[float, float, str, Font, str]] = (
            []
        )  # A list of tuples containing (x, y, text, font, color) for painting
        self.width = width

    def paint(self) -> list[DrawInstruction]:
        cmds: list[DrawInstruction] = []

        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font, color in self.display_list:
                cmds.append(DrawText(word, x, y, font, color))

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

            self.line: List[Tuple[float, str, Font, str]] = (
                []
            )  # List of tuples (x, word, font, color)

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
            if isinstance(child, TAGElement) and child.tag_name == "head":
                continue

            next = BlockLayout(child, self.width, self, previous)
            self.children.append(next)
            previous = next

    def layout_mode(self):
        """
        Determine the layout mode of this block.
        Returns "inline" if this is a block layout laying out text inline (i.e., a text node potentially wrapping to multiple lines, <b>, <i>, etc.), or "block" if it is a block layout that contains other block elements (i.e. <p>, <h1>).
        """

        if isinstance(self.node, TextElement):
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

    def recursive(self, node: HTMLElement):
        """Recursively processes the (root) node and its children for layout."""

        if isinstance(node, TextElement):
            for word in node.text.split():
                self.word(word, node)
        elif isinstance(node, TAGElement):
            if node.tag_name == "br":
                self.flush()

            for child in node.children:
                self.recursive(child)

    def word(self, word: str, text_node: TextElement):
        """Add a word to the current line, wrapping to the next line if necessary."""

        weight = text_node.style["font-weight"]
        style = text_node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(
            float(text_node.style["font-size"][:-2]) * 0.75
        )  # Convert from px to Tk points

        color = text_node.style["color"]

        text_node_parent = text_node.parent
        assert text_node_parent is not None, "Text node parent is None."
        underline = text_node_parent.style.get("text-decoration") == "underline"

        assert weight in ["normal", "bold"], f"Invalid font weight: {weight}"
        assert style in ["roman", "italic"], f"Invalid font style: {style}"

        font = get_font(
            size=size,
            weight=weight,  # type: ignore
            slant=style,  # type: ignore
            underline=underline,
        )

        w = font.measure(word)

        screen_x_position_after_word = self.cursor_x + w
        max_width = self.width

        if screen_x_position_after_word > max_width:
            self.flush()

        self.line.append((self.cursor_x, word, font, color))
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

        metrics = [font.metrics() for _x, _word, font, _color in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])

        baseline = self.cursor_y + 1.25 * max_ascent

        for rel_x, word, font, color in self.line:
            assert self.x is not None, "BlockLayout x coordinate is not set."
            assert self.y is not None, "BlockLayout y coordinate is not set."
            x: float = self.x + rel_x
            y: float = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = 0
        self.line = []

    def __repr__(self) -> str:
        return f"BlockLayout[{self.layout_mode()}] ({self.node})"
