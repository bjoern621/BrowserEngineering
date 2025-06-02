from css_parser.base_selector import BaseCSSSelector
from css_parser.descendant_selector import DescendantSelector
from css_parser.tag_selector import TagSelector


class CSSParser:
    """Parser for CSS string that parses a CSS string (i.e., a string containing CSS rules like `\"background-color:lightblue\"` or \"
    .video {
        width: 100%;
        height: 100%;
    }

    .loading-container {
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }\") into a format that can be used by the layout engine.

    The class contains different methods to parse specific parts of the CSS string, such as  selectors, whitespaces, properties or property-values.
    """

    def __init__(self, css_string: str) -> None:
        self.css: str = css_string
        self.index: int = 0

    def whitespace(self):
        """Parse whitespace characters."""

        while self.index < len(self.css) and self.css[self.index].isspace():
            self.index += 1

    def word(self) -> str:
        """Parse any kind of word. A word is a sequence of letters, dashes, numbers (negative and positive and including decimal points),
        and percent signs. It can also start with a hash sign (#) to indicate an ID selector or a HEX color.

        Example of valid words:
        - `background-color`
        - `#ff0000`
        - `#my-id`
        - `width`
        - `100%`
        - `-12.45`
        - `-webkit-transition`

        The functions returns the parsed word as a string.
        Raises a ValueError if the expected format is not found.
        """

        start = self.index
        while self.index < len(self.css):
            if self.css[self.index].isalnum() or self.css[self.index] in "#-.%":
                self.index += 1
            else:
                break
        if not (self.index > start):
            raise ValueError("Expected a word at index {}".format(self.index))

        return self.css[start : self.index]

    def literal(self, literal: str) -> None:
        """Parse a literal string. The function checks if the next characters in the CSS string match the given literal.
        If they do not match, it raises a ValueError.

        Example:
        - `literal("background-color")` will check if the next characters in the CSS string are "background-color".

        Raises a ValueError if the expected literal is not found at the current index.
        """

        end = self.index + len(literal)
        if self.css[self.index : end] != literal:
            raise ValueError("Expected '{}' at index {}".format(literal, self.index))
        self.index = end

    def property_pair(self) -> tuple[str, str]:
        """
        Parse a property-value pair. The function expects a word (the property name), followed by a colon, optional whitespace,
        and then a word (the property value). It returns a tuple containing the property name and value.

        Example:
        - `property_pair()` will parse `background-color: lightblue` and return `("background-color", "lightblue")`.

        Raises a ValueError if the expected format is not found.
        """

        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        value = self.word()
        return prop.casefold(), value

    def body(self) -> dict[str, str]:
        """Parse the body of a CSS rule (i.e., the text inside `{` and `}`). The function expects one or more property-value pairs separated by semicolons."""

        pairs: dict[str, str] = {}
        while self.index < len(self.css) and self.css[self.index] != "}":
            try:
                prop, value = self.property_pair()
                pairs[prop.casefold()] = value
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except ValueError:
                exception_reason = self.ignore_until([";", "}"])
                if exception_reason == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    def ignore_until(self, chars: list[str]) -> str | None:
        """Ignore characters until one of the specified characters is found. This is useful for skipping over parts of the CSS string
        that are not relevant for parsing, such as comments or other non-CSS content.

        Example:
        - `ignore_until(["{", "}", ";"])` will skip characters until it finds one of these characters.
        """

        while self.index < len(self.css):
            if self.css[self.index] in chars:
                return self.css[self.index]  # Return the character that was found
            else:
                self.index += 1

        return None  # End of file reached

    def selector(self) -> BaseCSSSelector:
        """Parse a CSS selector. The function expects a tag name followed by optional descendant selectors (e.g., `div p`)."""

        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.index < len(self.css) and self.css[self.index] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()

        return out

    def parse_css_file(self) -> list[tuple[BaseCSSSelector, dict[str, str]]]:
        """Parse an entire CSS file and return a list of tuples of selectors and their property-value pairs."""

        rules: list[tuple[BaseCSSSelector, dict[str, str]]] = []

        while self.index < len(self.css):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except ValueError:
                reason = self.ignore_until(["}"])
                if reason == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break

        return rules
