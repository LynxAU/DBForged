"""
Combat commands module.

Contains all combat-related commands: attack, flee, target, charge, guard, counter.
"""

from __future__ import annotations

import time

from commands.command import Command
from world.combat import engage, disengage, register_beam, start_charging, stop_charging
from world.events import emit_combat_event, emit_entity_delta, emit_vfx
from world.power import pl_gap_effect
from world.techniques import TECHNIQUES, execute_technique_stub, get_technique, is_beam


def _search_target(caller, text):
    return caller.search(text, location=caller.location)


def _is_npc(obj):
    return bool(obj.db.is_npc)


def _interrupt_target(target, actor):
    interrupted = False
    if target.db.is_charging:
        stop_charging(target, interrupted=True)
        interrupted = True
    return interrupted


def _tech_mastery_level(caller, tech_key):
    return (caller.db.tech_mastery or {}).get(tech_key, 0)


def _set_cooldown(caller, tech_key, cooldown):
    cds = dict(caller.db.tech_cooldowns or {})
    cds[tech_key] = time.time() + cooldown
    caller.db.tech_cooldowns = cds


def _cooldown_remaining(caller, tech_key):
    return max(0.0, (caller.db.tech_cooldowns or {}).get(tech_key, 0) - time.time())


def _gain_tech_mastery(caller, tech_key, amount=1):
    mastery = dict(caller.db.tech_mastery or {})
    mastery[tech_key] = mastery.get(tech_key, 0) + amount
    caller.db.tech_mastery = mastery


