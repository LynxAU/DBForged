"""
Dragon Ball vertical-slice commands.
"""

from __future__ import annotations

import random
import time

from evennia.objects.models import ObjectDB
from evennia.utils import evtable

from commands.command import Command
from world.combat import engage, disengage, register_beam, start_charging, stop_charging
from world.color_utils import aura_phrase, colorize
from world.events import emit_combat_event, emit_entity_delta, emit_vfx
from world.forms import get_form
from world.power import pl_gap_effect
from world.techniques import TECHNIQUES, get_technique, is_beam


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
        title_line = "│" + title_text[:inner].ljust(inner) + "│"
    out = [top, title_line, "├" + ("─" * inner) + "┤"]
    for raw in lines:
        text = str(raw)
        chunks = [text[i : i + inner] for i in range(0, len(text), inner)] or [""]
        for chunk in chunks:
            out.append("│" + chunk.ljust(inner) + "│")
    out.append(bottom)
    return "\n".join(out)


class CmdDBStats(Command):
    key = "+stats"
    aliases = ["stats"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        stats = caller.get_stats()
        _, breakdown = caller.get_current_pl()
        table = evtable.EvTable(border="none")
        table.add_row("|wHealth|n", f"{stats['hp_current']}/{stats['hp_max']}")
        table.add_row("|wKi|n", f"{stats['ki_current']}/{stats['ki_max']}")
        table.add_row("|wPower Level (combat)|n", stats["power_level"])
        table.add_row("|wPower Level (displayed)|n", stats["displayed_power_level"])
        table.add_row("|wBase Power|n", stats["base_power"])
        table.add_row("|wSTR/SPD/BAL/MAS|n", f"{stats['strength']}/{stats['speed']}/{stats['balance']}/{stats['mastery']}")
        table.add_row("|wKi Control|n", stats["ki_control"])
        table.add_row(
            "|wAppearance|n",
            (
                f"{caller.db.race}/{caller.db.sex} "
                f"hair:{caller.db.hair_style} {colorize(caller.db.hair_color)} "
                f"eyes:{colorize(caller.db.eye_color)} aura:{colorize(caller.db.aura_color)}"
            ),
        )
        caller.msg(str(table))
        caller.msg(
            "PL breakdown: "
            f"stats {breakdown['stat_factor']} x injury {breakdown['injury_factor']} x ki {breakdown['ki_factor']} "
            f"x charge {breakdown['charge_factor']} x form {breakdown['form_factor']} "
            f"x control {breakdown['control_efficiency']} x bruised {breakdown['bruised_factor']}."
        )


class CmdAttack(Command):
    key = "attack"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
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


class CmdFlee(Command):
    key = "flee"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not caller.is_in_combat():
            caller.msg("You are not in combat.")
            return
        if random.random() < 0.35:
            caller.msg("|rYou fail to disengage.|n")
            return
        disengage(caller)
        caller.msg("|gYou disengage and flee from the fight.|n")
        emit_combat_event(caller.location, caller, None, {"subtype": "flee"})


class CmdCharge(Command):
    key = "charge"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if caller.db.is_charging:
            stop_charging(caller)
            caller.msg("You relax your stance and stop charging.")
            return
        if caller.has_status("stunned"):
            caller.msg("You are stunned and cannot focus your ki.")
            return
        start_charging(caller, duration=6)
        caller.msg(
            f"|cYou begin charging ki.|n Your {aura_phrase(caller.db.aura_color)} starts to rise. "
            "You are vulnerable to interrupts."
        )


class CmdTransform(Command):
    key = "transform"
    aliases = ["revert"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        raw = self.cmdstring.lower() if self.cmdstring else ""
        if raw == "revert" or self.args.strip().lower() == "revert":
            if caller.db.active_form:
                caller.db.active_form = None
                caller.msg(f"|yYou revert to base form.|n Your {aura_phrase(caller.db.aura_color)} settles.")
                emit_vfx(caller.location, "vfx_revert", source=caller)
                emit_entity_delta(caller)
            else:
                caller.msg("You are already in base form.")
            return
        if not self.args:
            caller.msg("Usage: transform <form> or revert")
            return
        form_key, form = get_form(self.args.strip())
        if not form:
            caller.msg("Unknown form.")
            return
        if form.get("stub"):
            caller.msg(f"{form['name']} is not implemented in this slice.")
            return
        if form.get("race") != (caller.db.race or "").lower():
            caller.msg(f"Only {form.get('race')} can use {form['name']}.")
            return
        if caller.db.active_form == form_key:
            caller.msg("You are already in that form.")
            return
        if caller.db.ki_current < 20:
            caller.msg("You need at least 20 ki to transform.")
            return
        caller.db.active_form = form_key
        mastery = dict(caller.db.form_mastery or {})
        mastery[form_key] = mastery.get(form_key, 0) + 1
        caller.db.form_mastery = mastery
        caller.msg(f"|yYou transform into {form['name']}!|n Your {aura_phrase(caller.db.aura_color)} flares.")
        emit_vfx(caller.location, form.get("vfx_id", "vfx_transform"), source=caller)
        emit_entity_delta(caller)


class CmdTech(Command):
    key = "tech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: tech <techname> <target?>")
            return
        parts = self.args.split()
        tech_key, tech = get_technique(parts[0])
        if not tech:
            caller.msg("Unknown technique.")
            return
        if tech_key not in (caller.db.equipped_techniques or []):
            caller.msg("That technique is not equipped.")
            return
        if caller.has_status("stunned"):
            caller.msg("You are stunned and cannot use techniques.")
            return
        cd = _cooldown_remaining(caller, tech_key)
        if cd > 0:
            caller.msg(f"Technique on cooldown: {cd:.1f}s")
            return
        if not caller.spend_ki(tech["ki_cost"]):
            caller.msg("Not enough ki.")
            return

        target = caller
        if "self" not in tech.get("tags", []) and len(parts) > 1:
            target = _search_target(caller, " ".join(parts[1:]))
            if not target:
                return
        elif "self" not in tech.get("tags", []):
            target = ObjectDB.objects.filter(id=caller.db.combat_target).first() if caller.db.combat_target else None
            if target and target.location != caller.location:
                target = None
            if not target:
                caller.msg("Specify a target.")
                return

        if target != caller:
            if not hasattr(target, "get_current_pl"):
                caller.msg("That is not a valid combat target.")
                return
            engage(caller, target)
        mastery_level = _tech_mastery_level(caller, tech_key)
        cooldown = max(0.8, tech["cooldown"] - min(1.4, mastery_level * 0.04))
        _set_cooldown(caller, tech_key, cooldown)

        if caller.db.active_form:
            from world.forms import FORMS

            form = FORMS.get(caller.db.active_form, {})
            form_mastery = (caller.db.form_mastery or {}).get(caller.db.active_form, 0)
            reduction = min(0.7, form_mastery * form.get("mastery_drain_reduction", 0.0))
            tech_drain = max(1, int(form.get("drain_per_tech", 0) * (1.0 - reduction)))
            if tech_drain:
                caller.spend_ki(tech_drain)

        subtype = "technique"
        if tech_key == "solar_flare":
            target.add_status("stunned", tech["effect"]["duration"])
            _interrupt_target(target, caller)
            caller.location.msg_contents(f"|y{caller.key} unleashes Solar Flare, stunning {target.key}!|n")
            emit_vfx(caller.location, tech["vfx_id"], source=caller, target=target)
            subtype = "stun"
        elif tech_key == "guard":
            caller.add_status("guard", tech["effect"]["duration"], reduction=tech["effect"]["reduction"])
            caller.msg("You tighten your defense.")
            emit_vfx(caller.location, tech["vfx_id"], source=caller)
            subtype = "defense"
        elif tech_key == "afterimage_dash":
            caller.add_status("afterimage", tech["effect"]["duration"])
            caller.msg("You burst into afterimages and become hard to track.")
            emit_vfx(caller.location, tech["vfx_id"], source=caller)
            subtype = "movement"
        else:
            scaling = tech["scaling"]
            pl, _ = caller.get_current_pl()
            gap = pl_gap_effect(pl, target.get_current_pl()[0])
            base_damage = (
                scaling["base"]
                + int((caller.db.strength or 10) * scaling["strength"])
                + int((caller.db.mastery or 10) * scaling["mastery"])
                + int(pl * scaling["pl"])
                + int(mastery_level * 0.7)
            )
            if tech_key == "vanish_strike":
                _interrupt_target(target, caller)
            if is_beam(tech_key):
                register_beam(caller, target, tech_key, base_damage)
                caller.location.msg_contents(
                    f"|c{caller.key} fires {tech['name']} at {target.key}!|n"
                )
                subtype = "beam_cast"
            else:
                damage = int(base_damage * gap["damage_mult"])
                dealt = target.apply_damage(damage, source=caller, kind="technique")
                caller.location.msg_contents(
                    f"|c{caller.key}|n uses {tech['name']} on {target.key} for |r{dealt}|n!"
                )
                emit_entity_delta(target)
                subtype = "damage"
            emit_vfx(caller.location, tech["vfx_id"], source=caller, target=target)

        _gain_tech_mastery(caller, tech_key, amount=1)
        emit_combat_event(
            caller.location,
            caller,
            target if target != caller else None,
            {"subtype": subtype, "technique": tech_key},
        )
        emit_entity_delta(caller)


class CmdEquipTech(Command):
    key = "equiptech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: equiptech <techname>")
            return
        if caller.is_in_combat():
            caller.msg("You can only change techniques out of combat.")
            return
        tech_key, tech = get_technique(self.args.strip())
        if not tech:
            caller.msg("Unknown technique.")
            return
        known = list(caller.db.known_techniques or [])
        if tech_key not in known:
            caller.msg("You have not learned that technique.")
            return
        equipped = list(caller.db.equipped_techniques or [])
        if tech_key in equipped:
            caller.msg("Already equipped.")
            return
        if len(equipped) >= 4:
            dropped = equipped.pop(0)
            caller.msg(f"Equip limit reached; unequipped {TECHNIQUES[dropped]['name']}.")
        equipped.append(tech_key)
        caller.db.equipped_techniques = equipped
        caller.msg(f"Equipped {tech['name']}.")


