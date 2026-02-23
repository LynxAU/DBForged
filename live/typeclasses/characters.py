"""
DB vertical-slice character typeclass.
"""

from __future__ import annotations

import random
import time

from evennia import search_tag
from evennia.objects.objects import DefaultCharacter

from world.color_utils import colorize
from world.events import emit_entity_delta
from world.power import compute_current_pl
from world.racials import ensure_character_racials
from world.techniques import STARTER_TECHNIQUES

from .objects import ObjectParent

CHARGEN_STEPS = [
    ("hair_style", "Hair style", "Enter a hair style (e.g. spiky, short, ponytail):"),
    ("hair_color", "Hair color", "Enter a hair color (e.g. black, blond, red):"),
    ("eye_color", "Eye color", "Enter an eye color:"),
    ("aura_color", "Aura color", "Enter an aura color:"),
    ("race", "Race", "Choose race:"),
    ("sex", "Sex", "Choose sex [male/female/other]:"),
]

# Descriptive mapping for menu display - maps internal keys to display names
RACE_DISPLAY_NAMES = {
    "saiyan": "Saiyan (Warrior race with exponential growth potential)",
    "human": "Human (Balanced race with diverse abilities)",
    "namekian": "Namekian (Dragon Clan - can create Dragon Balls)",
    "frost_demon": "Frost Demon (Arctic conquerors with lethal cryokinesis)",
    "android": "Android (Mech-organic fusion, limitless potential)",
    "majin": "Majin (Shape-shifting warriors with regeneration)",
    "half_breed": "Half-Breed (Hybrid Saiyan/Human latent power)",
    "biodroid": "Biodroid (Adaptive bio-engineered evolution fighter)",
    "grey": "Grey (Meditative powerhouse akin to Pride Trooper elites)",
    "kai": "Kai (Divine being with superior ki attunement)",
    "truffle": "Truffle/Tuffle (Tech-focused survivors and tactical specialists)",
}

# Race options for character creation
RACE_OPTIONS = {
    "saiyan",
    "human",
    "namekian",
    "frost_demon",
    "android",
    "bio_android",
    "biodroid",
    "majin",
    "half_breed",  # Human/Saiyan hybrid
    "truffle",
    "grey",  # Jiren race
    "kai",
}
SEX_OPTIONS = {"male", "female", "other"}


