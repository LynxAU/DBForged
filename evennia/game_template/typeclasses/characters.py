"""
DB vertical-slice character typeclass.
"""

from __future__ import annotations

import random
import time

from evennia import search_tag
from evennia.objects.objects import DefaultCharacter

from world.events import emit_entity_delta
from world.power import compute_current_pl
from world.techniques import STARTER_TECHNIQUES

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    Character with PL, combat, status, and transformation support.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.race = self.db.race or "saiyan"
        self.db.sprite_id = self.db.sprite_id or "sprite_player_default"
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
        self.db.tech_mastery = self.db.tech_mastery or {}
        self.db.tech_cooldowns = self.db.tech_cooldowns or {}
        self.db.known_techniques = self.db.known_techniques or list(STARTER_TECHNIQUES)
        self.db.equipped_techniques = self.db.equipped_techniques or list(STARTER_TECHNIQUES[:4])

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        emit_entity_delta(self)

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
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
