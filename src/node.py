from typing import List, Union


class Node:
    def __init__(self, parent: Union["Node", None]):
        self.parent = parent
        self.children: List["Node"] = []
