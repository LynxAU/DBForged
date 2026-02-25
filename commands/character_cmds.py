"""
Character commands module.

Contains character-related commands: stats, profile, transform, tech, forms, racials, fly, scan, sense, etc.
"""

from __future__ import annotations

import time

from commands.command import Command
from world.events import emit_entity_delta, emit_vfx
from world.forms import FORMS, activate_form, deactivate_form, get_form, list_forms_for_race
from world.lssj import escalate_lssj, get_lssj_ui_state, train_lssj_control
from world.power import pl_gap_effect
from world.racials import (
    RACIALS,
    get_character_racials,
    get_racial,
    get_racial_hook_value,
    use_racial,
)
from world.techniques import TECHNIQUES, execute_technique_stub, get_technique, is_beam
from world.color_utils import aura_phrase, colorize


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


def _boxed_ui(title, lines, width=70):
    inner = max(20, width - 2)
    top = "┌" + ("─" * inner) + "┐"
    bottom = "└" + ("─" * inner) + "┘"
    title_text = f" {title} "
    if len(title_text) <= inner:
        left = (inner - len(title_text)) // 2
        right = inner - len(title_text) - left
        title_line = "│" + (" " * left) + title_text + (" " * right) + "│"
    else:
        title_line = "│" + title_text[:inner] + "│"

    content = [top, title_line]
    for line in lines:
        if len(line) > inner:
            line = line[:inner - 3] + "..."
        content.append("│" + line.ljust(inner) + "│")
    content.append(bottom)
    return "\n".join(content)


class CmdDBStats(Command):
    """
    Display character statistics.

    Usage:
      +stats

    Shows your current Power Level, attributes, HP, Ki, and other stats.
    """
    key = "+stats"

    def func(self):
        caller = self.caller

        pl = getattr(caller, "get_current_pl", lambda: 0)()
        base_pl = caller.db.base_pl or 0

        hp_max = caller.db.hp_max or 100
        hp_current = caller.db.hp_current or hp_max
        ki_max = caller.db.ki_max or 100
        ki_current = caller.db.ki_current or ki_max
        stamina_max = caller.db.stamina_max or 50
        stamina_current = caller.db.stamina_current or stamina_max

        strength = caller.db.strength or 10
        speed = caller.db.speed or 10
        durability = caller.db.durability or 10
        ki_power = caller.db.ki_power or 10

        race = caller.db.race or "Human"
        gender = caller.db.gender or "N/A"
        age = caller.db.age or 18

        active_form = caller.db.active_form
        form_info = ""
        if active_form:
            form = get_form(active_form, race)
            if form:
                form_info = f" | Form: {form.get('name', active_form)}"

        lines = [
            f"Character: {caller.key}",
            f"Race: {race} | Gender: {gender} | Age: {age}{form_info}",
            f"",
            f"Base PL: {base_pl:,} | Current PL: {pl:,}",
            f"STR: {strength} | SPD: {speed} | DUR: {durability} | KI: {ki_power}",
            f"HP: {hp_current:,}/{hp_max:,} ({hp_current * 100 // hp_max}%)",
            f"Ki: {ki_current:,}/{ki_max:,} ({ki_current * 100 // ki_max}%)",
            f"Stamina: {stamina_current}/{stamina_max}",
        ]

        if caller.db.zenkai_count:
            zenkai = caller.db.zenkai_count
            lines.append(f"Zenkai Boosts: {zenkai}")

        caller.msg(_boxed_ui("CHARACTER STATS", lines))


class CmdPlayerProfile(Command):
    """
    View player profile.

    Usage:
      player [player name]

    View your own or another player's profile.
    """
    key = "player"

    def func(self):
        caller = self.caller

        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        else:
            target = caller

        profile_lines = [f"=== {target.key} ==="]

        race = target.db.race or "Unknown"
        pl = getattr(target, "get_current_pl", lambda: 0)()
        base_pl = target.db.base_pl or 0

        profile_lines.append(f"Race: {race}")
        profile_lines.append(f"Base PL: {base_pl:,} | Combat PL: {pl:,}")

        if target.db.active_form:
            form = get_form(target.db.active_form, race)
            if form:
                profile_lines.append(f"Form: {form.get('name', target.db.active_form)}")

        if target.db.combat_wins is not None:
            profile_lines.append(f"Wins: {target.db.combat_wins}")
        if target.db.combat_losses is not None:
            profile_lines.append(f"Losses: {target.db.combat_losses}")

        guild = target.db.guild
        if guild:
            profile_lines.append(f"Guild: {guild}")

        caller.msg("\n".join(profile_lines))