class CmdListTech(Command):
    key = "listtech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        known = caller.db.known_techniques or []
        equipped = set(caller.db.equipped_techniques or [])
        rows = []
        for key in known:
            data = TECHNIQUES.get(key, {"name": key})
            marker = "*" if key in equipped else " "
            lvl = _tech_mastery_level(caller, key)
            rows.append(f"[{marker}] {data['name']} (ki {data.get('ki_cost', '-')}, cd {data.get('cooldown', '-')}, m{lvl})")
        caller.msg("Known techniques:\n" + "\n".join(rows))
        caller.msg("`*` = equipped (max 4).")


class CmdScan(Command):
    key = "scan"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: scan <target>")
            return
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        if not hasattr(target, "get_current_pl"):
            caller.msg("That target has no readable power signature.")
            return
        _, breakdown = target.get_current_pl()
        displayed = breakdown["displayed_pl"]
        scanner_skill = (caller.db.ki_control or 0) + (caller.db.mastery or 0) * 0.35
        error = max(0.04, 0.30 - scanner_skill * 0.0045)
        if target.db.suppressed:
            error += max(0.02, 0.22 - scanner_skill * 0.002)
        estimate = int(max(1, displayed * random.uniform(1.0 - error, 1.0 + error)))
        caller.msg(f"Scouter readout on {target.key}: ~{estimate} PL (error margin ~{int(error*100)}%).")