class Character(ObjectParent, DefaultCharacter):
    """
    Character with PL, combat, status, and transformation support.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.race = self.db.race or "saiyan"
        self.db.sex = self.db.sex or "other"
        self.db.hair_style = self.db.hair_style or "spiky"
        self.db.hair_color = self.db.hair_color or "black"
        self.db.eye_color = self.db.eye_color or "black"
        self.db.skin_color = self.db.skin_color or "light"
        self.db.aura_color = self.db.aura_color or "white"
        self.db.chargen_complete = bool(self.db.chargen_complete)
        self._refresh_sprite_id()
        self.db.base_power = self.db.base_power or 120
        self.db.strength = self.db.strength or 10
        self.db.speed = self.db.speed or 10
        self.db.balance = self.db.balance or 10
        self.db.mastery = self.db.mastery or 10
        self.db.ki_control = self.db.ki_control or 5
        self.db.hp_max = self.db.hp_max or 120
        self.db.hp_current = self.db.hp_current or self.db.hp_max
        self.db.ki_max = self.db.ki_max or 90
        self.db.ki_current = self.db.ki_current or int(self.db.ki_max * 0.75)
        self.db.statuses = self.db.statuses or {}
        self.db.combat_target = None
        self.db.in_combat = False
        self.db.is_charging = False
        self.db.charge_stacks = 0
        self.db.suppressed = False
        self.db.suppression_factor = self.db.suppression_factor or 0.35
        self.db.active_form = None
        self.db.form_mastery = self.db.form_mastery or {}
        self.db.unlocked_forms = self.db.unlocked_forms or []
        self.db.tech_mastery = self.db.tech_mastery or {}
        self.db.tech_cooldowns = self.db.tech_cooldowns or {}
        self.db.known_techniques = self.db.known_techniques or list(STARTER_TECHNIQUES)
        self.db.equipped_techniques = self.db.equipped_techniques or list(STARTER_TECHNIQUES[:4])
        self.db.racial_traits = self.db.racial_traits or []
        self.db.lssj_state = self.db.lssj_state or {}
        self.db.coords = self.db.coords or (0, 0, 0)
        ensure_character_racials(self)

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        self._ensure_profile_defaults()
        emit_entity_delta(self)

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        self._ensure_profile_defaults()
        emit_entity_delta(self)

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """
        Intercept input for explicit modal IC flows (chargen, codex/info menus).
        """
        self._ensure_profile_defaults()
        if self.has_account and getattr(self.ndb, "info_menu_state", None):
            text = (raw_string or "").strip()
            if text.lower() in {"quit", "@quit"}:
                return super().execute_cmd(raw_string, session=session, **kwargs)
            try:
                from commands.db_commands import handle_ic_info_menu_input

                if handle_ic_info_menu_input(self, text):
                    return
            except Exception:
                # Fall through to normal command handling on menu-routing errors.
                pass
        if self.has_account and self._is_ic_chargen_active():
            text = (raw_string or "").strip()
            if text.lower() in {"quit", "@quit"}:
                return super().execute_cmd(raw_string, session=session, **kwargs)
            self._process_chargen_input(text)
            return
        return super().execute_cmd(raw_string, session=session, **kwargs)

    def _ensure_profile_defaults(self):
        changed = False
        defaults = {
            "sex": "other",
            "hair_style": "spiky",
            "hair_color": "black",
            "eye_color": "black",
            "skin_color": "light",
            "aura_color": "white",
        }
        if not self.attributes.has("chargen_complete"):
            # Default to complete; DBForged uses the OOC menu wizard for creation.
            self.db.chargen_complete = True
            changed = True
        if not self.attributes.has("chargen_active"):
            self.db.chargen_active = False
            changed = True
        for key, value in defaults.items():
            if not self.attributes.has(key):
                setattr(self.db, key, value)
                changed = True
        if not self.attributes.has("race"):
            self.db.race = "saiyan"
            changed = True
        if not self.attributes.has("unlocked_forms"):
            self.db.unlocked_forms = []
            changed = True
        if not self.attributes.has("racial_traits"):
            self.db.racial_traits = []
            changed = True
        if not self.attributes.has("lssj_state"):
            self.db.lssj_state = {}
            changed = True
        ensure_character_racials(self)
        if changed or not self.db.sprite_id:
            self._refresh_sprite_id()

    def _refresh_sprite_id(self):
        race = (self.db.race or "humanoid").lower().replace(" ", "_")
        sex = (self.db.sex or "other").lower().replace(" ", "_")
        self.db.sprite_id = f"sprite_{race}_{sex}"

    def _chargen_step_index(self):
        return int(self.db.chargen_step_index or 0)

    def _is_ic_chargen_active(self):
        return bool(self.has_account and not self.db.chargen_complete and self.db.chargen_active)

    def start_chargen(self):
        self.db.chargen_active = True
        self.db.chargen_step_index = self.db.chargen_step_index or 0
        self.msg("|yCharacter creation started.|n Answer the prompts to finish setup.")
        self.msg("|xType `cancel` to keep defaults and finish quickly.|n")
        self._show_chargen_prompt()

    def _show_chargen_prompt(self):
        idx = self._chargen_step_index()
        if idx >= len(CHARGEN_STEPS):
            self.finish_chargen()
            return
        _, label, prompt = CHARGEN_STEPS[idx]
        current_key = CHARGEN_STEPS[idx][0]
        current_val = getattr(self.db, current_key, "")
        preview = colorize(current_val) if "color" in current_key else current_val
        self.msg(f"|w{label}:|n {prompt} |x[current:|n {preview}|x]|n")

    def _normalize_chargen_value(self, key, value):
        value = (value or "").strip()
        if not value:
            return None, "Please enter a value."
        if key in {"hair_style", "hair_color", "eye_color", "aura_color"}:
            cleaned = value.lower().replace("-", "_").replace(" ", "_")
            if len(cleaned) > 24:
                return None, "Keep it under 24 characters."
            return cleaned, None
        if key == "race":
            cleaned = value.lower().replace(" ", "_")
            if cleaned not in RACE_OPTIONS:
                return None, f"Invalid race. Choose: {', '.join(sorted(RACE_OPTIONS))}"
            return cleaned, None
        if key == "sex":
            cleaned = value.lower()
            if cleaned not in SEX_OPTIONS:
                return None, f"Invalid sex. Choose: {', '.join(sorted(SEX_OPTIONS))}"
            return cleaned, None
        return value, None

    def _process_chargen_input(self, text):
        if not text:
            self._show_chargen_prompt()
            return
        if text.lower() == "cancel":
            self.finish_chargen()
            return
        idx = self._chargen_step_index()
        if idx >= len(CHARGEN_STEPS):
            self.finish_chargen()
            return
        key, label, _prompt = CHARGEN_STEPS[idx]
        value, error = self._normalize_chargen_value(key, text)
        if error:
            self.msg(f"|r{error}|n")
            self._show_chargen_prompt()
            return
        setattr(self.db, key, value)
        self.db.chargen_step_index = idx + 1
        shown = colorize(value) if "color" in key else value
        self.msg(f"|gSet {label} to {shown}|g.|n")
        self._show_chargen_prompt()

    def finish_chargen(self):
        self.db.chargen_complete = True
        self.db.chargen_active = False
        self.db.chargen_step_index = 0
        self._refresh_sprite_id()
        self.msg(
            f"|gCharacter setup complete.|n {self.db.race.title()} / {self.db.sex.title()} / "
            f"hair {self.db.hair_style} ({colorize(self.db.hair_color)}), "
            f"eyes {colorize(self.db.eye_color)}, aura {colorize(self.db.aura_color)}."
        )
        emit_entity_delta(self)

    def get_current_pl(self):
        return compute_current_pl(self)

    def get_stats(self):
        pl, breakdown = self.get_current_pl()
        return {
            "hp_current": self.db.hp_current,
            "hp_max": self.db.hp_max,
            "ki_current": self.db.ki_current,
            "ki_max": self.db.ki_max,
            "power_level": pl,
            "displayed_power_level": breakdown["displayed_pl"],
            "base_power": self.db.base_power,
            "strength": self.db.strength,
            "speed": self.db.speed,
            "balance": self.db.balance,
            "mastery": self.db.mastery,
            "ki_control": self.db.ki_control,
        }

    def clean_statuses(self):
        now = time.time()
        statuses = dict(self.db.statuses or {})
        dirty = False
        for key, data in list(statuses.items()):
            until = data.get("until")
            if until and until <= now:
                statuses.pop(key, None)
                dirty = True
        if dirty:
            self.db.statuses = statuses
        return statuses

    def has_status(self, key):
        return key in self.clean_statuses()

    def add_status(self, key, duration, **data):
        statuses = self.clean_statuses()
        statuses[key] = {"until": time.time() + float(duration), "data": data}
        self.db.statuses = statuses

    def remove_status(self, key):
        statuses = self.clean_statuses()
        if key in statuses:
            statuses.pop(key, None)
            self.db.statuses = statuses

    def get_status_data(self, key, default=None):
        return self.clean_statuses().get(key, {}).get("data", default)

    def is_in_combat(self):
        return bool(self.db.in_combat and self.db.combat_target)

    def spend_ki(self, amount):
        amount = int(max(0, amount))
        if (self.db.ki_current or 0) < amount:
            return False
        self.db.ki_current = max(0, (self.db.ki_current or 0) - amount)
        emit_entity_delta(self)
        return True

    def restore_ki(self, amount):
        amount = int(max(0, amount))
        self.db.ki_current = min(self.db.ki_max, (self.db.ki_current or 0) + amount)
        emit_entity_delta(self)
        return self.db.ki_current

    def _get_safe_room(self):
        safe_rooms = search_tag("safe_room", category="zone")
        if self.location and self.location in safe_rooms:
            return self.location
        return safe_rooms[0] if safe_rooms else self.home

    def apply_damage(self, amount, source=None, kind="attack"):
        amount = int(max(0, amount))
        if self.has_status("guard"):
            reduction = self.get_status_data("guard", {}).get("reduction", 0.45)
            amount = max(1, int(amount * (1.0 - reduction)))
        if self.has_status("afterimage") and random.random() < 0.5:
            self.remove_status("afterimage")
            if self.location:
                self.location.msg_contents(f"{self.key} blurs with an afterimage and avoids the hit!")
            return 0
        self.db.hp_current = max(0, (self.db.hp_current or 0) - amount)
        if self.db.hp_current <= 0:
            self.handle_defeat(source=source, kind=kind)
        emit_entity_delta(self)
        return amount

    def handle_defeat(self, source=None, kind="attack"):
        from world.combat import disengage, stop_charging

        stop_charging(self, interrupted=True)
        disengage(self)
        self.db.active_form = None
        self.add_status("bruised", 300, pl_penalty=0.92)
        self.db.hp_current = max(1, int(self.db.hp_max * 0.55))
        self.db.ki_current = max(1, int(self.db.ki_max * 0.40))
        safe_room = self._get_safe_room()
        if safe_room:
            self.move_to(safe_room, quiet=True)
        if source:
            self.msg(f"|rYou were defeated by {source.key}. You wake up bruised at a safe point.|n")
        else:
            self.msg("|rYou were defeated. You wake up bruised at a safe point.|n")
        emit_entity_delta(self)
