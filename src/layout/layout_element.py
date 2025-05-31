from typing import Union

from draw_commands.DrawInstruction import DrawInstruction
from nodes.html_element import HTMLElement


class LayoutElement:
    """
    Base class for layout elements.
    """

    def __init__(
        self,
        node: HTMLElement,
        parent: Union["LayoutElement", None],
        previous_sibling: Union["LayoutElement", None],
    ):
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        self.children: list["LayoutElement"] = []

        self.x: float
        self.y: float
        self.width: float
        self.height: float

    def layout(self) -> None:
        """
        Layout this element. This method creates the child layout elements and recursively calls their layout method. It also sets the x, y, width, and height properties of this element.
        """

        raise NotImplementedError("Subclasses must implement this method.")

    def paint(self) -> list[DrawInstruction]:
        """
        Paint this element. This method should return a list of DrawInstructions / draw commands for painting.
        """

        raise NotImplementedError("Subclasses must implement this method.")


def paint_tree(
    layout_element: "LayoutElement",
    display_list: list[DrawInstruction],
) -> None:
    """
    Paint the layout tree to the display list.
    """

    display_list.extend(layout_element.paint())

    for child in layout_element.children:
        paint_tree(child, display_list)
