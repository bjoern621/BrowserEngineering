from tkinter import Canvas


class DrawInstruction:
    """Base class for all draw commands. This class is used in the display list to execute drawing operations on a canvas."""

    def __init__(self):
        self.top: float
        self.bottom: float
        pass

    def execute(self, scroll: float, canvas: Canvas) -> None:
        """
        Execute the draw command. This method should be overridden by subclasses to perform the actual drawing.
        """
        raise NotImplementedError("Subclasses must implement this method.")
