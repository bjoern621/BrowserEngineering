from tkinter import Canvas
from tkinter.font import Font
from draw_commands.DrawInstruction import DrawInstruction


class DrawText(DrawInstruction):
    def __init__(self, text: str, x: float, y: float, font: Font):
        self.text = text
        self.left = x
        self.top = y
        self.font = font
        self.bottom = y + font.metrics("linespace")

    def execute(self, scroll: float, canvas: Canvas) -> None:
        canvas.create_text(
            self.left, self.top - scroll, text=self.text, font=self.font, anchor="nw"
        )
