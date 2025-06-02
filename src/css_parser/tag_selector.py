from css_parser.base_selector import BaseCSSSelector
from nodes.html_element import HTMLElement
from nodes.tag_element import TAGElement


class TagSelector(BaseCSSSelector):
    """
    Represents a tag selector in a CSS stylesheet.
    A tag selector matches elements by their tag name.
    For example `div { ... }` matches all <div> elements in the document.
    """

    def __init__(self, tag_name: str):
        super().__init__()
        self.tag_name = tag_name
        self.priority = 1

    def matches(self, element: HTMLElement) -> bool:
        return isinstance(element, TAGElement) and element.tag_name == self.tag_name
