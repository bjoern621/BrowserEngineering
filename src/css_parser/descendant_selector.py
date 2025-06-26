from typing import Sequence
from .base_selector import BaseCSSSelector

from nodes.html_element import HTMLElement


class DescendantSelector(BaseCSSSelector):
    """
    Represents a descendant selector in a CSS selector chain.
    A descendant selector matches elements that are descendants of a specified element.
    For example, `div p { ... }` (ancestor is `div` and descendant is `p`) matches all `<p>` elements that are descendants of `<div>` elements.
    """

    def __init__(self, selectors: Sequence[BaseCSSSelector]):
        self.selectors = selectors
        self.priority = sum(s.priority for s in selectors)

    def matches(self, element: HTMLElement) -> bool:
        i = len(self.selectors) - 1
        node = element
        while i >= 0 and node:
            if self.selectors[i].matches(node):
                i -= 1
            node = node.parent
        return i < 0
