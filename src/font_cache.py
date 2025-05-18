import tkinter.font
from typing import Dict, Literal, Tuple

FONTS: Dict[
    Tuple[
        int, Literal["normal", "bold"], Literal["roman", "italic"], bool
    ],  # [font_size, font_weight, font_slant, font_underline]
    Tuple[tkinter.font.Font, tkinter.Label],
] = {}


def get_font(
    size: int,
    weight: Literal["normal", "bold"],
    slant: Literal["roman", "italic"],
    underline: bool,
) -> tkinter.font.Font:
    """
    Retrieves or creates a cached tkinter.font.Font object.
    This function manages a cache of font objects to optimize performance
    by reusing existing fonts.
    """

    key = (size, weight, slant, underline)

    if key not in FONTS:
        font = tkinter.font.Font(
            size=size, weight=weight, slant=slant, underline=underline
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]
