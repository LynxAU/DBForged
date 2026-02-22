"""
Simple cosmetic color -> Evennia ANSI mapping for text previews.
"""

ANSI_COLOR_MAP = {
    "black": "|x",
    "white": "|w",
    "gray": "|x",
    "grey": "|x",
    "silver": "|w",
    "red": "|r",
    "crimson": "|r",
    "maroon": "|r",
    "blue": "|b",
    "navy": "|b",
    "cyan": "|c",
    "teal": "|c",
    "green": "|g",
    "lime": "|g",
    "yellow": "|y",
    "gold": "|y",
    "blond": "|y",
    "blonde": "|y",
    "orange": "|y",
    "purple": "|m",
    "violet": "|m",
    "magenta": "|m",
    "pink": "|m",
    # Additional colors
    "brown": "|y",  # Brown as golden/yellow tone
    "hazel": "|y",  # Hazel as golden tone
    "bronze": "|y",  # Bronze as golden tone
    "none": "|x",   # No aura - black
}


def color_tag(color_name):
    return ANSI_COLOR_MAP.get((color_name or "").strip().lower(), "|w")


def colorize(color_name, text=None):
    shown = text if text is not None else (color_name or "unknown")
    return f"{color_tag(color_name)}{shown}|n"


def aura_phrase(color_name, noun="aura"):
    return f"{colorize(color_name, color_name)} {noun}"