class CmdSense(Command):
    key = "sense"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if (caller.db.ki_control or 0) < 15:
            caller.msg("Your ki control is too low to sense energy directly (need 15).")
            return
        if not self.args:
            caller.msg("Usage: sense <target or room>")
            return
        arg = self.args.strip().lower()
        if arg == "room":
            lines = []
            for obj in caller.location.contents:
                if not hasattr(obj, "get_current_pl") or obj == caller:
                    continue
                _, breakdown = obj.get_current_pl()
                lines.append(f"{obj.key}: {aura_phrase(obj.db.aura_color)} ~{breakdown['displayed_pl']}")
            caller.msg("Room ki signatures:\n" + ("\n".join(lines) if lines else "None detected."))
            return
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        if not hasattr(target, "get_current_pl"):
            caller.msg("You cannot sense that target.")
            return
        _, breakdown = target.get_current_pl()
        caller.msg(f"You sense {target.key}'s {aura_phrase(target.db.aura_color)} around {breakdown['displayed_pl']} PL.")


class CmdSuppress(Command):
    key = "suppress"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        if arg not in {"on", "off"}:
            caller.msg("Usage: suppress on|off")
            return
        caller.db.suppressed = arg == "on"
        caller.msg("Suppression enabled." if caller.db.suppressed else "Suppression disabled.")
        emit_entity_delta(caller)


