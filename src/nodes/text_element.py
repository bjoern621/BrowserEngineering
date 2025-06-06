from nodes.html_element import HTMLElement


class TextElement(HTMLElement):
    """
    A class to represent text content.
    It is used to handle the text content of a web page, that is "a run of characters outside a tag".
    """

    def __init__(self, text: str, parent: HTMLElement):
        super().__init__(parent)
        self.text = text

    def __repr__(self) -> str:
        return f'"{self.text.encode("unicode_escape").decode("utf-8")}"'
