from typing import List, Union


class HTMLElement:
    """
    A class representing an element in the DOM tree structure.
    """

    def __init__(self, parent: Union["HTMLElement", None]):
        self.parent = parent
        self.children: List["HTMLElement"] = []
        self.style: dict[str, str] = {}
