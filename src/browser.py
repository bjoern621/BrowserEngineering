import tkinter
import tkinter.font

from common.constants import VSTEP
from css_parser.base_selector import BaseCSSSelector
from draw_commands.DrawInstruction import DrawInstruction
from layout.document_layout import DocumentLayout
from layout.layout_element import LayoutElement, paint_tree
from nodes.html_element import HTMLElement
from nodes.tag_element import TAGElement
from css_parser.css_parser import CSSParser
from parser.parser import HTMLParser, print_tree
from common.url import URL

INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600
MIN_WIDTH = 400
MIN_HEIGHT = 250


SCROLL_STEP = 100

DEFAULT_STYLE_SHEET = CSSParser(open("src/browser.css").read()).parse_css_file()

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}  # Style properties that are inherited by default from parent elements. Text elements can only use these properties because they cannot be selected by CSS selectors otherwise.


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()

        bi_times = tkinter.font.Font(
            family="Times", size=16, weight="normal", slant="roman"
        )
        self.font = bi_times

        self.canvas = tkinter.Canvas(
            self.window, width=INITIAL_WIDTH, height=INITIAL_HEIGHT, bg="white"
        )
        self.window.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.canvas.pack(
            fill=tkinter.BOTH, expand=True
        )  # The pack() method is used to add the canvas widget to the window's layout.

        self.scroll = 0
        self.window.bind("<Up>", lambda e: self.scroll_up())
        self.window.bind("<Down>", lambda e: self.scroll_down())
        self.window.bind(
            "<MouseWheel>",
            lambda e: self.handle_mouse_wheel(e.delta),
        )
        self.window.bind("<Configure>", lambda e: self.handle_resize(e.width, e.height))

        self.width = INITIAL_WIDTH
        self.height = INITIAL_HEIGHT

        self.display_list: list[
            DrawInstruction
        ]  # A list of draw commands to be executed on the canvas in order.

    def load(self, url: URL):
        """Load the URL and display its content in the browser."""

        body = url.request()
        self.root_node = HTMLParser(body).parse()

        print_tree(self.root_node)

        self.apply_css_to_root_node(url)

        self.document = DocumentLayout(self.root_node, INITIAL_WIDTH)
        self.document.layout()

        print_tree(self.document)

        self.display_list: list[DrawInstruction] = []
        paint_tree(self.document, self.display_list)

        self.draw()

    def apply_css_to_root_node(self, base_url: URL):
        """Apply CSS styles to the root node of the HTML tree."""

        css_rules = DEFAULT_STYLE_SHEET.copy()

        links = [
            node.attributes["href"]
            for node in tree_to_list(self.root_node, [])
            if isinstance(node, TAGElement)
            and node.tag_name == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]  # Find all <link rel="stylesheet" href="..."> elements in the HTML tree.

        for link in links:
            style_sheet_url = base_url.resolve(link)
            try:
                body = style_sheet_url.request()
            except Exception as e:
                print(f"Failed to load stylesheet {link}: {e}")
                continue

            css_rules.extend(CSSParser(body).parse_css_file())

        style(self.root_node, sorted(css_rules, key=cascade_priority))

    def draw(self):
        """Draw the content of the display_list that is currently in view on the canvas."""

        self.canvas.delete("all")

        for cmd in self.display_list:
            # Skip draw commmands that are not in the current view
            if cmd.top > self.scroll + self.height:
                continue

            if cmd.bottom < self.scroll:
                continue

            cmd.execute(self.scroll, self.canvas)

    def scroll_up(self, scroll_step: int = SCROLL_STEP):
        self.scroll -= scroll_step
        self.scroll = max(self.scroll, 0)  # Prevent scrolling above the top
        self.draw()

    def scroll_down(self, scroll_step: int = SCROLL_STEP):
        self.scroll += scroll_step
        max_y = max(
            self.document.height + 2 * VSTEP - self.height,
            0,
            # self.display_list[-1].bottom - self.height, 0
        )  # Calculate maximum scrolling that still allows for viewing content
        self.scroll = min(self.scroll, max_y)
        self.draw()

    def handle_mouse_wheel(self, delta: int):
        """Handle mouse wheel scrolling. Supports Windows."""

        if delta > 0:
            self.scroll_up(delta)
        else:
            self.scroll_down(abs(delta))

    def handle_resize(self, width: int, height: int):
        """Handle window resize events. Re-layout and redraw the content."""

        if self.width == width and self.height == height:
            return  # No need to re-layout if the size hasn't changed e.g., when the windows is dragged.

        assert self.root_node is not None, "Root node is None."

        if self.width != width:
            # Re-layout the text if the width has changed
            self.document = DocumentLayout(self.root_node, width)
            self.document.layout()

            self.display_list: list[DrawInstruction] = []
            paint_tree(self.document, self.display_list)
            # self.display_list = BlockLayout(self.root_node, width).display_list

        self.width = width
        self.height = height

        self.draw()


def style(node: HTMLElement, rules: list[tuple[BaseCSSSelector, dict[str, str]]]):
    """Recursively set styles (`node.style: dict[str, str]`) on the HTML tree node and its children."""

    node.style = {}

    for prop, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[prop] = node.parent.style[prop]
        else:
            node.style[prop] = default_value

    # Apply CSS rules based on rules from a CSS file.
    # CSS rules may be the User Agent styles or styles from a fetched stylesheet (last take precedence).
    for selector, body in rules:
        if not selector.matches(node):
            continue
        for prop, value in body.items():
            node.style[prop] = value

    # If the node is a TAGElement and has a "style" attribute, parse it and set the styles.
    if isinstance(node, TAGElement) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()

        for prop, value in pairs.items():
            node.style[prop] = value

    # Resolve percentage font sizes to pixel values before inheriting.
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = f"{node_pct * parent_px}px"

    for child in node.children:
        style(child, rules)


def tree_to_list(
    tree: HTMLElement | LayoutElement, list: list[HTMLElement | LayoutElement]
) -> list[HTMLElement | LayoutElement]:
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


def cascade_priority(rule: tuple[BaseCSSSelector, dict[str, str]]) -> int:
    """Calculate the cascade priority of a CSS rule based on its selector."""

    selector, _ = rule
    return selector.priority