class CmdTransform(Command):
    """
    Transform into a higher power form.

    Usage:
      transform <form>

    Transform into a more powerful version of yourself. Each form
    has different power multipliers and drawbacks.
    """
    key = "transform"

    def func(self):
        caller = self.caller
        race = caller.db.race or "Human"

        if not self.args:
            caller.msg("Usage: transform <form_name>")
            return

        form_key = self.args.strip().lower()
        form = get_form(form_key, race)

        if not form:
            caller.msg(f"Unknown form '{form_key}'. Use 'forms' to see available forms.")
            return

        result = activate_form(caller, form_key)
        if result.get("success"):
            caller.msg(f"Transforming into {form['name']}!")
            emit_entity_delta(caller)
            emit_vfx(caller.location, caller, "transform", {
                "form": form['name'],
                "duration": 2,
            })
        else:
            caller.msg(result.get("reason", "Transformation failed."))


class CmdTech(Command):
    """
    Use a technique.

    Usage:
      tech <technique name>

    Execute a technique you have learned. Techniques have various
    effects and costs.
    """
    key = "tech"

    def func(self):
        caller = self.caller
        race = caller.db.race or "Human"

        if not self.args:
            caller.msg("Usage: tech <technique_name>")
            return

        tech_key = self.args.strip().lower()
        technique = get_technique(tech_key, caller)

        if not technique:
            caller.msg(f"You don't know '{tech_key}'. Use 'listtech' to see your techniques.")
            return

        cd = _cooldown_remaining(caller, tech_key)
        if cd > 0:
            caller.msg(f"{technique['name']} is on cooldown ({cd:.1f}s remaining).")
            return

        ki_cost = technique.get("ki_cost", 0)
        ki = caller.db.ki_current or 0
        if ki < ki_cost:
            caller.msg(f"Not enough Ki. Need {ki_cost}, have {ki}.")
            return

        stamina_cost = technique.get("stamina_cost", 0)
        stamina = caller.db.stamina_current or 0
        if stamina < stamina_cost:
            caller.msg(f"Not enough Stamina. Need {stamina_cost}, have {stamina}.")
            return

        caller.db.ki_current = max(0, ki - ki_cost)
        caller.db.stamina_current = max(0, stamina - stamina_cost)

        cooldown = technique.get("cooldown", 3)
        _set_cooldown(caller, tech_key, cooldown)

        target_id = caller.db.combat_target
        if target_id:
            target = caller.search(target_id, location=caller.location)
        else:
            target = None

        if technique.get("type") == "beam" and target:
            from world.combat import register_beam
            register_beam(caller, target, technique)
            caller.msg(f"You fire a {technique['name']} at {target.key}!")
        elif technique.get("type") == "self" or not target:
            caller.msg(f"You use {technique['name']}!")
        else:
            caller.msg(f"You use {technique['name']} on {target.key}!")

        _gain_tech_mastery(caller, tech_key)
        emit_entity_delta(caller)


class CmdEquipTech(Command):
    """
    Equip a technique to a slot.

    Usage:
      equiptech <technique> <slot>

    Equip a technique you know to a quick-access slot (1-5).
    """
    key = "equiptech"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: equiptech <technique_name> <slot>")
            return

        parts = self.args.strip().split()
        if len(parts) != 2:
            caller.msg("Usage: equiptech <technique_name> <slot>")
            return

        tech_name = parts[0].lower()
        slot = parts[1]

        technique = get_technique(tech_name, caller)
        if not technique:
            caller.msg(f"You don't know '{tech_name}'.")
            return

        try:
            slot_num = int(slot)
            if slot_num < 1 or slot_num > 5:
                raise ValueError()
        except ValueError:
            caller.msg("Slot must be a number between 1 and 5.")
            return

        equipped = dict(caller.db.equipped_techs or {})
        equipped[str(slot_num)] = tech_name
        caller.db.equipped_techs = equipped

        caller.msg(f"Equipped {technique['name']} to slot {slot_num}.")


