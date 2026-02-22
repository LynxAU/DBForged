"""
DBForged OOC account menu commands.
"""

from __future__ import annotations

from evennia.commands.default import account as default_account
from evennia.commands.cmdhandler import CMD_NOMATCH, CMD_NOINPUT
from evennia.utils import logger
from evennia.utils.evmenu import get_input
from evennia.utils.utils import make_iter

from typeclasses.characters import RACE_OPTIONS, SEX_OPTIONS, RACE_DISPLAY_NAMES


def _iter_account_characters(account):
    return [char for char in make_iter(account.characters) if char]


def _quote_name(name):
    text = str(name)
    return f"\"{text}\"" if " " in text else text


def _resolve_character(account, raw_value):
    chars = _iter_account_characters(account)
    if not chars:
        return None, "You have no characters yet!"

    query = (raw_value or "").strip()
    if not query:
        return None, "Choose a character number or name."

    if query.isdigit():
        index = int(query)
        if 1 <= index <= len(chars):
            return chars[index - 1], None
        return None, "That character number does not exist."

    exact = [char for char in chars if char.key.lower() == query.lower()]
    if len(exact) == 1:
        return exact[0], None
    if len(exact) > 1:
        return None, "Multiple characters match that name. Use the number instead."

    partial = [char for char in chars if char.key.lower().startswith(query.lower())]
    if len(partial) == 1:
        return partial[0], None
    if len(partial) > 1:
        return None, "Multiple characters match that text. Use the number instead."

    return None, "No matching character found."


def _show_character_list(cmd, mode_label):
    account = cmd.account
    chars = _iter_account_characters(account)
    if not chars:
        cmd.msg("|rYou have no characters yet!|n")
        return

    lines = [f"|y{mode_label}|n", ""]
    for idx, char in enumerate(chars, start=1):
        status = "|Yin creation|n" if not getattr(char.db, "chargen_complete", False) else "|Gready|n"
        lines.append(f" |c{idx}|n - |w{char.key}|n ({status})")
    lines.append("")
    lines.append(f"Type |w{cmd.cmdstring} <number>|n or |w{cmd.cmdstring} <name>|n.")
    cmd.msg("\n".join(lines))


def _normalize_name(value):
    name = (value or "").strip()
    if not name:
        return None, "Character name cannot be blank."
    if len(name) < 3:
        return None, "Character name must be at least 3 characters."
    if len(name) > 24:
        return None, "Character name must be 24 characters or less."
    return name, None


def _normalize_choice(value, valid, label):
    cleaned = (value or "").strip().lower().replace(" ", "_")
    if not cleaned:
        return None, f"{label} cannot be blank."
    # Direct match
    if cleaned in valid:
        return cleaned, None
    # For race, also check if input matches part of display name
    if label == "race":
        for race_key in RACE_DISPLAY_NAMES:
            display_name = RACE_DISPLAY_NAMES[race_key].lower()
            # Check if input is contained in display name or vice versa
            if (cleaned in race_key or race_key in cleaned or 
                cleaned in display_name or display_name.startswith(cleaned)):
                return race_key, None
    if cleaned not in valid:
        return None, f"Invalid {label}. Choose: {', '.join(sorted(valid))}"
    return cleaned, None


def _normalize_short_text(value, label):
    cleaned = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not cleaned:
        return None, f"{label} cannot be blank."
    if len(cleaned) > 24:
        return None, f"{label} must be 24 characters or less."
    return cleaned, None


def _format_race_options():
    """Format race options for display in prompts."""
    lines = []
    for race_key in sorted(RACE_DISPLAY_NAMES.keys()):
        display = RACE_DISPLAY_NAMES[race_key]
        lines.append(f"  |c{race_key}|n - {display}")
    return "\n".join(lines)


class _DBMenuCommand(default_account.COMMAND_DEFAULT_CLASS):
    account_caller = True
    locks = "cmd:is_ooc()"
    help_category = "General"


class CmdDBMainMenu(_DBMenuCommand):
    """
    Show the DBForged OOC main menu.
    """

    key = "menu"
    aliases = ["mainmenu"]

    def func(self):
        # Use the accounts.py menu system
        self.account._db_menu_reset(session=self.session)
        self.account._db_menu_send(session=self.session)