class CmdTrain(Command):
    key = "train"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        trainer = None
        for obj in caller.location.contents:
            if _is_npc(obj) and obj.db.npc_role == "trainer":
                trainer = obj
                break
        if not trainer:
            caller.msg("No trainer is available here.")
            return
        if caller.is_in_combat():
            caller.msg("You cannot train in active combat.")
            return
        gains = ["strength", "speed", "balance", "mastery"]
        stat = random.choice(gains)
        caller.db[stat] = (caller.db[stat] or 10) + 1
        caller.db.base_power = (caller.db.base_power or 100) + 3
        caller.db.ki_control = min(100, (caller.db.ki_control or 0) + 1)
        caller.msg(
            f"{trainer.key} drills fundamentals. +1 {stat}, +3 base power, +1 ki_control."
        )
        emit_entity_delta(caller)


class CmdPlayerProfile(Command):
    key = "player"
    aliases = ["profile", "sheet", "me"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        stats = caller.get_stats()
        _, breakdown = caller.get_current_pl()

        equipped = [TECHNIQUES[k]["name"] for k in (caller.db.equipped_techniques or []) if k in TECHNIQUES]
        known = [TECHNIQUES[k]["name"] for k in (caller.db.known_techniques or []) if k in TECHNIQUES]
        statuses = sorted((caller.db.statuses or {}).keys()) if caller.db.statuses else []

        lines = [
            f"|wName|n: {caller.key}    |wDBREF|n: {caller.dbref}",
            f"|wRace|n: {caller.db.race or 'unknown'}    |wSex|n: {caller.db.sex or 'unknown'}",
            f"|wForm|n: {caller.db.active_form or 'base'}    |wSuppressed|n: {'yes' if caller.db.suppressed else 'no'}",
            f"|wLocation|n: {(caller.location.key if caller.location else 'None')}",
            "",
            f"|wHP|n {stats['hp_current']}/{stats['hp_max']}   |wKI|n {stats['ki_current']}/{stats['ki_max']}",
            f"|wPL (combat)|n {stats['power_level']}   |wPL (displayed)|n {breakdown['displayed_pl']}",
            f"|wBase Power|n {stats['base_power']}   |wKi Control|n {stats['ki_control']}",
            f"|wSTR/SPD/BAL/MAS|n {stats['strength']}/{stats['speed']}/{stats['balance']}/{stats['mastery']}",
            "",
            (
                f"|wAppearance|n hair:{caller.db.hair_style or '?'} {colorize(caller.db.hair_color)}  "
                f"eyes:{colorize(caller.db.eye_color)}  aura:{colorize(caller.db.aura_color)}"
            ),
            f"|wStatus Effects|n: {', '.join(statuses) if statuses else 'None'}",
            f"|wEquipped Techs|n: {', '.join(equipped) if equipped else 'None'}",
            f"|wKnown Tech Count|n: {len(known)}",
        ]
        caller.msg(_boxed_ui("DBFORGED PLAYER PROFILE", lines, width=78))


class CmdAttack(Command):
    key = "attack"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
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


class CmdFlee(Command):
    key = "flee"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not caller.is_in_combat():
            caller.msg("You are not in combat.")
            return
        if random.random() < 0.35:
            caller.msg("|rYou fail to disengage.|n")
            return
        disengage(caller)
        caller.msg("|gYou disengage and flee from the fight.|n")
        emit_combat_event(caller.location, caller, None, {"subtype": "flee"})


class CmdCharge(Command):
    key = "charge"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if caller.db.is_charging:
            stop_charging(caller)
            caller.msg("You relax your stance and stop charging.")
            return
        if caller.has_status("stunned"):
            caller.msg("You are stunned and cannot focus your ki.")
            return
        start_charging(caller, duration=6)
        caller.msg(
            f"|cYou begin charging ki.|n Your {aura_phrase(caller.db.aura_color)} starts to rise. "
            "You are vulnerable to interrupts."
        )


class CmdTransform(Command):
    key = "transform"
    aliases = ["revert"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        raw = self.cmdstring.lower() if self.cmdstring else ""
        if raw == "revert" or self.args.strip().lower() == "revert":
            if caller.db.active_form:
                caller.db.active_form = None
                caller.msg(f"|yYou revert to base form.|n Your {aura_phrase(caller.db.aura_color)} settles.")
                emit_vfx(caller.location, "vfx_revert", source=caller)
                emit_entity_delta(caller)
            else:
                caller.msg("You are already in base form.")
            return
        if not self.args:
            caller.msg("Usage: transform <form> or revert")
            return
        form_key, form = get_form(self.args.strip())
        if not form:
            caller.msg("Unknown form.")
            return
        if form.get("stub"):
            caller.msg(f"{form['name']} is not implemented in this slice.")
            return
        if form.get("race") != (caller.db.race or "").lower():
            caller.msg(f"Only {form.get('race')} can use {form['name']}.")
            return
        if caller.db.active_form == form_key:
            caller.msg("You are already in that form.")
            return
        if caller.db.ki_current < 20:
            caller.msg("You need at least 20 ki to transform.")
            return
        caller.db.active_form = form_key
        mastery = dict(caller.db.form_mastery or {})
        mastery[form_key] = mastery.get(form_key, 0) + 1
        caller.db.form_mastery = mastery
        caller.msg(f"|yYou transform into {form['name']}!|n Your {aura_phrase(caller.db.aura_color)} flares.")
        emit_vfx(caller.location, form.get("vfx_id", "vfx_transform"), source=caller)
        emit_entity_delta(caller)


class CmdTech(Command):
    key = "tech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: tech <techname> <target?>")
            return
        parts = self.args.split()
        tech_key, tech = get_technique(parts[0])
        if not tech:
            caller.msg("Unknown technique.")
            return
        if tech_key not in (caller.db.equipped_techniques or []):
            caller.msg("That technique is not equipped.")
            return
        if caller.has_status("stunned"):
            caller.msg("You are stunned and cannot use techniques.")
            return
        cd = _cooldown_remaining(caller, tech_key)
        if cd > 0:
            caller.msg(f"Technique on cooldown: {cd:.1f}s")
            return
        if not caller.spend_ki(tech["ki_cost"]):
            caller.msg("Not enough ki.")
            return

        target = caller
        if "self" not in tech.get("tags", []) and len(parts) > 1:
            target = _search_target(caller, " ".join(parts[1:]))
            if not target:
                return
        elif "self" not in tech.get("tags", []):
            target = ObjectDB.objects.filter(id=caller.db.combat_target).first() if caller.db.combat_target else None
            if target and target.location != caller.location:
                target = None
            if not target:
                caller.msg("Specify a target.")
                return

        if target != caller:
            if not hasattr(target, "get_current_pl"):
                caller.msg("That is not a valid combat target.")
                return
            engage(caller, target)
        mastery_level = _tech_mastery_level(caller, tech_key)
        cooldown = max(0.8, tech["cooldown"] - min(1.4, mastery_level * 0.04))
        _set_cooldown(caller, tech_key, cooldown)

        if caller.db.active_form:
            from world.forms import FORMS

            form = FORMS.get(caller.db.active_form, {})
            form_mastery = (caller.db.form_mastery or {}).get(caller.db.active_form, 0)
            reduction = min(0.7, form_mastery * form.get("mastery_drain_reduction", 0.0))
            tech_drain = max(1, int(form.get("drain_per_tech", 0) * (1.0 - reduction)))
            if tech_drain:
                caller.spend_ki(tech_drain)

        subtype = "technique"
        if tech_key == "solar_flare":
            target.add_status("stunned", tech["effect"]["duration"])
            _interrupt_target(target, caller)
            caller.location.msg_contents(f"|y{caller.key} unleashes Solar Flare, stunning {target.key}!|n")
            emit_vfx(caller.location, tech["vfx_id"], source=caller, target=target)
            subtype = "stun"
        elif tech_key == "guard":
            caller.add_status("guard", tech["effect"]["duration"], reduction=tech["effect"]["reduction"])
            caller.msg("You tighten your defense.")
            emit_vfx(caller.location, tech["vfx_id"], source=caller)
            subtype = "defense"
        elif tech_key == "afterimage_dash":
            caller.add_status("afterimage", tech["effect"]["duration"])
            caller.msg("You burst into afterimages and become hard to track.")
            emit_vfx(caller.location, tech["vfx_id"], source=caller)
            subtype = "movement"
        else:
            scaling = tech["scaling"]
            pl, _ = caller.get_current_pl()
            gap = pl_gap_effect(pl, target.get_current_pl()[0])
            base_damage = (
                scaling["base"]
                + int((caller.db.strength or 10) * scaling["strength"])
                + int((caller.db.mastery or 10) * scaling["mastery"])
                + int(pl * scaling["pl"])
                + int(mastery_level * 0.7)
            )
            if tech_key == "vanish_strike":
                _interrupt_target(target, caller)
            if is_beam(tech_key):
                register_beam(caller, target, tech_key, base_damage)
                caller.location.msg_contents(
                    f"|c{caller.key} fires {tech['name']} at {target.key}!|n"
                )
                subtype = "beam_cast"
            else:
                damage = int(base_damage * gap["damage_mult"])
                dealt = target.apply_damage(damage, source=caller, kind="technique")
                caller.location.msg_contents(
                    f"|c{caller.key}|n uses {tech['name']} on {target.key} for |r{dealt}|n!"
                )
                emit_entity_delta(target)
                subtype = "damage"
            emit_vfx(caller.location, tech["vfx_id"], source=caller, target=target)

        _gain_tech_mastery(caller, tech_key, amount=1)
        emit_combat_event(
            caller.location,
            caller,
            target if target != caller else None,
            {"subtype": subtype, "technique": tech_key},
        )
        emit_entity_delta(caller)


class CmdEquipTech(Command):
    key = "equiptech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: equiptech <techname>")
            return
        if caller.is_in_combat():
            caller.msg("You can only change techniques out of combat.")
            return
        tech_key, tech = get_technique(self.args.strip())
        if not tech:
            caller.msg("Unknown technique.")
            return
        known = list(caller.db.known_techniques or [])
        if tech_key not in known:
            caller.msg("You have not learned that technique.")
            return
        equipped = list(caller.db.equipped_techniques or [])
        if tech_key in equipped:
            caller.msg("Already equipped.")
            return
        if len(equipped) >= 4:
            dropped = equipped.pop(0)
            caller.msg(f"Equip limit reached; unequipped {TECHNIQUES[dropped]['name']}.")
        equipped.append(tech_key)
        caller.db.equipped_techniques = equipped
        caller.msg(f"Equipped {tech['name']}.")


