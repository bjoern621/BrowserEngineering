from tkinter import Canvas
from tkinter.font import Font
from draw_commands.DrawInstruction import DrawInstruction


class DrawText(DrawInstruction):
    """Draws text on the canvas at a specified position with a given font."""

    def __init__(self, text: str, x: float, y: float, font: Font, color: str):
        self.text = text
        self.left = x
        self.top = y
        self.font = font
        self.bottom = y + font.metrics("linespace")
        self.color = color

    def execute(self, scroll: float, canvas: Canvas) -> None:
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            font=self.font,
            anchor="nw",
            fill=self.color,
        )
