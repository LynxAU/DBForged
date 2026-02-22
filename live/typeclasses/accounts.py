"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from evennia.utils.utils import is_iter

from typeclasses.characters import SEX_OPTIONS

DB_MENU_RACES = [
    ("saiyan", "Saiyan", "Powerful warrior race with exponential growth potential"),
    ("human", "Human", "Versatile baseline race with balanced stats"),
    ("namekian", "Namekian", "Regenerative alien race with Namekian Dragon summons"),
    ("frost_demon", "Frost Demon", "Ice-based race with freezing abilities and cunning"),
    ("android", "Android", "Synthetic human with unlimited energy and self-repair"),
    ("bio_android", "Bio-Android", "Organic-synthetic hybrid like Cell with regenerative abilities"),
    ("majin", "Majin", "Magical race with shapeshifting and Buu-esque abilities"),
    ("half_breed", "Half Breed", "Human-Saiyan hybrid with balanced potential"),
    ("truffle", "Truffle", "Underground race with sensory abilities"),
    ("grey", "Grey", "Powerful warrior race from Universe 11"),
]

DB_MENU_HAIR_COLORS = [
    ("black", "Black", "Classic dark hair"),
    ("brown", "Brown", "Warm brown tones"),
    ("blonde", "Blonde", "Bright golden hair"),
    ("red", "Red", "Fiery red hair"),
    ("blue", "Blue", "Cool blue hair"),
    ("white", "White", "Pure white hair"),
    ("silver", "Silver", "Elegant silver hair"),
    ("none", "None", "Bald / No hair"),
]

DB_MENU_EYE_COLORS = [
    ("black", "Black", "Dark mysterious eyes"),
    ("brown", "Brown", "Warm brown eyes"),
    ("blue", "Blue", "Ice blue eyes"),
    ("green", "Green", "Vibrant green eyes"),
    ("amber", "Amber", "Golden amber eyes"),
    ("red", "Red", "Intimidating red eyes"),
    ("silver", "Silver", "Silver shimmering eyes"),
    ("purple", "Purple", "Mystical purple eyes"),
]

DB_MENU_AURA_COLORS = [
    ("white", "White", "Pure golden-white energy"),
    ("blue", "Blue", "Cool electric blue energy"),
    ("gold", "Gold", "Royal golden radiance"),
    ("red", "Red", "Fiery red energy"),
    ("green", "Green", "Nature-based green energy"),
    ("purple", "Purple", "Mystical purple energy"),
    ("pink", "Pink", "Gentle pink energy"),
    ("silver", "Silver", "Ethereal silver light"),
    ("orange", "Orange", "Burning orange flame energy"),
    ("violet", "Violet", "Deep violet mystical energy"),
    ("teal", "Teal", "Calming teal aura"),
    ("indigo", "Indigo", "Deep indigo spiritual energy"),
]

# Color mapping for review display (maps color keys to Evennia color codes)
DB_MENU_COLOR_CODES = {
    # Hair colors
    "black": "|x",      # Dark/Black
    "brown": "|33",     # Brown
    "blonde": "|y",    # Yellow/Gold
    "red": "|r",        # Red
    "blue": "|b",       # Blue
    "white": "|w",      # White
    "silver": "|7",     # Silver/Grey
    "none": "|x",       # Dark (bald)
    # Eye colors
    "green": "|g",      # Green
    "amber": "|33",     # Amber/Brown
    "purple": "|m",     # Magenta/Purple
    # Aura colors
    "gold": "|y",       # Yellow/Gold
    "pink": "|h",       # Light magenta
    "violet": "|m",     # Magenta
    "teal": "|c",       # Cyan
    "indigo": "|4",     # Dark blue
}


def _get_color_code(color_key):
    """Get Evennia color code for a color key."""
    return DB_MENU_COLOR_CODES.get(color_key.lower(), "|w")


def _format_name_gradient(name):
    """Format name with yellow first part and red last 2 letters."""
    if not name or len(name) < 2:
        return f"|y{name}|n"
    # First part in yellow, last 2 letters in red
    first_part = name[:-2] if len(name) > 2 else name[0] if len(name) > 1 else ""
    last_two = name[-2:]
    return f"|y{first_part}|r{last_two}|n"


def _format_color_display(color_key):
    """Format a color name with its actual color."""
    color_code = _get_color_code(color_key)
    display = color_key.replace("_", " ").title()
    return f"{color_code}{display}|n"