class CmdListTech(Command):
    key = "listtech"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        known = caller.db.known_techniques or []
        equipped = set(caller.db.equipped_techniques or [])
        rows = []
        for key in known:
            data = TECHNIQUES.get(key, {"name": key})
            marker = "*" if key in equipped else " "
            lvl = _tech_mastery_level(caller, key)
            rows.append(f"[{marker}] {data['name']} (ki {data.get('ki_cost', '-')}, cd {data.get('cooldown', '-')}, m{lvl})")
        caller.msg("Known techniques:\n" + "\n".join(rows))
        caller.msg("`*` = equipped (max 4).")


class CmdScan(Command):
    key = "scan"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: scan <target>")
            return
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        if not hasattr(target, "get_current_pl"):
            caller.msg("That target has no readable power signature.")
            return
        _, breakdown = target.get_current_pl()
        displayed = breakdown["displayed_pl"]
        scanner_skill = (caller.db.ki_control or 0) + (caller.db.mastery or 0) * 0.35
        error = max(0.04, 0.30 - scanner_skill * 0.0045)
        if target.db.suppressed:
            error += max(0.02, 0.22 - scanner_skill * 0.002)
        estimate = int(max(1, displayed * random.uniform(1.0 - error, 1.0 + error)))
        caller.msg(f"Scouter readout on {target.key}: ~{estimate} PL (error margin ~{int(error*100)}%).")


