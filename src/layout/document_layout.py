from common.constants import HSTEP, VSTEP
from draw_commands.DrawInstruction import DrawInstruction
from layout.block_layout import BlockLayout
from layout.layout_element import LayoutElement
from nodes.node import Node


class DocumentLayout(LayoutElement):
    """
    A class to represent the layout of a whole HTML document.
    """

    def __init__(self, root_node: Node, width: float):
        super().__init__(root_node, None, None)
        self.width = width

    def layout(self):
        """Create the child layout element and recursively call layout on it."""

        child = BlockLayout(self.node, 800, self, None)
        self.children.append(child)

        self.x = HSTEP
        self.y = VSTEP

        child.layout()

        self.height = child.height

    def paint(self) -> list[DrawInstruction]:
        return []