class CmdDBMenuEnterGame(_DBMenuCommand):
    """
    Menu option 1: list/select a character and enter the game.
    """

    key = "entergame"
    aliases = ["1", "play", "enter"]

    def func(self):
        # Check if in create mode - if so, don't handle this command
        state = self.account._db_menu_state(session=self.session)
        if state.get("mode") == "create":
            # In create mode - route to create input handler instead
            self.account._db_menu_handle_create_input(self.raw_string.strip(), session=self.session)
            return
        
        # Use the accounts.py menu system for character selection
        state.clear()
        state["mode"] = "enter_select"
        self.account._db_menu_render_charlist(session=self.session, for_delete=False)


class CmdDBMenuCreateCharacter(_DBMenuCommand):
    """
    Menu option 2: guided, colored character creation wizard.
    """

    key = "createcharacter"
    aliases = ["2", "createchar", "newchar"]

    def func(self):
        # Check if already in create mode - if so, route to create input handler
        state = self.account._db_menu_state(session=self.session)
        if state.get("mode") == "create":
            # Already in create mode - route input to create handler
            self.account._db_menu_handle_create_input(self.raw_string.strip(), session=self.session)
            return
        
        # Start character creation
        state.clear()
        state["mode"] = "create"
        state["step"] = 0
        state["data"] = {}
        self.account._db_menu_prompt_create(session=self.session)


class CmdDBMenuDeleteCharacter(_DBMenuCommand):
    """
    Menu option 3: delete a character after exact-name confirmation.
    """

    key = "deletecharacter"
    aliases = ["3", "deletechar", "delchar"]

    def func(self):
        # Check if in create mode - if so, route to create input handler
        state = self.account._db_menu_state(session=self.session)
        if state.get("mode") == "create":
            self.account._db_menu_handle_create_input(self.raw_string.strip(), session=self.session)
            return
        
        # Normal delete character flow
        self.account._db_menu_start_delete(session=self.session)


class CmdDBMenuExit(_DBMenuCommand):
    """
    Menu option 4: quit.
    """

    key = "exit"
    aliases = ["4", "quit", "q"]

    def func(self):
        # Check if in create mode - if so, route to create input handler
        state = self.account._db_menu_state(session=self.session)
        if state.get("mode") == "create":
            self.account._db_menu_handle_create_input(self.raw_string.strip(), session=self.session)
            return
        
        # Execute quit through the account's sessions
        if self.session:
            self.session.msg("|yGoodbye!|n")
        # Trigger the disconnect
        from evennia.server.models import Session
        for sess in self.account.sessions.all():
            sess.disconnect()


class CmdDBMenuTextInput(_DBMenuCommand):
    """
    Catch-all for text input during menu navigation.
    This handles any text that isn't a known command (using CMD_NOMATCH).
    Only active when in "create" mode - routes to create input handler.
    """

    key = CMD_NOINPUT  # This is the special key for unmatched commands
    aliases = [CMD_NOMATCH]
    locks = "cmd:all()"
    
    def func(self):
        # Only handle input if in create mode
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        
        if mode == "create":
            # Route to create input handler
            raw = self.raw_string.strip()
            if raw:
                self.account._db_menu_handle_create_input(raw, session=self.session)
        else:
            # For other modes, just show invalid option
            self.msg("|rInvalid menu option.|n Type 1, 2, 3, or 4.", session=self.session)


class CmdDBMenuBack(_DBMenuCommand):
    """
    Go back to previous menu. Used in sub-menus.
    """

    key = "back"
    aliases = ["b"]

    def func(self):
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        
        if mode == "enter_select":
            # Go back to main menu
            self.account._db_menu_reset(session=self.session)
            self.account._db_menu_send(session=self.session)
        elif mode == "create":
            # Route to create input handler for back navigation within character creation
            self.account._db_menu_handle_create_input("back", session=self.session)
        elif mode == "create_cancel_confirm":
            # Cancel the cancel and go back to creation
            state["mode"] = "create"
            self.account._db_menu_prompt_create(session=self.session)
        elif mode == "delete_select":
            # Go back to main menu
            self.account._db_menu_reset(session=self.session)
            self.account._db_menu_send(session=self.session)
        elif mode == "delete_confirm":
            # Go back to delete selection
            state.clear()
            state["mode"] = "delete_select"
            self.account._db_menu_render_charlist(session=self.session, for_delete=True)
        else:
            # Any other mode, go to main menu
            self.account._db_menu_reset(session=self.session)
            self.account._db_menu_send(session=self.session)