class CmdSense(Command):
    key = "sense"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if (caller.db.ki_control or 0) < 15:
            caller.msg("Your ki control is too low to sense energy directly (need 15).")
            return
        if not self.args:
            caller.msg("Usage: sense <target or room>")
            return
        arg = self.args.strip().lower()
        if arg == "room":
            lines = []
            for obj in caller.location.contents:
                if not hasattr(obj, "get_current_pl") or obj == caller:
                    continue
                _, breakdown = obj.get_current_pl()
                lines.append(f"{obj.key}: {aura_phrase(obj.db.aura_color)} ~{breakdown['displayed_pl']}")
            caller.msg("Room ki signatures:\n" + ("\n".join(lines) if lines else "None detected."))
            return
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        if not hasattr(target, "get_current_pl"):
            caller.msg("You cannot sense that target.")
            return
        _, breakdown = target.get_current_pl()
        caller.msg(f"You sense {target.key}'s {aura_phrase(target.db.aura_color)} around {breakdown['displayed_pl']} PL.")


class CmdSuppress(Command):
    key = "suppress"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        if arg not in {"on", "off"}:
            caller.msg("Usage: suppress on|off")
            return
        caller.db.suppressed = arg == "on"
        caller.msg("Suppression enabled." if caller.db.suppressed else "Suppression disabled.")
        emit_entity_delta(caller)


