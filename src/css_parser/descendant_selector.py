from .base_selector import BaseCSSSelector

from nodes.html_element import HTMLElement


class DescendantSelector(BaseCSSSelector):
    """
    Represents a descendant selector in a CSS selector chain.
    A descendant selector matches elements that are descendants of a specified element.
    For example, `div p { ... }` (ancestor is `div` and descendant is `p`) matches all <p> elements that are descendants of &lt;div&gt; elements.
    """

    def __init__(self, ancestor: BaseCSSSelector, descendant: BaseCSSSelector):
        self.ancestor: BaseCSSSelector = ancestor
        self.descendant: BaseCSSSelector = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, element: HTMLElement) -> bool:
        if not self.descendant.matches(element):
            return False

        while element.parent:
            if self.ancestor.matches(element.parent):
                return True
            element = element.parent

        return False
