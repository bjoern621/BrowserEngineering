from tkinter import Canvas
from draw_commands.DrawInstruction import DrawInstruction


class DrawRect(DrawInstruction):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, color: str):
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2
        self.color = color

    def execute(self, scroll: float, canvas: Canvas) -> None:
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,  # Hides default one-pixel black border
            fill=self.color,
        )