class CmdTrain(Command):
    key = "train"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        trainer = None
        for obj in caller.location.contents:
            if _is_npc(obj) and obj.db.npc_role == "trainer":
                trainer = obj
                break
        if not trainer:
            caller.msg("No trainer is available here.")
            return
        if caller.is_in_combat():
            caller.msg("You cannot train in active combat.")
            return
        gains = ["strength", "speed", "balance", "mastery"]
        stat = random.choice(gains)
        caller.db[stat] = (caller.db[stat] or 10) + 1
        caller.db.base_power = (caller.db.base_power or 100) + 3
        caller.db.ki_control = min(100, (caller.db.ki_control or 0) + 1)
        caller.msg(
            f"{trainer.key} drills fundamentals. +1 {stat}, +3 base power, +1 ki_control."
        )
        emit_entity_delta(caller)


class CmdHelpDB(Command):
    key = "helpdb"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        self.caller.msg(
            "DB Vertical Slice Commands:\n"
            "+stats\n"
            "attack <target>\n"
            "flee\n"
            "charge\n"
            "transform <form> | revert\n"
            "tech <techname> <target?>\n"
            "equiptech <techname>\n"
            "listtech\n"
            "scan <target>\n"
            "sense <target|room>\n"
            "suppress on|off\n"
            "train\n"
            "teleport <target> (builder/admin)\n"
            "logo_test\n"
            "helpdb\n"
            "\nNotes: Combat has passive 1s ticks. Beams can collide into beam struggles if exchanged quickly."
        )


class CmdLogoTest(Command):
    key = "logo_test"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        try:
            from server.conf import connection_screens
        except Exception as err:
            caller.msg(f"|rCould not import connection screen renderer: {err}|n")
            return
        try:
            if hasattr(connection_screens, "_LOGO_CACHE"):
                connection_screens._LOGO_CACHE = None
            logo = connection_screens._render_logo_ansi()
            logo_path = connection_screens._find_logo_path()
        except Exception as err:
            caller.msg(f"|rLogo render failed: {err}|n")
            return
        if not logo:
            caller.msg(
                "No logo image found. Place PNG at |wserver/conf/assets/db_logo.png|n "
                "(or `dragonball_logo.png` / `logo.png`) and run `logo_test` again."
            )
            return
        caller.msg("|wConnection Screen Logo Preview|n")
        caller.msg(logo)
        if logo_path:
            caller.msg(f"|xSource: {logo_path}|n")


class CmdTeleport(Command):
    key = "teleport"
    aliases = ["tel", "tp"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        arg = self.args.strip()
        if not arg:
            caller.msg("Usage: teleport <room|object|#dbref>")
            return

        target = caller.search(arg, global_search=True, quiet=True)
        if not target:
            caller.msg(f"Could not find '{arg}'.")
            return
        if isinstance(target, list):
            if len(target) != 1:
                caller.msg("Multiple matches found. Be more specific.")
                return
            target = target[0]

        destination = target if getattr(target, "location", None) is None else target.location
        if not destination:
            caller.msg("That target has no valid destination.")
            return
        if destination == caller.location:
            caller.msg("You are already there.")
            return

        old_location = caller.location
        caller.move_to(destination, quiet=True, move_hooks=False)
        caller.msg(f"|gTeleported to|n {destination.get_display_name(caller)} |x({destination.dbref})|n.")
        if old_location and old_location != destination:
            caller.execute_cmd("look")
