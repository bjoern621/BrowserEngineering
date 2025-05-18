class Tag:
    """
    A class representing an HTML tag.
    A Tag object represents the contens of an HTML tag, which is a run of characters inside a tag.
    E.g. '!doctpye html', div, p, span, /span, ....
    """

    def __init__(self, tag_name: str):
        self.tag_name = tag_name