class CmdAttack(Command):
    """
    Attack a target in combat.

    Usage:
      attack [technique]

    Attacks your current combat target. If you specify a technique name,
    attempts to use that technique.
    """
    key = "attack"
    aliases = ["a", "hit"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # If no args, use basic engage
        if not self.args:
            # Legacy behavior: just engage target
            target = _search_target(caller, self.args.strip() if self.args else "")
            if not self.args:
                caller.msg("Usage: attack <target>")
                return
            
            target = _search_target(caller, self.args.strip())
            if not target or target == caller:
                return
            if not hasattr(target, "db") or target.db.hp_current is None:
                caller.msg("You cannot attack that.")
                return
            caller.db.in_combat = True
            target.db.in_combat = True
            engage(caller, target)
            caller.location.msg_contents(f"{caller.key} engages {target.key} in combat!")
            emit_combat_event(caller.location, caller, target, {"subtype": "engage"})
            return

        # Technique-based attack
        target = caller.ndb.combat_target or caller.db.combat_target

        if not target:
            caller.msg("You have no target set. Use 'target <name>' first.")
            return

        target = caller.search(target, location=caller.location)
        if not target:
            caller.msg("Your target is no longer here.")
            caller.db.combat_target = None
            return

        # Get target's current PL
        target_pl = getattr(target, "get_current_pl", lambda: 0)()
        my_pl = getattr(caller, "get_current_pl", lambda: 0)()

        # Use technique if specified
        tech_name = self.args.strip().lower()
        technique = get_technique(tech_name, caller)
        if not technique:
            caller.msg(f"You don't know a technique called '{tech_name}'.")
            return
        if _cooldown_remaining(caller, tech_name) > 0:
            caller.msg(f"{technique['name']} is on cooldown.")
            return

        cd = technique.get("cooldown", 3)
        _set_cooldown(caller, tech_name, cd)

        damage = technique.get("damage", 0)
        ki_cost = technique.get("ki_cost", 0)
        stamina_cost = technique.get("stamina_cost", 0)

        # ═══════════════════════════════════════════════════════════════════════
        # COMBO DAMAGE BONUS - Chain attacks for increased damage!
        # ═══════════════════════════════════════════════════════════════════════
        combo_count = caller.db.combo_count or 0
        if combo_count > 0:
            combo_bonus = min(0.5, combo_count * 0.05)  # Up to 50% bonus at 10+ combo
            damage = int(damage * (1 + combo_bonus))
            if combo_count >= 5:
                caller.msg(f"{{m>>> COMBO x{combo_count}! +{int(combo_bonus*100)}% damage!|{{x")
        
        # ═══════════════════════════════════════════════════════════════════════
        # CHARGE STACK DAMAGE BONUS - Charged attacks hit harder!
        # ═══════════════════════════════════════════════════════════════════════
        charge_stacks = caller.db.charge_stacks or 0
        is_charged_attack = charge_stacks >= 3
        if charge_stacks >= 3:
            charge_bonus = 0.25 + (charge_stacks * 0.1)  # 25% at 3 stacks, up to 85% at 9
            damage = int(damage * (1 + charge_bonus))
            
            # ULTIMATE CHARGE at max stacks!
            if charge_stacks >= 9:
                caller.msg(f"{{m!!! ULTIMATE CHARGE ATTACK! +{int(charge_bonus*100)}% damage! !!!|{{x")
            elif charge_stacks >= 7:
                caller.msg(f"{{m★ POWER CHARGE x{charge_stacks}! +{int(charge_bonus*100)}% damage!★|{{x")
            else:
                caller.msg(f"{{cCharged attack! +{int(charge_bonus*100)}% damage!|{{x")
        
        # Reset charge stacks after using them (unless it's a charge tech)
        if charge_stacks >= 3 and technique.get("type") != "charge":
            caller.db.charge_stacks = 0
        
        ki = getattr(caller, "db", {}).get("ki_current", 0)
        if ki < ki_cost:
            caller.msg(f"Not enough Ki. Need {ki_cost}.")
            return

        caller.db.ki_current = max(0, ki - ki_cost)

        if technique.get("type") == "beam":
            register_beam(caller, target, technique)
        else:
            damage += pl_gap_effect(my_pl, target_pl)

            target.db.hp_current = max(0, (target.db.hp_current or 0) - damage)
            
            # Increment combo counter!
            caller.db.combo_count = (caller.db.combo_count or 0) + 1
            caller.db.last_combo_hit = time.time()
            
            _interrupt_target(target, caller)
            _gain_tech_mastery(caller, tech_name)

            if target.db.hp_current <= 0:
                if hasattr(target, "handle_defeat"):
                    target.handle_defeat(caller, "attack")
                emit_combat_event(caller, "defeat", {"target": target.key})
                
                # Check for Roshi's sparring test quest
                target_key = target.key.lower() if target.key else ""
                if "dummy" in target_key or "training" in target_key:
                    from world.quests import get_quest_status, mark_quest_turn_in_ready
                    status = get_quest_status(caller, "roshi_sparring_test")
                    if status.get("accepted") and not status.get("completed"):
                        ok, msg = mark_quest_turn_in_ready(caller, "roshi_sparring_test")
                        if ok:
                            caller.msg("{{g★ Quest complete: You defeated the training dummy! Return to Master Roshi!{{x")
            else:
                emit_combat_event(caller, "attack", {
                    "target": target.key,
                    "damage": damage,
                })

        caller.msg(f"You use {technique['name']} on {target.key}!")

        emit_entity_delta(caller)
        emit_entity_delta(target)


class CmdFlee(Command):
    """
    Attempt to flee from combat.

    Usage:
      flee

    Attempts to disengage from combat. Success depends on your
    speed relative to your target.
    """
    key = "flee"
    aliases = ["run"]

    def func(self):
        caller = self.caller

        if not caller.db.combat_target:
            caller.msg("You're not in combat.")
            return

        target_id = caller.db.combat_target
        target = caller.search(target_id, location=caller.location)

        if not target:
            caller.msg("Your target is already gone.")
            caller.db.combat_target = None
            return

        my_pl = getattr(caller, "get_current_pl", lambda: 0)()
        target_pl = getattr(target, "get_current_pl", lambda: 0)()

        flee_chance = 0.5
        if my_pl > target_pl:
            flee_chance = min(0.9, 0.5 + (my_pl - target_pl) / target_pl * 0.3)
        elif target_pl > my_pl:
            flee_chance = max(0.1, 0.5 - (target_pl - my_pl) / my_pl * 0.3)

        import random
        if random.random() < flee_chance:
            disengage(caller)
            caller.msg("You successfully fled from combat!")
            emit_combat_event(caller, "flee_success", {})
        else:
            caller.msg("You failed to flee!")
            emit_combat_event(caller, "flee_fail", {})


class CmdTarget(Command):
    """
    Set your combat target.

    Usage:
      target <name>

    Sets the target you'll attack in combat. Must be in the same room.
    """
    key = "target"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: target <name>")
            return

        target_name = self.args.strip()
        target = _search_target(caller, target_name)

        if not target:
            caller.msg(f"Couldn't find '{target_name}' here.")
            return

        if target == caller:
            caller.msg("You can't target yourself.")
            return

        # Security: Validate target is in same room
        if target.location != caller.location:
            caller.msg("You can only target someone in your current location.")
            return

        # Validate target is a valid combatant
        if not hasattr(target, "db") or target.db.hp_current is None:
            caller.msg("You cannot attack that.")
            return

        caller.db.combat_target = target.id
        caller.msg(f"Target set to {target.key}.")
        if hasattr(target, "get_current_pl"):
            emit_entity_delta(target, recipients=[caller])


class CmdCharge(Command):
    """
    Begin charging ki.

    Usage:
      charge [form]

    Charges ki to power up. Some races charge faster. You can
    optionally specify a transformation to charge toward.
    """
    key = "charge"
    aliases = ["chargeup"]

    def func(self):
        caller = self.caller

        if caller.db.is_charging:
            caller.msg("You're already charging!")
            return

        if caller.db.active_form:
            caller.msg("You're already transformed!")
            return

        start_charging(caller)
        caller.msg("You begin charging your ki...")

        emit_combat_event(caller, "charge_start", {})
        emit_entity_delta(caller)


class CmdGuard(Command):
    """
    Assume a defensive stance.

    Usage:
      guard

    Reduces damage taken until you attack or are interrupted.
    """
    key = "guard"

    def func(self):
        caller = self.caller

        if caller.db.is_charging:
            stop_charging(caller, interrupted=True)

        caller.db.is_guarding = True
        caller.msg("You assume a defensive stance!")
        emit_combat_event(caller, "guard", {})


class CmdCounter(Command):
    """
    Attempt to counter an attack.

    Usage:
      counter

    Enter counter stance. If attacked while countering, you may
    automatically counterattack with increased damage.
    """
    key = "counter"

    def func(self):
        caller = self.caller

        if caller.db.is_charging:
            stop_charging(caller, interrupted=True)

        caller.db.is_countering = True
        caller.msg("You ready yourself to counter!")
        emit_combat_event(caller, "counter", {})


# Export all combat commands
__all__ = [
    "CmdAttack",
    "CmdFlee",
    "CmdTarget",
    "CmdCharge",
    "CmdGuard",
    "CmdCounter",
]