DB_MENU_SKIN_PALETTES = {
    "saiyan": [
        ("light", "Light", "Light skin tone"),
        ("tan", "Tan", "Warm tan complexion"),
        ("bronze", "Bronze", "Bronzed golden skin"),
        ("brown", "Brown", "Rich brown skin"),
        ("dark", "Dark", "Deep dark skin"),
    ],
    "human": [
        ("fair", "Fair", "Fair porcelain skin"),
        ("light", "Light", "Light skin tone"),
        ("olive", "Olive", "Olive Mediterranean skin"),
        ("tan", "Tan", "Warm tan complexion"),
        ("brown", "Brown", "Rich brown skin"),
        ("dark", "Dark", "Deep dark skin"),
    ],
    "namekian": [
        ("emerald", "Emerald", "Emerald green Namekian skin"),
        ("mint", "Mint", "Mint green Namekian skin"),
        ("teal", "Teal", "Teal Namekian skin"),
        ("olive", "Olive", "Olive green Namekian skin"),
    ],
    "frost_demon": [
        ("white_violet", "White Violet", "Pale violet frost demon skin"),
        ("ivory_purple", "Ivory Purple", "Ivory with purple hints"),
        ("pale_blue", "Pale Blue", "Pale blue frost demon skin"),
        ("gray_purple", "Gray Purple", "Gray-purple frost demon skin"),
    ],
    "android": [
        ("fair", "Fair", "Synthetic fair skin"),
        ("light", "Light", "Synthetic light skin"),
        ("tan", "Tan", "Synthetic tan skin"),
        ("brown", "Brown", "Synthetic brown skin"),
        ("synthetic_pale", "Synthetic Pale", "Unusual pale synthetic skin"),
    ],
    "bio_android": [
        # Bio-Android like Cell - organic-looking with unique patterns
        ("green", "Green", "Green bio-organic skin (Cell-like)"),
        ("yellow", "Yellow", "Yellow bio-organic skin"),
        ("teal", "Teal", "Teal bio-organic skin"),
        ("lime", "Lime", "Lime green bio-organic skin"),
        ("patterned", "Patterned", "Bio-metal patterned skin"),
    ],
    "majin": [
        ("pink", "Pink", "Classic pink Majin skin"),
        ("rose", "Rose", "Rose-colored Majin skin"),
        ("magenta", "Magenta", "Vibrant magenta Majin skin"),
        ("lavender", "Lavender", "Soft lavender Majin skin"),
        ("blue", "Blue", "Rare blue Majin skin"),
    ],
    "half_breed": [
        # Human-Saiyan hybrid - inherits both traits
        ("light", "Light", "Light skin tone"),
        ("tan", "Tan", "Warm tan complexion"),
        ("bronze", "Bronze", "Bronzed golden skin"),
        ("brown", "Brown", "Rich brown skin"),
        ("dark", "Dark", "Deep dark skin"),
    ],
    "truffle": [
        # Underground race - unique coloring
        ("purple_green", "Purple-Green", "Truffle purple with green undertones"),
        ("dark_purple", "Dark Purple", "Dark purple Truffle skin"),
        ("moss_green", "Moss Green", "Moss green Truffle skin"),
        ("brown_green", "Brown-Green", "Brown-green Truffle skin"),
    ],
    "grey": [
        # Grey (Jiren race) - monochromatic
        ("grey_light", "Light Grey", "Light grey skin"),
        ("grey_silver", "Silver Grey", "Silver-grey skin"),
        ("grey_dark", "Dark Grey", "Dark grey skin"),
        ("grey_charcoal", "Charcoal", "Charcoal grey skin"),
    ],
}


