"""
Dragon Ball vertical-slice commands.
"""

from __future__ import annotations

import random
import time

from django.urls import reverse
from evennia.objects.models import ObjectDB
from evennia.utils import evtable
from evennia.utils.create import create_object

from commands.command import Command
from world.combat import engage, disengage, register_beam, start_charging, stop_charging
from world.color_utils import aura_phrase, colorize
from world.content_unlocks import get_trainer_reward_map, get_unlock_label
from world.events import emit_combat_event, emit_entity_delta, emit_vfx
from world.forms import FORMS, activate_form, deactivate_form, get_form, list_forms_for_race
from world.lssj import escalate_lssj, get_lssj_ui_state, train_lssj_control
from world.npc_content import NPC_DEFINITIONS, get_npc_definition
from world.power import pl_gap_effect
from world.quests import (
    accept_quest,
    get_quest_definition,
    get_quest_status,
    get_quests_for_npc,
    mark_quest_turn_in_ready,
    turn_in_quest,
)
from world.racials import (
    RACIALS,
    get_character_racials,
    get_racial,
    get_racial_hook_value,
    use_racial,
)
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


def _parchment_ui(title, lines, width=88):
    """
    Text UI styled like a readable codex/parchment page for info-heavy menus.
    """
    inner = max(48, width - 2)
    top = "|y/" + ("~" * inner) + "\\|n"
    bottom = "|y\\" + ("~" * inner) + "/|n"
    hdr = f" {title} "
    left = max(0, (inner - len(hdr)) // 2)
    right = max(0, inner - len(hdr) - left)
    out = [top, "|y:" + (" " * left) + f"|W{hdr}|n" + (" " * right) + ":|n", "|y:" + ("-" * inner) + ":|n"]
    for raw in lines:
        text = str(raw)
        chunks = [text[i : i + inner] for i in range(0, len(text), inner)] or [""]
        for chunk in chunks:
            out.append("|y:|n" + f"{chunk.ljust(inner)}" + "|y:|n")
    out.append(bottom)
    return "\n".join(out)


def _ic_menu_state(caller):
    state = getattr(caller.ndb, "info_menu_state", None)
    return state if isinstance(state, dict) else None


def _clear_ic_menu(caller, *, msg=True):
    if hasattr(caller.ndb, "info_menu_state"):
        caller.ndb.info_menu_state = None
    if msg:
        caller.msg("|xClosed codex menu.|n")


def _render_ic_menu(caller):
    state = _ic_menu_state(caller)
    if not state:
        return False
    view = state.get("view", "list")
    items = state.get("items", [])
    if not items:
        _clear_ic_menu(caller, msg=False)
        caller.msg("Nothing to display.")
        return True

    if view == "list":
        lines = []
        subtitle = state.get("subtitle")
        if subtitle:
            lines.append(subtitle)
            lines.append("")
        for idx, item in enumerate(items, start=1):
            marker = item.get("marker", " ")
            summary = item.get("summary", "")
            line = f"|c[{idx}]|n {marker} |w{item['name']}|n"
            if summary:
                line += f" - {summary}"
            lines.append(line)
        lines.extend(["", "|wB|n Back/Close    |wX|n Exit    |w<number>|n Open entry"])
        caller.msg(_parchment_ui(state.get("title", "Codex"), lines, width=96))
        return True

    if view == "detail":
        idx = int(state.get("index", 0))
        idx = max(0, min(idx, len(items) - 1))
        state["index"] = idx
        item = items[idx]
        lines = [f"|wEntry|n {idx+1}/{len(items)}", ""]
        for label, value in item.get("details", []):
            lines.append(f"|w{label}|n: {value}")
        lines.extend(["", "|wB|n Back to list    |wX|n Exit"])
        caller.msg(_parchment_ui(item.get("detail_title") or item["name"], lines, width=96))
        return True
    return False


def handle_ic_info_menu_input(caller, raw_text):
    state = _ic_menu_state(caller)
    if not state:
        return False
    text = (raw_text or "").strip()
    key = text.lower()

    if key in {"x", "exit", "q", "quit", "close"}:
        _clear_ic_menu(caller)
        return True

    if key in {"b", "back"}:
        if state.get("view") == "detail":
            state["view"] = "list"
            _render_ic_menu(caller)
        else:
            _clear_ic_menu(caller)
        return True

    if state.get("view") == "list" and text.isdigit():
        idx = int(text) - 1
        items = state.get("items", [])
        if 0 <= idx < len(items):
            state["view"] = "detail"
            state["index"] = idx
            _render_ic_menu(caller)
        else:
            caller.msg("|rThat number is not in the list.|n")
            _render_ic_menu(caller)
        return True

    if state.get("view") == "detail":
        caller.msg("|rUse B to go back or X to exit.|n")
        _render_ic_menu(caller)
        return True

    caller.msg("|rEnter a number, B (back), or X (exit).|n")
    _render_ic_menu(caller)
    return True


def _open_technique_codex_menu(caller):
    known = list(caller.db.known_techniques or [])
    equipped = set(caller.db.equipped_techniques or [])
    items = []
    for key in known:
        data = TECHNIQUES.get(key)
        if not data:
            continue
        lvl = _tech_mastery_level(caller, key)
        marker = "@ " if key in equipped else "- "
        items.append(
            {
                "key": key,
                "name": data["name"],
                "marker": marker.strip(),
                "summary": f"ki {data.get('ki_cost','-')} | cd {data.get('cooldown','-')} | m{lvl}",
                "detail_title": f"Technique: {data['name']}",
                "details": [
                    ("Key", key),
                    ("Category", data.get("category", "misc")),
                    ("Tags", ", ".join(data.get("tags", [])) or "None"),
                    ("Ki Cost", data.get("ki_cost", 0)),
                    ("Cooldown", data.get("cooldown", 0)),
                    ("Mastery", lvl),
                    ("Summary", data.get("ui_summary", "")),
                    ("Unlock", get_unlock_label("technique", key)),
                    ("Description", data.get("description", "")),
                ],
            }
        )
    items.sort(key=lambda i: (TECHNIQUES.get(i["key"], {}).get("category", "misc"), i["name"]))
    caller.ndb.info_menu_state = {
        "kind": "techniques",
        "view": "list",
        "title": "Technique Codex",
        "subtitle": "Known abilities. @ = equipped.",
        "items": items,
    }
    _render_ic_menu(caller)


def _open_forms_codex_menu(caller):
    race = caller.db.race or "unknown"
    unlocked = set(caller.db.unlocked_forms or [])
    active = caller.db.active_form
    items = []
    for key, form in list_forms_for_race(race):
        marker = "@" if key == active else ("+" if key in unlocked else "-")
        items.append(
            {
                "key": key,
                "name": form["name"],
                "marker": marker,
                "summary": f"Tier {form.get('tier','?')} | {get_unlock_label('transformation', key)}",
                "detail_title": f"Transformation: {form['name']}",
                "details": [
                    ("Key", key),
                    ("Race", form.get("race", "unknown")),
                    ("Tier", form.get("tier", "?")),
                    ("Status", "active" if key == active else ("unlocked" if key in unlocked else "locked")),
                    ("PL Multiplier", form.get("pl_multiplier", 1.0)),
                    ("Speed Bias", form.get("speed_bias", 1.0)),
                    ("Drain / Tick", form.get("drain_per_tick", 0)),
                    ("Drain / Tech", form.get("drain_per_tech", 0)),
                    ("Unlock", get_unlock_label("transformation", key)),
                    ("Description", form.get("description", "")),
                ],
            }
        )
    caller.ndb.info_menu_state = {
        "kind": "forms",
        "view": "list",
        "title": "Transformation Codex",
        "subtitle": "Available forms for your race. @ = active, + = unlocked.",
        "items": items,
    }
    _render_ic_menu(caller)


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
            ok, msg, _stub = deactivate_form(caller, reason="manual")
            caller.msg(f"|y{msg}|n" if ok else msg)
            if ok:
                emit_vfx(caller.location, "vfx_revert", source=caller)
                emit_entity_delta(caller)
            return
        if not self.args:
            caller.msg("Usage: transform <form> or revert")
            return
        form_key, form = get_form(self.args.strip())
        if not form:
            caller.msg("Unknown form.")
            return
        if caller.db.ki_current < 20 and form.get("resource_drain", {}).get("ki_per_tick", 0) > 0:
            caller.msg("You need at least 20 ki to transform.")
            return
        ok, msg, _stub = activate_form(caller, form_key, context={"command": "transform"})
        if not ok:
            caller.msg(msg)
            return
        caller.msg(f"|y{msg}|n Your {aura_phrase(caller.db.aura_color)} flares.")
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
        ki_cost = int(tech.get("ki_cost", 0) or 0)
        cost_reduction = float(get_racial_hook_value(caller, "ki_cost_reduction", 0.0) or 0.0)
        if tech.get("category") in {"utility", "control"}:
            cost_reduction += float(get_racial_hook_value(caller, "utility_ki_cost_reduction", 0.0) or 0.0)
        ki_cost = max(0, int(round(ki_cost * (1.0 - min(0.65, cost_reduction)))))
        if not caller.spend_ki(ki_cost):
            caller.msg("Not enough ki.")
            return

        target_mode = (tech.get("target_rules") or {}).get("target")
        is_self_target = "self" in tech.get("tags", []) or target_mode == "self"
        target = caller
        if not is_self_target and len(parts) > 1:
            target = _search_target(caller, " ".join(parts[1:]))
            if not target:
                return
        elif not is_self_target:
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
            form = FORMS.get(caller.db.active_form, {})
            form_mastery = (caller.db.form_mastery or {}).get(caller.db.active_form, 0)
            reduction = min(0.7, form_mastery * form.get("mastery_drain_reduction", 0.0))
            tech_drain = max(1, int(form.get("drain_per_tech", 0) * (1.0 - reduction)))
            if tech_drain:
                caller.spend_ki(tech_drain)

        subtype = "technique"
        effect_type = (tech.get("effect") or {}).get("type")
        if effect_type == "transform":
            form_key = tech["effect"].get("form_key")
            ok, msg, _stub = activate_form(caller, form_key, context={"via_technique": tech_key})
            caller.msg(f"|y{msg}|n" if ok else msg)
            if ok:
                emit_vfx(caller.location, tech.get("vfx_id", "vfx_transform"), source=caller)
                subtype = "transform"
            _gain_tech_mastery(caller, tech_key, amount=1)
            emit_combat_event(caller.location, caller, None, {"subtype": subtype, "technique": tech_key})
            emit_entity_delta(caller)
            return
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
        elif tech.get("scaling"):
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
        else:
            # Integration-ready stub path for utility/control techniques not hardcoded yet.
            execute_technique_stub(caller, tech_key, target=target, context={"cmd": "tech"})
            caller.msg(
                f"|c{caller.key}|n uses {tech['name']} on {target.key if target else 'self'} "
                f"({tech.get('ui_summary', 'stub effect')})."
            )
            emit_vfx(caller.location, tech.get("vfx_id", "vfx_technique"), source=caller, target=target if target != caller else None)
            subtype = "technique_stub"

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
        _open_technique_codex_menu(caller)


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
        error -= float(get_racial_hook_value(caller, "scan_error_reduction", 0.0) or 0.0)
        if target.db.suppressed:
            error += max(0.02, 0.22 - scanner_skill * 0.002)
        error = max(0.02, error)
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
        sense_bonus = float(get_racial_hook_value(caller, "sense_precision_bonus", 0.0) or 0.0)
        precision_note = f" (enhanced clarity +{int(sense_bonus * 100)}%)" if sense_bonus > 0 else ""
        caller.msg(
            f"You sense {target.key}'s {aura_phrase(target.db.aura_color)} around {breakdown['displayed_pl']} PL."
            f"{precision_note}"
        )


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


class CmdTechniqueUI(Command):
    key = "techui"
    aliases = ["spellui", "techniques"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        try:
            path = reverse("db_technique_ui")
        except Exception:
            path = "/db/techniques/"
        equipped = ", ".join(
            TECHNIQUES[k]["name"] for k in (caller.db.equipped_techniques or []) if k in TECHNIQUES
        ) or "None"
        caller.msg(
            "Technique UI (web): "
            f"|w{path}|n\n"
            "Open this in the Evennia web client browser tab to view search/filter categories and your 4-tech loadout.\n"
            f"Current loadout: {equipped}"
        )


class CmdForms(Command):
    key = "forms"
    aliases = ["listforms"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        _open_forms_codex_menu(caller)
        if caller.db.active_form == "legendary_super_saiyan":
            lssj = get_lssj_ui_state(caller)["modifiers"]
            caller.msg(
                f"LSSJ: stage={lssj.get('stage')} rage={lssj.get('rage')} control={lssj.get('control')} "
                f"PLx={lssj.get('pl_factor',1.0):.2f}"
            )


class CmdLSSJ(Command):
    key = "lssj"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        arg = (self.args or "").strip().lower()
        if not arg or arg == "status":
            ui = get_lssj_ui_state(caller)
            state = ui["state"]
            mods = ui["modifiers"]
            caller.msg(
                "LSSJ Status: "
                f"unlocked={state.get('unlocked')} active={state.get('active')} stage={state.get('stage')} "
                f"rage={state.get('rage')} control={state.get('control')} mastery={state.get('mastery_rank')} "
                f"PLx={mods.get('pl_factor',1.0):.2f}"
            )
            return
        if arg == "escalate":
            ok, msg = escalate_lssj(caller)
            caller.msg(msg)
            return
        if arg == "train":
            state = train_lssj_control(caller, amount=1)
            caller.msg(
                f"LSSJ training stub: mastery={state.get('mastery_rank')} control={state.get('control')}."
            )
            return
        caller.msg("Usage: lssj [status|escalate|train]")


class CmdRacials(Command):
    key = "racials"
    aliases = ["racialslist", "traits"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        racials = get_character_racials(caller)
        if not racials:
            caller.msg("No racials found for your character.")
            return
        cds = caller.db.racial_cooldowns or {}
        now = time.time()
        lines = []
        for key, data in racials:
            marker = "A" if data.get("kind") == "active" else "P"
            cd_left = max(0.0, float(cds.get(key, 0) or 0) - now)
            cost = int(data.get("ki_cost", 0) or 0)
            extra = []
            if cost:
                extra.append(f"ki {cost}")
            if data.get("cooldown"):
                extra.append(f"cd {data.get('cooldown', 0):.0f}s")
            if cd_left > 0:
                extra.append(f"ready {cd_left:.1f}s")
            extra_txt = f" [{', '.join(extra)}]" if extra else ""
            lines.append(f"[{marker}] {data['name']} - {data.get('ui_summary', data.get('description', ''))}{extra_txt}")
        caller.msg("Racial traits:\n" + "\n".join(lines))
        caller.msg("Racial traits are passive for now.")


class CmdRacial(Command):
    key = "racial"
    aliases = ["traituse"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: racial <racial_name> [target]")
            return
        parts = self.args.split()
        racial_key = racial = None
        target_start = len(parts)
        # Support multi-word racial names by matching the longest prefix.
        for i in range(len(parts), 0, -1):
            key, data = get_racial(" ".join(parts[:i]))
            if data:
                racial_key, racial = key, data
                target_start = i
                break
        if not racial:
            caller.msg("Unknown racial.")
            return
        target = None
        ok, msg, _stub = use_racial(caller, racial_key, target=target, context={"cmd": "racial"})
        caller.msg(f"|y{msg}|n" if ok else msg)
        if not ok:
            return
        subtype = f"racial_{(racial.get('effect') or {}).get('type', 'use')}"
        emit_vfx(caller.location, racial.get("vfx_id", "vfx_technique"), source=caller, target=target)
        emit_combat_event(caller.location, caller, target, {"subtype": subtype, "racial": racial_key})
        emit_entity_delta(caller)
        if target and target != caller and hasattr(target, "db"):
            emit_entity_delta(target)


class CmdQuests(Command):
    key = "quests"
    aliases = ["questlog"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        arg = (self.args or "").strip()
        if not arg:
            nearby = []
            for obj in caller.location.contents if caller.location else []:
                if _is_npc(obj) and (obj.db.npc_role == "trainer"):
                    nearby.append(obj)
            if nearby:
                lines = ["Nearby trainer quest boards:"]
                for npc in nearby:
                    npc_key = npc.db.trainer_key or npc.db.npc_content_key
                    qlist = get_quests_for_npc(npc_key)
                    lines.append(f"- {npc.key}: {len(qlist)} quest(s)")
                    for quest in qlist[:5]:
                        status = get_quest_status(caller, quest["id"])
                        if status.get("completed"):
                            state = "completed"
                        elif status.get("turn_in_ready"):
                            state = "turn-in ready"
                        elif status.get("accepted"):
                            state = "accepted"
                        else:
                            state = "available"
                        lines.append(f"  {quest['id']} [{state}]")
                caller.msg("\n".join(lines))
                caller.msg("Use `quest <accept|done|turnin|show> <quest_id>`.")
                return
            state = caller.db.quest_state or {}
            if not state:
                caller.msg("No quest progress yet. Talk to a trainer.")
                return
            lines = ["Quest progress:"]
            for quest_id in sorted(state.keys()):
                quest = get_quest_definition(quest_id) or {"title": quest_id}
                status = get_quest_status(caller, quest_id)
                flags = []
                if status.get("accepted"):
                    flags.append("accepted")
                if status.get("turn_in_ready"):
                    flags.append("turn-in")
                if status.get("completed"):
                    flags.append("completed")
                lines.append(f"- {quest['title']} ({quest_id}) [{' / '.join(flags) or 'unknown'}]")
            caller.msg("\n".join(lines))
            return

        quest = get_quest_definition(arg)
        if not quest:
            caller.msg("Unknown quest id.")
            return
        status = get_quest_status(caller, arg)
        caller.msg(
            f"{quest['title']} ({quest['id']})\n"
            f"Giver: {NPC_DEFINITIONS.get(quest['giver'], {}).get('name', quest['giver'])}\n"
            f"{quest.get('summary','')}\n"
            f"State: accepted={status.get('accepted')} ready={status.get('turn_in_ready')} completed={status.get('completed')}"
        )


class CmdQuest(Command):
    key = "quest"
    locks = "cmd:all()"
    help_category = "DB"

    def _nearby_trainer_key(self, caller, quest_id):
        quest = get_quest_definition(quest_id)
        if not quest or not caller.location:
            return None
        giver = quest.get("giver")
        for obj in caller.location.contents:
            if not _is_npc(obj):
                continue
            npc_key = obj.db.trainer_key or obj.db.npc_content_key
            if npc_key == giver:
                return npc_key
        return None

    def func(self):
        caller = self.caller
        parts = (self.args or "").split()
        if len(parts) < 2:
            caller.msg("Usage: quest <accept|done|turnin|show> <quest_id>")
            return
        action = parts[0].lower()
        quest_id = parts[1]
        quest = get_quest_definition(quest_id)
        if not quest:
            caller.msg("Unknown quest id.")
            return
        if action == "show":
            status = get_quest_status(caller, quest_id)
            caller.msg(
                f"{quest['title']} ({quest_id})\n{quest.get('summary','')}\n"
                f"accepted={status.get('accepted')} ready={status.get('turn_in_ready')} completed={status.get('completed')}"
            )
            return
        nearby_giver = self._nearby_trainer_key(caller, quest_id)
        if not nearby_giver:
            caller.msg("You must be near that trainer to manage this quest.")
            return
        if action == "accept":
            ok, msg, _state = accept_quest(caller, quest_id)
            caller.msg(msg)
            return
        if action in {"done", "complete"}:
            ok, msg, _state = mark_quest_turn_in_ready(caller, quest_id)
            caller.msg(msg)
            return
        if action in {"turnin", "claim"}:
            ok, msg, payload = turn_in_quest(caller, quest_id, npc_key=nearby_giver)
            caller.msg(msg)
            if ok and payload:
                granted = payload.get("granted", {})
                techs = [TECHNIQUES[k]["name"] for k in granted.get("techniques", []) if k in TECHNIQUES]
                forms = [FORMS[k]["name"] for k in granted.get("forms", []) if k in FORMS]
                if techs:
                    caller.msg("Learned techniques: " + ", ".join(techs))
                if forms:
                    caller.msg("Unlocked forms: " + ", ".join(forms))
                if granted.get("lssj_changed"):
                    caller.msg("LSSJ progression updated.")
                emit_entity_delta(caller)
            return
        caller.msg("Usage: quest <accept|done|turnin|show> <quest_id>")


class CmdTalk(Command):
    key = "talk"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: talk <npc>")
            return
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        if not _is_npc(target):
            caller.msg("That target has nothing useful to say.")
            return
        content_key = target.db.trainer_key or target.db.npc_content_key
        data = get_npc_definition(content_key)
        if not data:
            caller.msg(f"{target.key} has no trainer dialogue scaffold attached yet.")
            return
        quests = get_quests_for_npc(content_key)
        reward_map = get_trainer_reward_map().get(content_key, {})
        lines = [
            f"|w{data['name']}|n - {data.get('bio','')}",
            f"Role: {data.get('role','npc')} | Location hint: {data.get('location_hint','Unknown')}",
            f"Signature moves: {', '.join(data.get('signature_moves', [])) or 'None'}",
            "",
            "Dialogue:",
        ]
        for text in data.get("dialogue", []):
            lines.append(f'  "{text}"')
        lines.append("")
        lines.append("Questlines:")
        for quest in quests:
            lines.append(f"  - {quest['title']} ({quest['id']})")
        lines.append("")
        lines.append(
            "Teaches: "
            + ", ".join(TECHNIQUES[k]["name"] for k in reward_map.get("techniques", []) if k in TECHNIQUES)
            if reward_map.get("techniques")
            else "Teaches: (content mapped, no direct technique rewards listed)"
        )
        if reward_map.get("transformations"):
            lines.append(
                "Forms: "
                + ", ".join(FORMS[k]["name"] for k in reward_map["transformations"] if k in FORMS)
            )
        caller.msg("\n".join(lines))


class CmdSpawnTrainer(Command):
    key = "spawntrainer"
    aliases = ["spawnnpc"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: spawntrainer <npc_key>")
            caller.msg("Available: " + ", ".join(sorted(NPC_DEFINITIONS.keys())))
            return
        if not caller.location:
            caller.msg("You are nowhere.")
            return
        raw = self.args.strip().lower().replace(" ", "_")
        if raw == "all":
            spawned = []
            for npc_key in sorted(NPC_DEFINITIONS.keys()):
                data = get_npc_definition(npc_key)
                if not data:
                    continue
                if any(getattr(obj.db, "trainer_key", None) == npc_key for obj in caller.location.contents):
                    continue
                from typeclasses.npcs import TrainingNPC

                npc = create_object(TrainingNPC, key=data["name"], location=caller.location)
                npc.db.trainer_key = npc_key
                npc.db.npc_content_key = npc_key
                npc.db.npc_role = data.get("role", "trainer")
                npc.db.bio = data.get("bio")
                npc.db.dialogue_lines = data.get("dialogue", [])
                npc.db.questline_keys = data.get("questlines", [])
                rewards = get_trainer_reward_map().get(npc_key, {})
                npc.db.teaches_techniques = rewards.get("techniques", [])
                npc.db.teaches_forms = rewards.get("transformations", [])
                spawned.append(npc.key)
            caller.msg(f"Spawned {len(spawned)} trainers: {', '.join(spawned)}")
            return
        npc_key = raw
        data = get_npc_definition(npc_key)
        if not data:
            caller.msg("Unknown NPC key.")
            return
        from typeclasses.npcs import TrainingNPC

        npc = create_object(TrainingNPC, key=data["name"], location=caller.location)
        npc.db.trainer_key = npc_key
        npc.db.npc_content_key = npc_key
        npc.db.npc_role = data.get("role", "trainer")
        npc.db.bio = data.get("bio")
        npc.db.dialogue_lines = data.get("dialogue", [])
        npc.db.questline_keys = data.get("questlines", [])
        rewards = get_trainer_reward_map().get(npc_key, {})
        npc.db.teaches_techniques = rewards.get("techniques", [])
        npc.db.teaches_forms = rewards.get("transformations", [])
        caller.msg(f"Spawned trainer NPC: {npc.key} ({npc_key}). Use `talk {npc.key}`.")


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
            "techui\n"
            "forms\n"
            "racials\n"
            "racial <trait> [target]\n"
            "quests [quest_id]\n"
            "quest <accept|done|turnin|show> <quest_id>\n"
            "lssj [status|escalate|train]\n"
            "scan <target>\n"
            "sense <target|room>\n"
            "suppress on|off\n"
            "train\n"
            "talk <npc>\n"
            "spawntrainer <npc_key>\n"
            "map\n"
            "logo_test\n"
            "helpdb\n"
            "teleport <x> <y> [z]\n"
            "n/s/e/w/u/d (spatial grid movement)\n"
            "\nNotes: Combat has passive 1s ticks. Beams can collide into beam struggles if exchanged quickly."
        )


class CmdMap(Command):
    """
    View the map of your current area.
    """
    key = "map"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Scouting support: map <x> <y>
        args = self.args.strip().split()
        if len(args) >= 2:
            try:
                scout_x = int(args[0])
                scout_y = int(args[1])
                from world.map_utils import render_map
                map_str = render_map(scout_x, scout_y, radius=5, target_obj=caller)
                caller.msg(f"|y[|c Scout View: {scout_x}, {scout_y} |y]|n\n" + map_str)
                return
            except ValueError:
                pass

        loc = caller.location
        if not loc:
            caller.msg("You are nowhere.")
            return

        coords = getattr(caller.db, "coords", (0, 0, 0))
        from world.map_utils import render_map
        map_str = render_map(coords[0], coords[1], radius=7, target_obj=caller)
        
        zone_name = "Unknown Area"
        if loc.tags.get(category="zone"):
            zone_name = loc.tags.get(category="zone")
            
        caller.msg(f"|y[|c {zone_name} |y]|n |w({coords[0]}, {coords[1]})|n\n" + map_str)


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


class CmdLogout(Command):
    """
    Leave the current character and return to the post-login main menu.
    """

    key = "logout"
    aliases = ["logoff"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        session = getattr(self, "session", None)
        account = getattr(caller, "account", None)
        if not account or not session:
            caller.msg("|rCannot log out from this session.|n")
            return

        try:
            account.unpuppet_object(session)
        except Exception as err:
            caller.msg(f"|rLogout failed: {err}|n")
            return

        # Hand control back to the enforced OOC menu.
        if hasattr(account, "_db_menu_reset"):
            account._db_menu_reset(session=session)
        if hasattr(account, "_db_menu_send"):
            account._db_menu_send(session=session)
        else:
            account.msg(account.at_look(target=account.characters, session=session), session=session)


class CmdGridMove(Command):
    """
    Move in a cardinal direction on the spatial grid.
    """

    key = "north"
    aliases = ["south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        direction = self.cmdstring.lower()
        # Mapping for vectors
        vectors = {
            "north": (0, 1, 0),
            "n": (0, 1, 0),
            "south": (0, -1, 0),
            "s": (0, -1, 0),
            "east": (1, 0, 0),
            "e": (1, 0, 0),
            "west": (-1, 0, 0),
            "w": (-1, 0, 0),
            "up": (0, 0, 1),
            "u": (0, 0, 1),
            "down": (0, 0, -1),
            "d": (0, 0, -1),
        }

        vector = vectors.get(direction)
        if not vector:
            caller.msg("Invalid direction.")
            return

        # Get current coords
        curr_coords = getattr(caller.db, "coords", (0, 0, 0))
        new_coords = (
            curr_coords[0] + vector[0],
            curr_coords[1] + vector[1],
            curr_coords[2] + vector[2],
        )

        # Task 7: Bounds checking (arbitrary for now, e.g. -500 to 500)
        MAP_LIMIT = 500
        if any(abs(c) > MAP_LIMIT for c in new_coords):
            caller.msg("You cannot move any further in that direction.")
            return

        # Task 6: Find target room
        from world.map_utils import get_room_at

        target_room = get_room_at(*new_coords)

        if target_room:
            # If we were in a room but the new coords point to another room, move.
            if caller.location != target_room:
                caller.move_to(target_room)
            caller.db.coords = new_coords
            # caller.msg(f"You move {direction} to {new_coords}.")
            # Evennia's at_post_move will handle the 'look' typically.
        else:
            # In this coordinate-based world, if no room exists, we block movement.
            caller.msg(f"There is nothing in that direction ({new_coords}).")


class CmdTeleport(Command):
    """
    Jump to specific coordinates.
    Usage: teleport <x> <y> [z]
    """

    key = "teleport"
    aliases = ["tpl"]
    locks = "cmd:perm(Builders)"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: teleport <x> <y> [z]")
            return

        args = self.args.strip().split()
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2]) if len(args) > 2 else 0
        except (ValueError, IndexError):
            caller.msg("Coordinates must be integers.")
            return

        from world.map_utils import get_room_at

        target_room = get_room_at(x, y, z)
        if target_room:
            caller.move_to(target_room)
            caller.db.coords = (x, y, z)
            caller.msg(f"Teleported to ({x}, {y}, {z}).")
        else:
            caller.msg(f"No GridRoom exists at ({x}, {y}, {z}).")


class CmdNPCStress(Command):
    key = "+npcstress"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        try:
            count = int(self.args.strip()) if self.args else 10
        except ValueError:
            count = 10

        from typeclasses.npcs import create_test_npc
        for i in range(count):
            npc = create_test_npc(caller.location, template_key="test_even", name=f"StressBot_0{i}")
            npc.db.test_ai = "stress_move"
            npc.db.attack_interval = 0.5
        caller.msg(f"Spawned {count} stress test bots.")
