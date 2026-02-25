# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from pathlib import Path

from django.conf import settings


_LOGO_CACHE = None


def _luma(rgb):
    r, g, b = rgb
    return int(0.2126 * r + 0.7152 * g + 0.0722 * b)


def _find_logo_path():
    base = Path(getattr(settings, "GAME_DIR", "."))
    try:
        import evennia as _ev_pkg
        ui_dir = Path(_ev_pkg.__file__).parent / "web" / "static" / "ui"
    except Exception:
        ui_dir = None
    candidates = []
    if ui_dir:
        candidates += [
            ui_dir / "dbforgedfullcoloralpha.png",
            ui_dir / "dbforgedfullcoloralpha.png.png",
            ui_dir / "dbforgedfullcolor.png",
            ui_dir / "dbforgedfullcolonoalpha.png",
            ui_dir / "logo.png",
        ]
    candidates += [
        base / "server" / "conf" / "assets" / "db_logo.png",
        base / "server" / "conf" / "assets" / "dragonball_logo.png",
        base / "server" / "conf" / "assets" / "logo.png",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _fallback_logo_ascii():
    """
    Handcrafted coloured ASCII fallback shown when no image asset is present.
    """
    return "\n".join(
        [
            "                |y██████╗ ██████╗  █████╗  ██████╗  ██████╗ ███╗   ██╗|n",
            "                |y██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║|n",
            "                |y██║  ██║██████╔╝███████║██║  ███╗██║   ██║██╔██╗ ██║|n",
            "                |y██║  ██║██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╗██║|n",
            "                |y██████╔╝██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║|n",
            "                |y╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝|n",
            "                              |r██████╗  █████╗ ██╗     ██╗     |n",
            "                              |r██╔══██╗██╔══██╗██║     ██║     |n",
            "                              |r██████╔╝███████║██║     ██║     |n",
            "                              |r██╔══██╗██╔══██║██║     ██║     |n",
            "                              |r██████╔╝██║  ██║███████╗███████╗|n",
            "                              |r╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝|n",
        ]
    )


def _render_logo_ansi():
    """
    Render a color logo PNG as truecolor ANSI half-block art.

    Preferred input is a transparent PNG (alpha-driven mask). If the image has
    no alpha, we derive a mask from chroma/luma so full-color art on black still
    works during iteration.
    """
    global _LOGO_CACHE
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE

    logo_path = _find_logo_path()
    if not logo_path:
        _LOGO_CACHE = _fallback_logo_ascii()
        return _LOGO_CACHE

    try:
        from PIL import Image
    except Exception:
        _LOGO_CACHE = _fallback_logo_ascii()
        return _LOGO_CACHE

    try:
        color_rgba = Image.open(logo_path).convert("RGBA")
        alpha = color_rgba.getchannel("A")
        amin, amax = alpha.getextrema()

        if amin < 255 and amax > 0:
            mask_src = alpha
            threshold_fn = lambda px: px >= 124
        else:
            # Fallback for non-alpha exports: treat colorful pixels and dark
            # outline/shadow pixels as logo, ignore near-black background.
            rgb = color_rgba.convert("RGB")
            w, h = rgb.size
            rp = rgb.load()
            mask_src = Image.new("L", (w, h), 0)
            mp = mask_src.load()
            for yy in range(h):
                for xx in range(w):
                    r, g, b = rp[xx, yy]
                    lum = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
                    chroma = max(r, g, b) - min(r, g, b)
                    if chroma >= 20 or (lum >= 18 and lum <= 210):
                        mp[xx, yy] = 255
            threshold_fn = lambda px: px >= 96

        mw, mh = mask_src.size
        mpx = mask_src.load()
        fg_xs = [xx for yy in range(mh) for xx in range(mw) if mpx[xx, yy] >= 16]
        fg_ys = [yy for yy in range(mh) for xx in range(mw) if mpx[xx, yy] >= 16]
        if not fg_xs:
            raise ValueError("Logo image has no detectable foreground pixels")

        pad = 2
        bx0 = max(0, min(fg_xs) - pad)
        by0 = max(0, min(fg_ys) - pad)
        bx1 = min(mw - 1, max(fg_xs) + pad)
        by1 = min(mh - 1, max(fg_ys) + pad)

        color_crop = color_rgba.crop((bx0, by0, bx1 + 1, by1 + 1))
        mask_crop = mask_src.crop((bx0, by0, bx1 + 1, by1 + 1))

        out_w = 140
        content_w, content_h = mask_crop.size
        out_px_h = max(4, int(out_w * (content_h / max(1, content_w)) * 0.47 * 2))
        if out_px_h % 2:
            out_px_h += 1

        mask_small = mask_crop.resize((out_w, out_px_h), Image.Resampling.BOX)
        color_small = color_crop.resize((out_w, out_px_h), Image.Resampling.LANCZOS)
        mp = mask_small.load()
        cp = color_small.load()

        def is_fg(x, y):
            return threshold_fn(mp[x, y])

        x0, y0, x1, y1 = 0, 0, out_w - 1, out_px_h - 1
        while y0 < y1 and not any(is_fg(xx, y0) for xx in range(out_w)):
            y0 += 1
        while y1 > y0 and not any(is_fg(xx, y1) for xx in range(out_w)):
            y1 -= 1
        while x0 < x1 and not any(is_fg(x0, yy) for yy in range(out_px_h)):
            x0 += 1
        while x1 > x0 and not any(is_fg(x1, yy) for yy in range(out_px_h)):
            x1 -= 1
        if ((y1 - y0 + 1) % 2) != 0 and y1 > y0:
            y1 -= 1

        top_block = "\u2580"
        bottom_block = "\u2584"
        lines = []
        for y in range(y0, y1 + 1, 2):
            parts = []
            for x in range(x0, x1 + 1):
                top_fg = is_fg(x, y)
                bot_fg = is_fg(x, y + 1) if (y + 1) <= y1 else False
                if not top_fg and not bot_fg:
                    parts.append(" ")
                    continue
                tr, tg, tb, _ = cp[x, y]
                br, bg, bb, _ = cp[x, y + 1] if (y + 1) <= y1 else (0, 0, 0, 0)
                if top_fg and bot_fg:
                    parts.append(f"\x1b[48;2;{br};{bg};{bb}m\x1b[38;2;{tr};{tg};{tb}m{top_block}")
                elif top_fg:
                    parts.append(f"\x1b[48;2;0;0;0m\x1b[38;2;{tr};{tg};{tb}m{top_block}")
                else:
                    parts.append(f"\x1b[48;2;0;0;0m\x1b[38;2;{br};{bg};{bb}m{bottom_block}")
            parts.append("\x1b[0m")
            lines.append("".join(parts).rstrip())

        _LOGO_CACHE = "\n".join(lines)
        return _LOGO_CACHE
    except Exception:
        _LOGO_CACHE = _fallback_logo_ascii()
        return _LOGO_CACHE

def connection_screen():
    # Webclient now uses a real PNG banner; keep the message text-only.
    logo = ""
    version = getattr(settings, "DBFORGED_VERSION", "0.1")
    orange = "\x1b[38;2;255;140;0m"
    red = "\x1b[38;2;220;35;35m"
    yellow = "\x1b[38;2;255;215;0m"
    reset = "\x1b[0m"
    # Welcome to Drag(*)nball Forged - Dragn=Yellow, {}=orange, *ED=red
    dragonball_forged = f"{yellow}Drag{orange}({red}*{orange})nball{orange}Forg{red}ED{reset}"
    # Center tagline under the 64-char banner
    tagline = (
        " |wWelcome to |n"
        f"{dragonball_forged}|n "
        "|wby|n |mTeam Tartarus|n"
    )
    header = (
        "|b==============================================================|n\n"
        f"     Welcome to |g{settings.SERVERNAME}|n, version {version}!\n"
    )
    if logo:
        header += "\n" + logo + "\n" + tagline + "\n"
    else:
        header += "\n" + tagline + "\n"
    body = (
        "\n"
        "     If you have an existing account, connect to it by typing:\n"
        "          |wconnect <username> <password>|n\n"
        "     If you need to create an account, type (without the <>'s):\n"
        "          |wcreate <username> <password>|n\n"
        "\n"
        "     If you have spaces in your username, enclose it in quotes.\n"
        "     Enter |whelp|n for more info. |wlook|n will re-show this screen.\n"
        "|b==============================================================|n"
    )
    return header + body
