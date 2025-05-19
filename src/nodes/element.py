from nodes.node import Node


class Element(Node):
    """
    A class representing an HTML tag.
    A Tag object represents the contens of an HTML tag, which is a run of characters inside a tag.
    E.g. '!doctpye html', div, p, span, /span, ....
    """

    def __init__(self, tag_name: str, parent: Node | None, attributes: dict[str, str]):
        super().__init__(parent)
        self.tag_name = tag_name  # Only the tag name, not the full tag; e.g. 'div', 'p', etc., NEVER '/div', '/p', etc.
        self.attributes = attributes

    def __repr__(self) -> str:
        return f"<{self.tag_name}>"
