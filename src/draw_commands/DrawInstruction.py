from tkinter import Canvas


class DrawInstruction:
    """Base class for all draw commands."""

    def __init__(self):
        self.top: float
        self.bottom: float
        pass

    def execute(self, scroll: float, canvas: Canvas) -> None:
        """
        Execute the draw command. This method should be overridden by subclasses to perform the actual drawing.
        """
        raise NotImplementedError("Subclasses must implement this method.")
