from nodes.html_element import HTMLElement


class BaseCSSSelector:
    """
    Base class for CSS selectors.
    This class is intended to be subclassed by specific selector types.
    """

    def __init__(self):
        self.priority: int

    def matches(self, element: HTMLElement) -> bool:
        """
        Check if the selector matches the given element.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
