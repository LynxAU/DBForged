from unittest.mock import Mock

import evennia
from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest

from typeclasses.accounts import Account, DB_MENU_SKIN_PALETTES
from typeclasses.characters import Character


class TestDBForgedAccountMenu(EvenniaTest):
    account_typeclass = Account
    character_typeclass = Character

    def setUp(self):
        super().setUp()
        self._msgs = []

        def _capture_msg(*args, **kwargs):
            text = args[0] if args else kwargs.get("text", "")
            self._msgs.append("" if text is None else str(text))

        self.account.msg = Mock(side_effect=_capture_msg)
        # Force OOC state for menu routing tests.
        if self.account.get_puppet(self.session):
            self.account.unpuppet_object(self.session)

    def _last_msg(self):
        for msg in reversed(self._msgs):
            if msg:
                return msg
        return ""

    def _all_msgs(self):
        return "\n".join(self._msgs)

    def _clear_msgs(self):
        self._msgs.clear()
        self.account.msg.reset_mock()

    def _clear_account_characters(self):
        for char in list(self.account.characters):
            self.account.characters.remove(char)
            char.account = None

    def _create_account_character(self, key="Hero"):
        char, errors = self.account.create_character(key=key, ip="127.0.0.1")
        self.assertFalse(errors)
        self.assertIsNotNone(char)
        char.db.chargen_complete = True
        return char

    def _start_create_wizard(self):
        self.account.execute_cmd("2", session=self.session)
        self.assertIn("CHARACTER CREATION", self._all_msgs())

    def test_post_login_lands_on_main_menu(self):
        self.account.at_post_login(session=self.session)
        out = self._all_msgs()
        self.assertIn("DragonballForged", out)
        self.assertIn("1", out)
        self.assertIn("Enter Game", out)
        self.assertIn("Create Character", out)
        self.assertIn("Delete Character", out)
        self.assertIn("Exit", out)

    def test_enter_game_with_no_characters_shows_exact_message_and_returns_menu(self):
        self._clear_account_characters()
        self.account.execute_cmd("1", session=self.session)
        out = self._all_msgs()
        self.assertIn("You have no characters yet!", out)
        self.assertIn("MAIN MENU", out)
        self.assertEqual(self.account._db_menu_state(self.session)["mode"], "main")

    def test_enter_game_select_puppets_ready_character(self):
        self._clear_account_characters()
        char = self._create_account_character("Gohan")
        self._clear_msgs()

        self.account.execute_cmd("1", session=self.session)  # enter game menu
        self.assertIn("ENTER GAME", self._all_msgs())
        self._clear_msgs()

        self.account.execute_cmd("1", session=self.session)  # select character
        puppet = self.account.get_puppet(self.session)
        self.assertIsNotNone(puppet)
        self.assertEqual(puppet.id, char.id)

    def test_create_wizard_numeric_flow_and_back_cancel(self):
        self._start_create_wizard()

        # Step 1 prompt
        self.assertIn("Name: Enter your character name.", self._last_msg())
        self.account.execute_cmd("c", session=self.session)
        self.assertIn("Cancel creation?", self._last_msg())
        self.account.execute_cmd("2", session=self.session)  # no, resume
        state = self.account._db_menu_state(self.session)
        self.assertEqual(state["mode"], "create")
        self.assertEqual(state["step"], 0)

        self.account.execute_cmd("Goku", session=self.session)  # -> race
        self.assertIn("Step 2/7 - Race", self._last_msg())
        self.account.execute_cmd("b", session=self.session)  # back to name
        self.assertIn("Step 1/7 - Name", self._last_msg())

        self.account.execute_cmd("Goku", session=self.session)
        self.account.execute_cmd("1", session=self.session)  # race
        self.account.execute_cmd("1", session=self.session)  # hair
        self.account.execute_cmd("1", session=self.session)  # eye
        self.account.execute_cmd("1", session=self.session)  # skin
        self.account.execute_cmd("1", session=self.session)  # aura -> review
        self.assertIn("Is this correct?", self._last_msg())

    def test_skin_palette_changes_by_race(self):
        self._start_create_wizard()
        self.account.execute_cmd("Piccolo", session=self.session)  # step 1
        self.account.execute_cmd("3", session=self.session)  # Namekian
        self.account.execute_cmd("1", session=self.session)  # hair
        self.account.execute_cmd("1", session=self.session)  # eyes
        out = self._last_msg()
        self.assertIn("Step 5/7 - Skin Color", out)
        for label in DB_MENU_SKIN_PALETTES["namekian"]:
            text = label[1] if isinstance(label, tuple) else label
            self.assertIn(text, out)

    def test_review_confirmation_yes_creates_character_and_no_returns_to_race(self):
        self._clear_account_characters()
        self._start_create_wizard()
        self.account.execute_cmd("Vegeta", session=self.session)
        self.account.execute_cmd("1", session=self.session)  # race
        self.account.execute_cmd("1", session=self.session)  # hair
        self.account.execute_cmd("1", session=self.session)  # eye
        self.account.execute_cmd("1", session=self.session)  # skin
        self.account.execute_cmd("1", session=self.session)  # aura -> review
        self.assertIn("Is this correct?", self._last_msg())

        self.account.execute_cmd("2", session=self.session)  # review no -> race step
        self.assertIn("Step 2/7 - Race", self._last_msg())

        # Finish creation and confirm yes.
        self.account.execute_cmd("1", session=self.session)  # race
        self.account.execute_cmd("1", session=self.session)  # hair
        self.account.execute_cmd("1", session=self.session)  # eye
        self.account.execute_cmd("1", session=self.session)  # skin
        self.account.execute_cmd("1", session=self.session)  # aura -> review
        self.account.execute_cmd("1", session=self.session)  # yes create
        out = self._all_msgs()
        self.assertIn("Character created:", out)
        self.assertIn("ENTER GAME", out)  # returns to character select (preferred)
        self.assertTrue(any(char.key == "Vegeta" for char in self.account.characters))

    def test_delete_requires_exact_name_confirmation_mismatch_never_deletes(self):
        self._clear_account_characters()
        self._create_account_character("Krillin")
        self._clear_msgs()

        self.account.execute_cmd("3", session=self.session)  # delete list
        self.assertIn("DELETE CHARACTER", self._last_msg())
        self.account.execute_cmd("1", session=self.session)  # choose char
        self.assertIn("Type the character name exactly to confirm deletion:", self._last_msg())
        self.account.execute_cmd("krillin", session=self.session)  # mismatch case-sensitive
        out = self._all_msgs()
        self.assertIn("Name mismatch. Deletion cancelled.", out)
        self.assertTrue(any(char.key == "Krillin" for char in self.account.characters))
        self.assertIn("DELETE CHARACTER", out)  # back to delete list

        self._clear_msgs()
        self.account.execute_cmd("1", session=self.session)  # choose again
        self.account.execute_cmd("Krillin", session=self.session)  # exact match
        out = self._all_msgs()
        self.assertIn("permanently deleted", out)
        self.assertFalse(any(char.key == "Krillin" for char in self.account.characters))
        self.assertIn("MAIN MENU", out)

    def test_exit_disconnects(self):
        evennia.SESSION_HANDLER.disconnect.reset_mock()
        self.account.execute_cmd("4", session=self.session)
        self.assertTrue(evennia.SESSION_HANDLER.disconnect.called)
