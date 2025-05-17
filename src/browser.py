import tkinter
from typing import List, Tuple

from url import URL

WIDTH = 800
HEIGHT = 600

HSTEP, VSTEP = 13, 18

SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()  # The pack() method is used to add the canvas widget to the window's layout.

        self.scroll = 0
        self.window.bind("<Up>", lambda e: self.scroll_up())
        self.window.bind("<Down>", lambda e: self.scroll_down())
        self.window.bind(
            "<MouseWheel>",
            lambda e: self.handle_mouse_wheel(e.delta),
        )

    def load(self, url: URL):
        """Load the URL and display its content in the browser."""

        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()

    def draw(self):
        """Draw the content of the display_list that is currently in view on the canvas."""

        self.canvas.delete("all")

        for x, y, char in self.display_list:
            # Skip characters that are not in the current view
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=char)

    def scroll_up(self, scroll_step: int = SCROLL_STEP):
        self.scroll -= scroll_step
        self.scroll = max(self.scroll, 0)  # Prevent scrolling above the top
        self.draw()

    def scroll_down(self, scroll_step: int = SCROLL_STEP):
        self.scroll += scroll_step
        self.draw()

    def handle_mouse_wheel(self, delta: int):
        """Handle mouse wheel scrolling. Supports Windows."""

        if delta > 0:
            self.scroll_up(delta)
        else:
            self.scroll_down(abs(delta))


def layout(text: str):
    """Layout the text for display on the canvas. It returns a display list of tuples with x, y coordinates and the character. The coordinates are page coordinates."""

    display_list: List[Tuple[int, int, str]] = []

    cursor_x, cursor_y = HSTEP, VSTEP

    for char in text:
        display_list.append((cursor_x, cursor_y, char))
        cursor_x += HSTEP

        if cursor_x > WIDTH - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP

    return display_list


def lex(body: str) -> str:
    """Lexical analysis of the HTML body to extract text content."""

    text = ""

    in_tag = False
    for char in body:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            text += char

    return text
