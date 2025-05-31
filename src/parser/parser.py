from typing import List
from nodes.tag_element import TAGElement
from nodes.html_element import HTMLElement
from nodes.text import Text

SELF_CLOSING_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]


class HTMLParser:
    HEAD_TAGS = [
        "base",
        "basefont",
        "bgsound",
        "noscript",
        "link",
        "meta",
        "title",
        "style",
        "script",
    ]  # HEAD_TAGS lists the tags that you’re supposed to put into the <head> element

    def __init__(self, html: str):
        self.html = html
        self.unfinished: List[TAGElement] = []

    def parse(self) -> HTMLElement:
        """Lexical and structural analysis of the HTML body. Returns the root HTML Node (most often <html>) which represents the DOM tree root."""

        buffer = ""
        in_tag = False

        for char in self.html:
            if char == "<":
                in_tag = True
                if buffer:
                    self.add_text(
                        buffer
                    )  # Stores the text content that was before the open tag
                buffer = ""
            elif char == ">":
                in_tag = False
                self.add_tag(buffer)
                buffer = ""
            else:
                buffer += char

        if not in_tag and buffer:
            self.add_text(buffer)

        return self.finish()

    def add_text(self, text: str):
        """
        This method creates a Text node with the given text content and adds it as a child of the
        current unfinished (parent) element.
        """

        if text.isspace():
            return  # Ignore whitespace-only text (not standard browser behavior)

        self.implicit_tags(None)

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag: str):
        """
        Process and add a tag (e.g., `"div"`, `"head"`, `"img src="img_girl.jpg" alt="Girl in a jacket""`, ...) to the DOM tree.
        This method handles different types of tags:
        - Ignores comment tags (starting with `!`)
        - Processes closing tags (starting with `/`)
        - Handles self-closing tags (like `<img>`, `<br>`, etc.)
        - Processes opening tags

        For opening tags, a new Element is created and added to the unfinished list.

        For closing tags, the corresponding opening Element is popped from the unfinished list
        and added to its parent's children.

        For self-closing tags, a new Element is created and directly added to the
        parent's children without being added to the unfinished list.
        """

        tag_name, attributes = self.get_attributes(tag)

        if tag_name.startswith("!"):
            return  # Ignore <!DOCTYPE html> and other comments like <!-- comment -->

        self.implicit_tags(tag_name)

        if tag_name.startswith("/"):
            # Finish the current closing tag by adding the opening tag it to it's parent node
            if len(self.unfinished) == 1:
                return  # Very last closing tag has no parent / no unfinished node

            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag_name in SELF_CLOSING_TAGS:
            # Add the self-closing tag to the parent node directly
            parent = self.unfinished[-1]
            node = TAGElement(tag_name, parent, attributes)
            parent.children.append(node)
        else:
            # Adds the new node to the unfinished list
            parent = (
                self.unfinished[-1] if self.unfinished else None
            )  # Very first open tag has no parent
            node = TAGElement(tag_name, parent, attributes)
            self.unfinished.append(node)

    def finish(self) -> HTMLElement:
        """Finishes the parsing process by closing any remaining tags in the unfinished list and returning the root node."""

        if not self.unfinished:
            self.implicit_tags(None)

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

    def get_attributes(self, text: str) -> tuple[str, dict[str, str]]:
        """
        Parses the attributes of an HTML tag. Returns the tag name and a dictionary of attributes.

        Example: `"meta charset="utf-8""` returns `("meta", {"charset": "utf-8"})`.
        """

        parts = text.split()
        tag_name = parts[0].casefold()

        attributes: dict[str, str] = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                attributes[key.casefold()] = value.strip("\"'")
            else:
                attributes[attrpair.casefold()] = ""

        return tag_name, attributes

    def implicit_tags(self, tag_name: str | None):
        """Handles implicit tags in the HTML structure. If the tag is not a self-closing tag, it closes the last unfinished tag."""

        while True:
            open_tags = [node.tag_name for node in self.unfinished]

            if open_tags == [] and tag_name != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag_name not in ["head", "body", "/html"]:
                if tag_name in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif (
                open_tags == ["html", "head"]
                and tag_name not in ["/head"] + self.HEAD_TAGS
            ):
                self.add_tag("/head")
            else:
                break  # Technically, the </body> and </html> tags can also be implicit. But since our finish function already closes any unfinished tags, that doesn’t need any extra code.


def print_tree(
    node: HTMLElement,
    prefix_parts: list[str] | None = None,
    is_last_sibling: bool = True,
):
    """Recursively prints the tree structure of the node and its children. Like
    ```
    <html>
    ├── <head>
    │   └── <title>
    │       └── "Title"
    └── <body>
        ├── <h1>
        │   └── "Header"
        └── <p>
            └── "Paragraph"
    ```
    """

    if prefix_parts is None:
        print(str(node))
        children = getattr(node, "children", [])
        num_children = len(children)
        for i, child_node in enumerate(children):
            print_tree(child_node, [], i == num_children - 1)
        return

    current_line_prefix = "".join(prefix_parts)
    connector = "└── " if is_last_sibling else "├── "
    print(current_line_prefix + connector + str(node))

    children = getattr(node, "children", [])
    num_children = len(children)

    new_prefix_segment = "    " if is_last_sibling else "│   "

    for i, child_node in enumerate(children):
        child_prefix_parts = prefix_parts + [new_prefix_segment]
        print_tree(child_node, child_prefix_parts, i == num_children - 1)
