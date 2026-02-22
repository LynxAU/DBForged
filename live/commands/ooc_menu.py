"""
DBForged OOC account menu commands.
"""

from __future__ import annotations

import evennia
from evennia.commands.default import account as default_account
from evennia.commands.cmdhandler import CMD_NOMATCH, CMD_NOINPUT
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

    def _route_ic_codex_if_active(self):
        sess = getattr(self, "session", None)
        puppet = getattr(sess, "puppet", None) if sess else None
        if not puppet or not getattr(getattr(puppet, "ndb", None), "info_menu_state", None):
            return False
        try:
            from commands.db_commands import handle_ic_info_menu_input

            return bool(handle_ic_info_menu_input(puppet, (self.raw_string or "").strip()))
        except Exception:
            return False


class CmdDBMainMenu(_DBMenuCommand):
    """
    Show the DBForged OOC main menu.
    """

    key = "menu"
    aliases = ["mainmenu"]

    def func(self):
        if self._route_ic_codex_if_active():
            return
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
        if self._route_ic_codex_if_active():
            return
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        if mode != "main":
            # In submenu mode, route the raw input to the shared menu state machine.
            self.account._db_menu_route_ooc_input(self.raw_string.strip(), session=self.session)
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
        if self._route_ic_codex_if_active():
            return
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        if mode != "main":
            self.account._db_menu_route_ooc_input(self.raw_string.strip(), session=self.session)
            return

        # Start character creation using the canonical account-menu helper (loads defaults/colors).
        self.account._db_menu_start_create(session=self.session)


class CmdDBMenuDeleteCharacter(_DBMenuCommand):
    """
    Menu option 3: delete a character after exact-name confirmation.
    """

    key = "deletecharacter"
    aliases = ["3", "deletechar", "delchar"]

    def func(self):
        if self._route_ic_codex_if_active():
            return
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        if mode != "main":
            self.account._db_menu_route_ooc_input(self.raw_string.strip(), session=self.session)
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
        if self._route_ic_codex_if_active():
            return
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        if mode != "main":
            self.account._db_menu_route_ooc_input(self.raw_string.strip(), session=self.session)
            return

        # Execute quit through the account's sessions
        if self.session:
            self.session.msg("|yGoodbye!|n")
        # Disconnect only this session (prevents nuking multi-session accounts).
        if self.session:
            evennia.SESSION_HANDLER.disconnect(self.session, "Menu exit")
            return
        for sess in self.account.sessions.all():
            evennia.SESSION_HANDLER.disconnect(sess, "Menu exit")


class CmdDBMenuTextInput(_DBMenuCommand):
    """
    Catch-all for text input during menu navigation.
    This handles text that isn't matched as a command and routes it to the
    active OOC submenu state machine.
    """

    key = CMD_NOINPUT  # This is the special key for unmatched commands
    aliases = [CMD_NOMATCH]
    locks = "cmd:all()"
    
    def func(self):
        if self._route_ic_codex_if_active():
            return
        state = self.account._db_menu_state(session=self.session)
        mode = state.get("mode", "main")
        
        if mode != "main":
            raw = self.raw_string.strip()
            if raw:
                self.account._db_menu_route_ooc_input(raw, session=self.session)
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
        if self._route_ic_codex_if_active():
            return
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
