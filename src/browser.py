import tkinter
import tkinter.font

from constants import VSTEP
from layout import Layout
from parser import HTMLParser
from url import URL

INITIAL_WIDTH = 800
INITIAL_HEIGHT = 600


SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()

        bi_times = tkinter.font.Font(
            family="Times", size=16, weight="normal", slant="roman"
        )
        self.font = bi_times

        self.canvas = tkinter.Canvas(
            self.window, width=INITIAL_WIDTH, height=INITIAL_HEIGHT
        )
        self.window.minsize(400, 250)
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

    def load(self, url: URL):
        """Load the URL and display its content in the browser."""

        body = url.request()
        self.root_node = HTMLParser(body).parse()
        self.display_list = Layout(self.root_node, INITIAL_WIDTH).display_list
        self.draw()

    def draw(self):
        """Draw the content of the display_list that is currently in view on the canvas."""

        self.canvas.delete("all")

        for x, y, char, font in self.display_list:
            # Skip characters that are not in the current view
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(
                x, y - self.scroll, text=char, anchor="nw", font=font
            )

    def scroll_up(self, scroll_step: int = SCROLL_STEP):
        self.scroll -= scroll_step
        self.scroll = max(self.scroll, 0)  # Prevent scrolling above the top
        self.draw()

    def scroll_down(self, scroll_step: int = SCROLL_STEP):
        self.scroll += scroll_step
        max_y = max(
            self.display_list[-1][1] if self.display_list else 0 - self.height, 0
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
            self.display_list = Layout(self.root_node, width).display_list

        self.width = width
        self.height = height

        self.draw()