class CmdListTech(Command):
    """
    List your techniques.

    Usage:
      listtech

    Shows all techniques you have learned.
    """
    key = "listtech"

    def func(self):
        caller = self.caller
        known = caller.db.known_techniques or []

        if not known:
            caller.msg("You haven't learned any techniques yet.")
            return

        lines = ["=== Your Techniques ==="]
        for tech_key in known:
            tech = TECHNIQUES.get(tech_key)
            if not tech:
                continue

            mastery = _tech_mastery_level(caller, tech_key)
            cd = _cooldown_remaining(caller, tech_key)
            cd_str = f" ({cd:.1f}s)" if cd > 0 else ""
            mastery_str = f" [Mastery {mastery}]" if mastery > 0 else ""

            lines.append(f"  {tech['name']}{cd_str}{mastery_str}")
            lines.append(f"    {tech.get('description', 'No description')[:50]}...")

        caller.msg("\n".join(lines))


class CmdForms(Command):
    """
    List available transformations.

    Usage:
      forms [race]

    Shows transformation forms available for your race, or
    another race if specified.
    """
    key = "forms"

    def func(self):
        caller = self.caller
        race = self.args.strip() if self.args else (caller.db.race or "Human")

        forms = list_forms_for_race(race)

        if not forms:
            caller.msg(f"No forms available for {race}.")
            return

        lines = [f"=== {race} Forms ==="]
        for form_key, form in forms:
            pl_mult = form.get("pl_multiplier", 1.0)
            drain = form.get("drain", 0)
            lines.append(f"  {form['name']}: {pl_mult}x PL, {drain} Ki/s drain")

        caller.msg("\n".join(lines))


class CmdLSSJ(Command):
    """
    Control Legendary Super Saiyan transformation.

    Usage:
      lssj [train|stop]

    LSSJ is a unique transformation requiring special training.
    Use 'train' to increase your control, 'stop' to revert.
    """
    key = "lssj"

    def func(self):
        caller = self.caller

        if caller.db.race != "Saiyan":
            caller.msg("Only Saiyans can use LSSJ.")
            return

        if not self.args:
            state = get_lssj_ui_state(caller)
            caller.msg(f"LSSJ Control: {state.get('control', 0)}% | Active: {state.get('active', False)}")
            return

        action = self.args.strip().lower()

        if action == "train":
            result = train_lssj_control(caller)
            if result.get("success"):
                caller.msg(f"LSSJ control increased to {result.get('control')}%!")
            else:
                caller.msg(result.get("reason", "Training failed."))
        elif action == "stop":
            if caller.db.active_form == "lssj":
                deactivate_form(caller)
                caller.msg("You calm your Legendary power.")
            else:
                caller.msg("You're not in LSSJ form.")
        else:
            caller.msg("Usage: lssj [train|stop]")


class CmdRacials(Command):
    """
    List racial abilities.

    Usage:
      racials

    Shows all racial abilities available to your race.
    """
    key = "racials"

    def func(self):
        caller = self.caller
        race = caller.db.race or "Human"

        racials = get_character_racials(race)

        if not racials:
            caller.msg(f"No racial abilities for {race}.")
            return

        lines = [f"=== {race} Racials ==="]
        for racial_key, racial in racials:
            lines.append(f"  {racial['name']}: {racial.get('description', '')[:40]}")

        caller.msg("\n".join(lines))


class CmdRacial(Command):
    """
    Use a racial ability.

    Usage:
      racial <ability>

    Activate one of your racial abilities.
    """
    key = "racial"

    def func(self):
        caller = self.caller
        race = caller.db.race or "Human"

        if not self.args:
            caller.msg("Usage: racial <ability_name>")
            return

        racial_key = self.args.strip().lower()
        racial = get_racial(racial_key, race)

        if not racial:
            caller.msg(f"Unknown racial ability '{racial_key}'. Use 'racials' to list.")
            return

        result = use_racial(caller, racial_key)
        if result.get("success"):
            caller.msg(f"Using {racial['name']}!")
        else:
            caller.msg(result.get("reason", "Failed to use racial."))