class Account(DefaultAccount):
    """
    An Account is the actual OOC player entity. It doesn't exist in the game,
    but puppets characters.

    This is the base Typeclass for all Accounts. Accounts represent
    the person playing the game and tracks account info, password
    etc. They are OOC entities without presence in-game. An Account
    can connect to a Character Object in order to "enter" the
    game.

    Account Typeclass API:

    * Available properties (only available on initiated typeclass objects)

     - key (string) - name of account
     - name (string)- wrapper for user.username
     - aliases (list of strings) - aliases to the object. Will be saved to
            database as AliasDB entries but returned as strings.
     - dbref (int, read-only) - unique #id-number. Also "id" can be used.
     - date_created (string) - time stamp of object creation
     - permissions (list of strings) - list of permission strings
     - user (User, read-only) - django User authorization object
     - obj (Object) - game object controlled by account. 'character' can also
                     be used.
     - is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     - locks - lock-handler: use locks.add() to add new lock strings
     - db - attribute-handler: store/retrieve database attributes on this
                              self.db.myattr=val, val=self.db.myattr
     - ndb - non-persistent attribute handler: same as db but does not
                                  create a database entry when storing data
     - scripts - script-handler. Add new scripts to object with scripts.add()
     - cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     - nicks - nick-handler. New nicks with nicks.add().
     - sessions - session-handler. Use session.get() to see all sessions connected, if any
     - options - option-handler. Defaults are taken from settings.OPTIONS_ACCOUNT_DEFAULT
     - characters - handler for listing the account's playable characters

    * Helper methods (check autodocs for full updated listing)

     - msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     - execute_cmd(raw_string)
     - search(searchdata, return_puppet=False, search_object=False, typeclass=None,
                      nofound_string=None, multimatch_string=None, use_nicks=True,
                      quiet=False, **kwargs)
     - is_typeclass(typeclass, exact=False)
     - swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     - access(accessing_obj, access_type='read', default=False, no_superuser_bypass=False, **kwargs)
     - check_permstring(permstring)
     - get_cmdsets(caller, current, **kwargs)
     - get_cmdset_providers()
     - uses_screenreader(session=None)
     - get_display_name(looker, **kwargs)
     - get_extra_display_name_info(looker, **kwargs)
     - disconnect_session_from_account()
     - puppet_object(session, obj)
     - unpuppet_object(session)
     - unpuppet_all()
     - get_puppet(session)
     - get_all_puppets()
     - is_banned(**kwargs)
     - get_username_validators(validator_config=settings.AUTH_USERNAME_VALIDATORS)
     - authenticate(username, password, ip="", **kwargs)
     - normalize_username(username)
     - validate_username(username)
     - validate_password(password, account=None)
     - set_password(password, **kwargs)
     - get_character_slots()
     - get_available_character_slots()
     - create_character(*args, **kwargs)
     - create(*args, **kwargs)
     - delete(*args, **kwargs)
     - channel_msg(message, channel, senders=None, **kwargs)
     - idle_time()
     - connection_time()

    * Hook methods

     basetype_setup()
     at_account_creation()

     > note that the following hooks are also found on Objects and are
       usually handled on the character level:

     - at_init()
     - at_first_save()
     - at_access()
     - at_cmdset_get(**kwargs)
     - at_password_change(**kwargs)
     - at_first_login()
     - at_pre_login()
     - at_post_login(session=None)
     - at_failed_login(session, **kwargs)
     - at_disconnect(reason=None, **kwargs)
     - at_post_disconnect(**kwargs)
     - at_message_receive()
     - at_message_send()
     - at_server_reload()
     - at_server_shutdown()
     - at_look(target=None, session=None, **kwargs)
     - at_post_create_character(character, **kwargs)
     - at_post_add_character(char)
     - at_post_remove_character(char)
     - at_pre_channel_msg(message, channel, senders=None, **kwargs)
     - at_post_chnnel_msg(message, channel, senders=None, **kwargs)

    """

    def _db_menu_box(self, title, lines, width=120):
        inner = max(40, width - 2)
        top = f"|b+{'-' * inner}+|n"
        bottom = top
        title_text = f" {title} "
        if len(title_text) > inner:
            title_text = title_text[:inner]
        left = max(0, (inner - len(title_text)) // 2)
        right = max(0, inner - len(title_text) - left)
        out = [top, f"|b|n{' ' * left}|y{title_text}|n{' ' * right}|b|n", top]
        for line in lines:
            text = str(line)
            chunks = [text[i : i + inner] for i in range(0, len(text), inner)] or [""]
            for chunk in chunks:
                out.append(f"|b|n{chunk.ljust(inner)}|b|n")
        out.append(bottom)
        return "\n".join(out)

    def _db_menu_clear(self):
        # ANSI clear screen + cursor home (works in telnet clients and most terminals).
        return "\x1b[2J\x1b[H"

    def _db_menu_states(self):
        store = getattr(self.ndb, "_db_menu_states", None)
        if store is None:
            store = {}
            self.ndb._db_menu_states = store
        return store

    def _db_menu_state(self, session=None):
        states = self._db_menu_states()
        active_sessions = list(self.sessions.all())
        active_sessids = {getattr(s, "sessid", None) for s in active_sessions}
        active_sessids.discard(None)
        # Clean up stale per-session menu state entries across reconnects.
        for sid in list(states.keys()):
            if sid != 0 and sid not in active_sessids:
                states.pop(sid, None)
        if not session:
            if len(active_sessions) == 1:
                session = active_sessions[0]
            elif len(states) == 1:
                # Reuse the only active menu state when session is omitted by the caller.
                return next(iter(states.values()))
        if not session:
            sessions = list(self.sessions.all())
            if len(sessions) == 1:
                session = sessions[0]
        sid = getattr(session, "sessid", 0) if session else 0
        if sid not in states:
            states[sid] = {"mode": "main"}
        return states[sid]

    def _db_menu_canonical_session(self, session=None):
        """
        Resolve a session-like object to the live session instance attached to this account.
        """
        if not session:
            return session
        sessid = getattr(session, "sessid", None)
        if sessid is None:
            return session
        for live_sess in self.sessions.all():
            if getattr(live_sess, "sessid", None) == sessid:
                return live_sess
        return session

    def _db_menu_reset(self, session=None):
        state = self._db_menu_state(session=session)
        state.clear()
        state["mode"] = "main"
        state["menu_sent"] = False
        return state

    def _db_menu_send(self, session=None):
        self.msg(self._db_menu_clear() + self.at_look(target=self.characters, session=session), session=session)
        self._db_menu_state(session=session)["menu_sent"] = True

    def _db_menu_character_lines(self):
        chars = [char for char in self.characters if char]
        if not chars:
            return []
        lines = []
        for idx, char in enumerate(chars, start=1):
            status = "|Yin creation|n" if not getattr(char.db, "chargen_complete", False) else "|Gready|n"
            lines.append(f" {idx}. |w{char.key}|n ({status})")
        return lines

    def at_look(self, target=None, session=None, **kwargs):
        """
        Show a custom OOC main menu after login while preserving normal single-target look behavior.
        """
        if target and not is_iter(target):
            return super().at_look(target=target, session=session, **kwargs)

        sessions = self.sessions.all()
        if not sessions:
            return ""

        lines = [
            "|yDragonballForged|n",
            "",
            "|c1|n - |wEnter Game|n",
            "|c2|n - |wCreate Character|n",
            "|c3|n - |wDelete Character|n",
            "|c4|n - |wExit|n",
            "",
            "|wEnter 1, 2, 3, or 4.|n",
        ]
        if session:
            self._db_menu_state(session=session)["menu_sent"] = True
        return self._db_menu_box("MAIN MENU", lines)

    def _db_menu_render_charlist(self, session=None, for_delete=False):
        chars = [char for char in self.characters if char]
        if not chars:
            msg = "You have no characters to delete!" if for_delete else "You have no characters yet!"
            self.msg(f"|r{msg}|n", session=session)
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)
            return
        label = "DELETE CHARACTER" if for_delete else "ENTER GAME"
        lines = [f"|y{label}|n", ""]
        for idx, char in enumerate(chars, start=1):
            status = "|Yin creation|n" if not getattr(char.db, "chargen_complete", False) else "|Gready|n"
            lines.append(f" |c{idx}|n - |w{char.key}|n ({status})")
        lines.append("")
        if for_delete:
            lines.append("Select a character number to delete.")
        else:
            lines.append("Select a character number to enter game.")
        lines.append("|cB|n - |wGo Back|n")
        self.msg(self._db_menu_box(label, lines), session=session)

    def _db_menu_get_chars(self):
        return [char for char in self.characters if char]

    def _db_menu_pick_char_by_input(self, value):
        chars = self._db_menu_get_chars()
        text = (value or "").strip()
        if not chars:
            return None, "You have no characters yet!"
        if not text:
            return None, "Please enter a character number."
        if text.isdigit():
            idx = int(text)
            if 1 <= idx <= len(chars):
                return chars[idx - 1], None
            return None, "That character number does not exist."
        return None, "Please enter a valid character number."

    def _db_menu_format_choices(self, options):
        lines = []
        for idx, item in enumerate(options, start=1):
            # Handle tuple format: (value, label, description) or (value, label)
            if isinstance(item, tuple) and len(item) >= 3:
                value, label, description = item[0], item[1], item[2]
            elif isinstance(item, tuple):
                value, label = item[0], item[1]
                description = ""
            else:
                label = str(item)
                value = str(item).lower().replace(" ", "_")
                description = ""
            
            # Determine color based on option type
            color = self._db_menu_get_option_color(label)
            if description:
                lines.append(f"|c[{idx}]|n {color}{label}|n - {description}")
            else:
                lines.append(f"|c[{idx}]|n {color}{label}|n")
        return lines

    def _db_menu_get_option_color(self, label):
        """Get appropriate color for menu option based on its content."""
        label_lower = label.lower()
        
        # Race-specific colors
        races = {
            "saiyan": "|r",      # Red for warrior race
            "human": "|w",        # White for baseline
            "namekian": "|g",     # Green for alien
            "frost_demon": "|c",  # Cyan for cold/frost
            "android": "|y",      # Yellow for mechanical
            "majin": "|m",        # Magenta for magical
        }
        if label_lower in races:
            return races[label_lower]
        
        # Hair color matching
        hair_colors = {
            "black": "|x",      # Dark
            "brown": "|y",      # Brown/yellow
            "blonde": "|w",     # White/bright  
            "red": "|r",        # Red
            "blue": "|b",       # Blue
            "white": "|c",      # Cyan/white
            "silver": "|c",     # Silver/cyan
            "none": "|x",       # Dark/none
        }
        if label_lower in hair_colors:
            return hair_colors[label_lower]
        
        # Eye color matching
        eye_colors = {
            "black": "|x",      # Dark
            "brown": "|y",      # Brown
            "blue": "|b",       # Blue
            "green": "|g",      # Green
            "amber": "|y",      # Amber/yellow
            "red": "|r",        # Red
            "silver": "|c",     # Silver
            "purple": "|m",      # Purple
        }
        if label_lower in eye_colors:
            return eye_colors[label_lower]
        
        # Aura color matching  
        aura_colors = {
            "white": "|w",      # White
            "blue": "|b",       # Blue
            "gold": "|y",       # Gold
            "red": "|r",        # Red
            "green": "|g",      # Green
            "purple": "|m",     # Purple
            "pink": "|r",       # Pink/red
            "silver": "|c",     # Silver
            "orange": "|y",     # Orange
            "violet": "|m",     # Violet/magenta
            "teal": "|b",       # Teal/blue
            "indigo": "|c",     # Indigo/cyan
        }
        if label_lower in aura_colors:
            return aura_colors[label_lower]
        
        # Skin color matching
        skin_colors = {
            "light": "|w",      # Light/white
            "fair": "|w",       # Fair/white
            "tan": "|y",        # Tan/yellow
            "bronze": "|y",     # Bronze/yellow
            "olive": "|g",       # Olive/green
            "brown": "|y",       # Brown/yellow
            "dark": "|x",        # Dark
            "emerald": "|g",     # Emerald/green
            "mint": "|g",        # Mint/green
            "teal": "|b",        # Teal/blue
            "ivory": "|w",       # Ivory/white
            "pale": "|c",        # Pale/cyan
            "synthetic": "|y",   # Synthetic/yellow
            "pink": "|r",        # Pink
            "rose": "|r",        # Rose/red
            "magenta": "|m",     # Magenta
            "lavender": "|m",    # Lavender/magenta
        }
        if label_lower in skin_colors:
            return skin_colors[label_lower]
        
        # Default to white if no match
        return "|w"

    def _db_menu_choice_value(self, options, raw_text):
        text = (raw_text or "").strip()
        
        # First try numeric input
        if text.isdigit():
            idx = int(text)
            if not (1 <= idx <= len(options)):
                return None, "That number is not in the list."
            item = options[idx - 1]
            # Handle tuple format: (value, label, description) or (value, label) or just string
            if isinstance(item, tuple):
                return item[0], None
            return str(item).lower().replace(" ", "_"), None
        
        # Try text input - check for direct match or partial match
        text_lower = text.lower()
        for idx, item in enumerate(options, start=1):
            # Handle tuple format: (value, label, description) or (value, label) or just string
            if isinstance(item, tuple):
                value, label = item[0], item[1]
                # Check if text matches value, label, or is contained in them
                if (text_lower == value.lower() or 
                    text_lower == label.lower() or 
                    text_lower in value.lower() or 
                    text_lower in label.lower()):
                    return value, None
            else:
                item_str = str(item)
                if text_lower == item_str.lower() or text_lower in item_str.lower():
                    return item_str.lower().replace(" ", "_"), None
        
        return None, "Please enter a number or a valid option name."

    def _db_menu_create_default_data(self):
        # Helper to extract value from tuple format (value, label, desc) or string
        def get_first_value(options_list):
            if not options_list:
                return ""
            first = options_list[0]
            if isinstance(first, tuple):
                return first[0]  # Get the value part
            return str(first).lower().replace(" ", "_")
        
        return {
            "name": "",
            "race": get_first_value(DB_MENU_RACES),
            "hair_style": "spiky",
            "sex": "other",
            "hair_color": get_first_value(DB_MENU_HAIR_COLORS),
            "eye_color": get_first_value(DB_MENU_EYE_COLORS),
            "skin_color": get_first_value(self._db_menu_create_skin_palette(get_first_value(DB_MENU_RACES))),
            "aura_color": get_first_value(DB_MENU_AURA_COLORS),
        }

    def _db_menu_create_skin_palette(self, race_key):
        # Define skin palettes with descriptions
        skin_data = {
            "saiyan": [
                ("light", "Light", "Light skin tone"),
                ("tan", "Tan", "Warm tan complexion"),
                ("bronze", "Bronze", "Bronzed golden skin"),
                ("brown", "Brown", "Rich brown skin"),
                ("dark", "Dark", "Deep dark skin"),
            ],
            "human": [
                ("fair", "Fair", "Fair porcelain skin"),
                ("light", "Light", "Light skin tone"),
                ("olive", "Olive", "Olive Mediterranean skin"),
                ("tan", "Tan", "Warm tan complexion"),
                ("brown", "Brown", "Rich brown skin"),
                ("dark", "Dark", "Deep dark skin"),
            ],
            "namekian": [
                ("emerald", "Emerald", "Emerald green Namekian skin"),
                ("mint", "Mint", "Mint green Namekian skin"),
                ("teal", "Teal", "Teal Namekian skin"),
                ("olive", "Olive", "Olive green Namekian skin"),
            ],
            "frost_demon": [
                ("white_violet", "White Violet", "Pale violet frost demon skin"),
                ("ivory_purple", "Ivory Purple", "Ivory with purple hints"),
                ("pale_blue", "Pale Blue", "Pale blue frost demon skin"),
                ("gray_purple", "Gray Purple", "Gray-purple frost demon skin"),
            ],
            "android": [
                ("fair", "Fair", "Synthetic fair skin"),
                ("light", "Light", "Synthetic light skin"),
                ("tan", "Tan", "Synthetic tan skin"),
                ("brown", "Brown", "Synthetic brown skin"),
                ("synthetic_pale", "Synthetic Pale", "Unusual pale synthetic skin"),
            ],
            "majin": [
                ("pink", "Pink", "Classic pink Majin skin"),
                ("rose", "Rose", "Rose-colored Majin skin"),
                ("magenta", "Magenta", "Vibrant magenta Majin skin"),
                ("lavender", "Lavender", "Soft lavender Majin skin"),
                ("blue", "Blue", "Rare blue Majin skin"),
            ],
        }
        return skin_data.get(race_key, skin_data.get("human"))

    def _db_menu_create_set_default_skin(self, data):
        race_key = data.get("race") or DB_MENU_RACES[0][0]
        current = (data.get("skin_color") or "").replace("_", " ").lower()
        palette = self._db_menu_create_skin_palette(race_key)
        # palette is list of tuples (key, display_name, description)
        palette_keys = {p[0].lower() for p in palette}
        if current not in palette_keys:
            data["skin_color"] = palette[0][0].replace(" ", "_")

    def _db_menu_start_create(self, session=None):
        state = self._db_menu_state(session=session)
        state.clear()
        state.update(
            {
                "mode": "create",
                "step": 0,
                "data": self._db_menu_create_default_data(),
            }
        )
        self._db_menu_prompt_create(session=session)

    def _db_menu_start_create_cancel_confirm(self, session=None):
        state = self._db_menu_state(session=session)
        state["prev_mode"] = state.get("mode", "create")
        state["mode"] = "create_cancel_confirm"
        self.msg(
            self._db_menu_box(
                "CANCEL CREATION",
                [
                    "|rCancel creation?|n",
                    " |c1|n Yes",
                    " |c2|n No",
                    "",
                    "|cB|n - Back",
                ],
            ),
            session=session,
        )

    def _db_menu_create_step_defs(self, data):
        race_key = (data.get("race") or DB_MENU_RACES[0][0]).lower()
        return [
            {"key": "name", "kind": "text", "title": "Step 1/7 - Name", "prompt": "Name: Enter your character name."},
            {"key": "race", "kind": "choice", "title": "Step 2/7 - Race", "prompt": "Choose a race:", "options": DB_MENU_RACES},
            {"key": "hair_color", "kind": "choice", "title": "Step 3/7 - Hair Color", "prompt": "Choose hair color:", "options": DB_MENU_HAIR_COLORS},
            {"key": "eye_color", "kind": "choice", "title": "Step 4/7 - Eye Color", "prompt": "Choose eye color:", "options": DB_MENU_EYE_COLORS},
            {
                "key": "skin_color",
                "kind": "choice",
                "title": "Step 5/7 - Skin Color",
                "prompt": f"Choose skin color for {race_key.replace('_', ' ').title()}:",
                "options": self._db_menu_create_skin_palette(race_key),
            },
            {"key": "aura_color", "kind": "choice", "title": "Step 6/7 - Aura Color", "prompt": "Choose aura color:", "options": DB_MENU_AURA_COLORS},
            {"key": "__review__", "kind": "review", "title": "Step 7/7 - Review", "prompt": "Is this correct?"},
        ]

    def _db_menu_create_display(self, data, key):
        val = data.get(key, "")
        return str(val).replace("_", " ").title() if key != "name" else str(val)

    def _db_menu_prompt_create(self, session=None):
        state = self._db_menu_state(session=session)
        data = state.get("data", {})
        step = int(state.get("step", 0))
        steps = self._db_menu_create_step_defs(data)
        if step < 0:
            step = 0
            state["step"] = 0
        if step >= len(steps):
            step = len(steps) - 1
            state["step"] = step
        stepdef = steps[step]
        lines = [f"|y{stepdef['title']}|n", ""]
        if stepdef["kind"] == "text":
            current = self._db_menu_create_display(data, stepdef["key"]) or "-"
            lines.extend(
                [
                    stepdef["prompt"],
                    f"|xCurrent:|n {current}",
                    "",
                    "|wB|n = Back   |wC|n = Cancel",
                ]
            )
        elif stepdef["kind"] == "choice":
            lines.append(stepdef["prompt"])
            lines.append("")
            lines.extend(self._db_menu_format_choices(stepdef["options"]))
            current = self._db_menu_create_display(data, stepdef["key"])
            lines.extend(["", f"|xCurrent:|n {current}", "|wB|n = Back   |wC|n = Cancel"])
        else:  # review
            # Format name with yellow/red gradient
            name = data.get('name', '')
            formatted_name = _format_name_gradient(name)
            # Format colors with their actual colors
            hair_color = _format_color_display(data.get('hair_color', ''))
            eye_color = _format_color_display(data.get('eye_color', ''))
            skin_color = _format_color_display(data.get('skin_color', ''))
            aura_color = _format_color_display(data.get('aura_color', ''))
            lines.extend(
                [
                    f"|wName|n: {formatted_name}",
                    f"|wRace|n: {self._db_menu_create_display(data, 'race')}",
                    f"|wHair Color|n: {hair_color}",
                    f"|wEye Color|n: {eye_color}",
                    f"|wSkin Color|n: {skin_color}",
                    f"|wAura Color|n: {aura_color}",
                    "",
                    "Is this correct?",
                    " |c1|n Yes",
                    " |c2|n No",
                    "",
                    "|wB|n = Back   |wC|n = Cancel",
                ]
            )
        self.msg(self._db_menu_box("CHARACTER CREATION", lines), session=session)

    def _db_menu_handle_create_input(self, raw_string, session=None):
        state = self._db_menu_state(session=session)
        text = (raw_string or "").strip()
        data = state.get("data", {})
        step = int(state.get("step", 0))
        steps = self._db_menu_create_step_defs(data)
        
        # Handle back/cancel commands
        if text.lower() in {"b", "back"}:
            if step <= 0:
                self._db_menu_reset(session=session)
                self._db_menu_send(session=session)
                return True
            state["step"] = step - 1
            self._db_menu_prompt_create(session=session)
            return True
        if text.lower() == "c":
            self._db_menu_start_create_cancel_confirm(session=session)
            return True

        if step >= len(steps):
            state["step"] = len(steps) - 1
            step = state["step"]
        stepdef = steps[step]

        if stepdef["kind"] == "review":
            if text == "2":
                state["step"] = 1  # back to Race step per spec
                self._db_menu_prompt_create(session=session)
                return True
            if text != "1":
                self.msg("|rPlease enter 1 or 2.|n", session=session)
                self._db_menu_prompt_create(session=session)
                return True
            desc = (
                f"A {data['race'].replace('_', ' ')} fighter with "
                f"{data['hair_color'].replace('_', ' ')} hair and {data['eye_color'].replace('_', ' ')} eyes."
            )
            new_character, errors = self.create_character(
                key=data["name"], description=desc, ip=(session.address if session else "")
            )
            if errors:
                self.msg(errors, session=session)
                self._db_menu_reset(session=session)
                self._db_menu_send(session=session)
                return True
            if not new_character:
                self.msg("|rCharacter creation failed.|n", session=session)
                self._db_menu_reset(session=session)
                self._db_menu_send(session=session)
                return True
            for key in ("race", "sex", "hair_style", "hair_color", "eye_color", "aura_color"):
                setattr(new_character.db, key, data[key])
            new_character.db.skin_color = data["skin_color"]
            new_character.db.chargen_complete = True
            new_character.db.chargen_step_index = 0
            if hasattr(new_character, "_refresh_sprite_id"):
                new_character._refresh_sprite_id()
            self.msg(f"|gCharacter created:|n |w{new_character.key}|n", session=session)
            state.clear()
            state["mode"] = "enter_select"
            self._db_menu_render_charlist(session=session, for_delete=False)
            return True

        field = stepdef["key"]
        if stepdef["kind"] == "text":
            cleaned, error = self._db_menu_validate_create_field(field, text)
        else:
            cleaned, error = self._db_menu_choice_value(stepdef["options"], text)
        if error:
            self.msg(f"|r{error}|n", session=session)
            self._db_menu_prompt_create(session=session)
            return True
        data[field] = cleaned
        if field == "race":
            self._db_menu_create_set_default_skin(data)
        state["step"] = step + 1
        self._db_menu_prompt_create(session=session)
        return True

    def _db_menu_handle_create_cancel_confirm(self, raw_string, session=None):
        state = self._db_menu_state(session=session)
        text = (raw_string or "").strip()
        if text.lower() in {"b", "back"}:
            state["mode"] = state.get("prev_mode", "create")
            state.pop("prev_mode", None)
            self._db_menu_prompt_create(session=session)
            return True
        if text == "1":
            self.msg("|yCharacter creation cancelled.|n", session=session)
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)
            return True
        if text == "2":
            state["mode"] = state.get("prev_mode", "create")
            state.pop("prev_mode", None)
            self._db_menu_prompt_create(session=session)
            return True
        self.msg("|rPlease enter 1, 2, or B.|n", session=session)
        self._db_menu_start_create_cancel_confirm(session=session)
        return True

    def _db_menu_validate_create_field(self, field, text):
        if field == "name":
            value = (text or "").strip()
            if not value:
                return None, "Character name cannot be blank."
            if len(value) < 3:
                return None, "Character name must be at least 3 characters."
            if len(value) > 24:
                return None, "Character name must be 24 characters or less."
            return value, None
        if field == "race":
            value = (text or "").strip().lower().replace(" ", "_")
            # Get valid race values from DB_MENU_RACES (which has tuples with descriptions)
            valid_races = {item[0] if isinstance(item, tuple) else item for item in DB_MENU_RACES}
            if value not in valid_races:
                return None, f"Invalid race. Choose from the available options."
            return value, None
        if field == "sex":
            value = (text or "").strip().lower()
            # Get valid sex values from DB_MENU_RACES (handle both tuple and string formats)
            valid_sexes = {item[0] if isinstance(item, tuple) else item for item in SEX_OPTIONS}
            if value not in valid_sexes:
                return None, f"Invalid sex. Choose from the available options."
            return value, None
        return None, "Invalid value."

    def _db_menu_start_delete(self, session=None):
        state = self._db_menu_state(session=session)
        state.clear()
        state["mode"] = "delete_select"
        self._db_menu_render_charlist(session=session, for_delete=True)

    def _db_menu_handle_delete_select(self, raw_string, session=None):
        text = (raw_string or "").strip()
        if text.lower() in {"b", "back"}:
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)
            return True
        char, err = self._db_menu_pick_char_by_input(text)
        if err:
            self.msg(f"|r{err}|n", session=session)
            self._db_menu_render_charlist(session=session, for_delete=True)
            return True
        if char.sessions.all():
            self.msg("|rThat character is currently in use and cannot be deleted.|n", session=session)
            self._db_menu_render_charlist(session=session, for_delete=True)
            return True
        if not char.access(self, "delete"):
            self.msg("|rYou do not have permission to delete that character.|n", session=session)
            self._db_menu_render_charlist(session=session, for_delete=True)
            return True
        state = self._db_menu_state(session=session)
        state.clear()
        state["mode"] = "delete_confirm"
        state["delete_dbref"] = char.dbref
        state["delete_name"] = char.key
        self.msg(
            self._db_menu_box(
                "DELETE CONFIRMATION",
                [
                    f"|rDelete|n |w{char.key}|n",
                    "This cannot be undone.",
                    "",
                    "Type the character name exactly to confirm deletion:",
                    f"|w{char.key}|n",
                    "",
                    "|wB|n = Back",
                ],
            ),
            session=session,
        )
        return True

    def _db_menu_handle_delete_confirm(self, raw_string, session=None):
        state = self._db_menu_state(session=session)
        text = (raw_string or "").strip()
        if text.lower() in {"b", "back"}:
            state.clear()
            state["mode"] = "delete_select"
            self._db_menu_render_charlist(session=session, for_delete=True)
            return True
        expected = state.get("delete_name")
        if text != expected:
            self.msg("|rName mismatch. Deletion cancelled.|n", session=session)
            state.clear()
            state["mode"] = "delete_select"
            self._db_menu_render_charlist(session=session, for_delete=True)
            return True
        target = next((c for c in self._db_menu_get_chars() if c.dbref == state.get("delete_dbref")), None)
        if not target:
            self.msg("|rCharacter no longer exists.|n", session=session)
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)
            return True
        key = target.key
        self.characters.remove(target)
        target.delete()
        self.msg(f"|rCharacter '{key}' was permanently deleted.|n", session=session)
        self._db_menu_reset(session=session)
        self._db_menu_send(session=session)
        return True

    def _db_menu_handle_main(self, raw_string, session=None):
        text = (raw_string or "").strip()
        key = text.lower()
        if not text:
            self._db_menu_send(session=session)
            return True
        if key in {"look", "l", "menu"}:
            self._db_menu_send(session=session)
            return True
        if key in {"1", "enter", "entergame"}:
            state = self._db_menu_state(session=session)
            state.clear()
            state["mode"] = "enter_select"
            self._db_menu_render_charlist(session=session, for_delete=False)
            return True
        if key in {"2", "create", "createcharacter"}:
            self._db_menu_start_create(session=session)
            return True
        if key in {"3", "delete", "deletecharacter"}:
            self._db_menu_start_delete(session=session)
            return True
        if key in {"4", "exit", "quit"}:
            return False  # let normal quit command processing happen via execute_cmd wrapper
        self.msg("|rInvalid menu option.|n Type 1, 2, 3, or 4.", session=session)
        self._db_menu_send(session=session)
        return True

    def _db_menu_handle_enter_select(self, raw_string, session=None):
        text = (raw_string or "").strip()
        if text.lower() in {"b", "back"}:
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)
            return True
        char, err = self._db_menu_pick_char_by_input(text)
        if err:
            self.msg(f"|r{err}|n", session=session)
            self._db_menu_render_charlist(session=session, for_delete=False)
            return True
        # Resolve to the canonical live session object attached to this account.
        session = self._db_menu_canonical_session(session)
        self._db_menu_reset(session=session)
        try:
            # Prefer the built-in IC command path, which handles session binding consistently.
            super().execute_cmd(f"ic {char.key}", session=session)
            if not self.get_puppet(session):
                self.puppet_object(session, char)
            if not self.get_puppet(session):
                raise RuntimeError("Puppeting did not attach to this session.")
            self.db._last_puppet = char
        except Exception as exc:
            self.msg(f"|rYou cannot enter |w{char.key}|n: {exc}|n", session=session)
            self._db_menu_send(session=session)
        return True

    def _db_menu_route_ooc_input(self, raw_string, session=None):
        state = self._db_menu_state(session=session)
        mode = state.get("mode", "main")
        if mode == "main":
            if (raw_string or "").strip() == "4":
                # Explicit menu exit; route to built-in quit command.
                super().execute_cmd("quit", session=session)
                return True
            return self._db_menu_handle_main(raw_string, session=session)
        if mode == "enter_select":
            return self._db_menu_handle_enter_select(raw_string, session=session)
        if mode == "create":
            return self._db_menu_handle_create_input(raw_string, session=session)
        if mode == "create_cancel_confirm":
            return self._db_menu_handle_create_cancel_confirm(raw_string, session=session)
        if mode == "delete_select":
            return self._db_menu_handle_delete_select(raw_string, session=session)
        if mode == "delete_confirm":
            return self._db_menu_handle_delete_confirm(raw_string, session=session)
        self._db_menu_reset(session=session)
        self._db_menu_send(session=session)
        return True

    def at_post_login(self, session=None, **kwargs):
        super().at_post_login(session=session, **kwargs)
        # Force the menu to take over immediately after login and clear the connect screen.
        if session:
            self._db_menu_reset(session=session)
            self._db_menu_send(session=session)

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """
        While OOC, the DBForged menu owns input until the player enters a character.
        Route input to the appropriate menu handler based on mode.
        """
        session = self._db_menu_canonical_session(session)
        # If this specific session is already puppeting, always route to normal IC processing.
        if session and self.get_puppet(session):
            return super().execute_cmd(raw_string, session=session, **kwargs)

        # Check puppet status
        puppets = self.get_all_puppets()
        
        # If we're not puppeting ANY character, we're in OOC state
        if not puppets:
            # Get session if not provided
            if not session:
                sessions = list(self.sessions.all())
                if sessions:
                    session = sessions[0]
            if session:
                # Check menu state to route correctly
                state = self._db_menu_state(session=session)
                mode = state.get("mode", "main")
                
                # If in create mode, route all input to create handler
                if mode == "create":
                    return self._db_menu_route_ooc_input(raw_string, session=session)
                
                # Otherwise, normal routing
                return self._db_menu_route_ooc_input(raw_string, session=session)
        
        # We have puppets (possibly on another session), use normal command processing
        return super().execute_cmd(raw_string, session=session, **kwargs)


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass
