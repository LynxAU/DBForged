from types import SimpleNamespace
from unittest import TestCase

from world.forms import get_form_tick_drain
from world.quests import accept_quest, get_quest_status, mark_quest_turn_in_ready, turn_in_quest
from world.racials import get_racial_hooks, use_racial


class _DummyChar:
    def __init__(self, **db):
        self.db = SimpleNamespace(**db)
        self._statuses = []

    def spend_ki(self, amount):
        if (self.db.ki_current or 0) < amount:
            return False
        self.db.ki_current -= int(amount)
        return True

    def restore_ki(self, amount):
        self.db.ki_current = min(self.db.ki_max, (self.db.ki_current or 0) + int(amount))
        return self.db.ki_current

    def add_status(self, key, duration, **data):
        self._statuses.append((key, float(duration), dict(data)))


class TestContentSystems(TestCase):
    def test_quest_lifecycle_grants_rewards(self):
        char = _DummyChar(
            quest_state={},
            known_techniques=["ki_blast"],
            unlocked_forms=[],
            lssj_state={},
            story_flags=[],
        )

        ok, _msg, _ = accept_quest(char, "ssj_breakpoint")
        self.assertTrue(ok)
        status = get_quest_status(char, "ssj_breakpoint")
        self.assertTrue(status["accepted"])
        self.assertFalse(status["completed"])

        ok, _msg, _ = mark_quest_turn_in_ready(char, "ssj_breakpoint")
        self.assertTrue(ok)
        status = get_quest_status(char, "ssj_breakpoint")
        self.assertTrue(status["turn_in_ready"])

        ok, _msg, payload = turn_in_quest(char, "ssj_breakpoint", npc_key="goku")
        self.assertTrue(ok)
        self.assertIn("super_saiyan", char.db.unlocked_forms)
        self.assertIn("kame_wave", char.db.known_techniques)
        self.assertTrue(payload["state"]["completed"])

    def test_racial_passive_hooks_and_forms_integration(self):
        char = _DummyChar(
            race="frost_demon",
            racial_traits=["frost_demon_form_discipline", "frost_demon_cruel_precision", "frost_demon_death_glare"],
            racial_cooldowns={},
            ki_current=80,
            ki_max=100,
            hp_current=100,
            hp_max=100,
            form_mastery={"golden_frost": 0},
            active_form="golden_frost",
        )

        hooks = get_racial_hooks(char)
        self.assertGreater(hooks.get("form_drain_reduction", 0), 0)

        drain, _ = get_form_tick_drain(char, "golden_frost")
        # Base golden_frost drain is 9; Frost Demon passive should reduce it.
        self.assertLess(drain, 9)

        ok, msg, _ = use_racial(char, "frost_demon_death_glare", target=None, context={"test": True}, now=100.0)
        self.assertFalse(ok)
        self.assertIn("passive", msg.lower())