class CmdScan(Command):
    """
    Scan an entity's power level.

    Usage:
      scan [target]

    Attempts to determine another entity's power level. Success
    depends on your own power relative to the target.
    """
    key = "scan"

    def func(self):
        caller = self.caller

        if self.args:
            target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return
        else:
            target = None
            for obj in caller.location.contents:
                if obj != caller and hasattr(obj, "db") and obj.db.hp_current is not None:
                    target = obj
                    break

        if not target:
            caller.msg("There's nothing to scan here.")
            return

        my_pl = getattr(caller, "get_current_pl", lambda: 0)()
        target_pl = getattr(target, "get_current_pl", lambda: 0)()

        if target_pl > my_pl * 1.5:
            caller.msg(f"You sense {target.key} is far stronger than you!")
        elif target_pl > my_pl:
            caller.msg(f"You sense {target.key} is stronger than you.")
        elif target_pl > my_pl * 0.7:
            caller.msg(f"You sense {target.key} is about as strong as you.")
        else:
            caller.msg(f"You sense {target.key} is weaker than you.")


class CmdSense(Command):
    """
    Sense ki in the area.

    Usage:
      sense

    Detects all entities in the current room and estimates their power.
    """
    key = "sense"

    def func(self):
        caller = self.caller
        my_pl = getattr(caller, "get_current_pl", lambda: 0)()

        lines = ["=== Sensed Entities ==="]
        for obj in caller.location.contents:
            if obj == caller:
                continue
            if not hasattr(obj, "db"):
                continue

            target_pl = getattr(obj, "get_current_pl", lambda: 0)()

            if target_pl > my_pl * 2:
                strength = "far stronger"
            elif target_pl > my_pl * 1.5:
                strength = "much stronger"
            elif target_pl > my_pl:
                strength = "stronger"
            elif target_pl > my_pl * 0.5:
                strength = "weaker"
            else:
                strength = "much weaker"

            lines.append(f"  {obj.key}: {target_pl:,} ({strength})")

        caller.msg("\n".join(lines))


class CmdSuppress(Command):
    """
    Suppress your power level.

    Usage:
      suppress [level]

    Hides your true power level from scanning. Level is 1-100.
    """
    key = "suppress"

    def func(self):
        caller = self.caller

        if not self.args:
            current = caller.db.suppress_level or 0
            caller.msg(f"Power suppression: {current}%")
            return

        try:
            level = int(self.args.strip())
            if level < 0 or level > 100:
                raise ValueError()
        except ValueError:
            caller.msg("Suppression level must be 0-100.")
            return

        caller.db.suppress_level = level
        caller.msg(f"Power suppressed by {level}%.")


class CmdFly(Command):
    """
    Fly in a direction.

    Usage:
      fly [direction]

    Take to the skies. Direction can be n, s, e, w, ne, nw, se, sw, u, d.
    """
    key = "fly"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: fly [direction]")
            return

        direction = self.args.strip().lower()
        valid_dirs = ["n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d", "up", "down", "north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]

        if direction not in valid_dirs:
            caller.msg(f"Invalid direction. Use: {', '.join(valid_dirs)}")
            return

        # Simplified - just move in the direction
        direction_map = {
            "n": "north", "north": "north",
            "s": "south", "south": "south",
            "e": "east", "east": "east",
            "w": "west", "west": "west",
            "ne": "northeast", "northeast": "northeast",
            "nw": "northwest", "northwest": "northwest",
            "se": "southeast", "southeast": "southeast",
            "sw": "southwest", "southwest": "southwest",
            "u": "up", "up": "up", "d": "down", "down": "down",
        }

        caller.msg(f"You fly {direction_map.get(direction, direction)}.")


# Export all character commands
__all__ = [
    "CmdDBStats",
    "CmdPlayerProfile",
    "CmdTransform",
    "CmdTech",
    "CmdEquipTech",
    "CmdListTech",
    "CmdForms",
    "CmdLSSJ",
    "CmdRacials",
    "CmdRacial",
    "CmdScan",
    "CmdSense",
    "CmdSuppress",
    "CmdFly",
]
