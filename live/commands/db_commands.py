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
from world.forms import FORMS, activate_form, deactivate_form, get_form, list_forms_for_race, get_form_mastery_display, get_transformation_duration
from world.beam_clash import BeamClash, get_beam_clash, start_beam_clash, end_beam_clash
from world.spirit_bomb import get_spirit_bomb, clear_spirit_bomb, FlurryAttack
from world.namekian_fusion import check_fusion_on_kill, accept_fusion, decline_fusion, unfuse, get_fusion_status
from world.mobility import timeskip, position_swap, save_teleport_location, teleport_to_location, instant_transmission, get_saved_locations
from world.dragon_balls import add_dragon_ball, can_summon_shenron, summon_shenron, make_wish, get_dragon_ball_status
from world.planet_cracker import use_planet_cracker, can_use_planet_cracker, train_with_npc, get_available_trainers, learn_technique_from_trainer, TRAINERS
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


class CmdEquipUltimate(Command):
    """
    Equip an ultimate technique (1 slot)
    
    Usage: equipultimate <techname>
    
    Ultimates are high-powered finishers. They require more Ki
    and have longer cooldowns, but deal massive damage.
    """
    key = "equipultimate"
    aliases = ["equipult"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: equipultimate <techname>")
            caller.msg("Use 'listtech' to see your known techniques.")
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
        # Check if technique qualifies as ultimate (high base damage or marked as ultimate)
        effect = tech.get("effect", {})
        base_damage = effect.get("base_damage", 0) if effect.get("type") == "damage" else 0
        if base_damage < 40 and "ultimate" not in tech.get("tags", []):
            caller.msg(f"{tech['name']} is not an ultimate technique.\n"
                       f"Ultimates must have base damage of 40+ or be tagged as ultimate.")
            return
        current_ultimate = caller.db.equipped_ultimate
        if current_ultimate == tech_key:
            caller.msg("Already set as your ultimate.")
            return
        if current_ultimate and current_ultimate in TECHNIQUES:
            caller.msg(f"Replaced {TECHNIQUES[current_ultimate]['name']} with {tech['name']} as your ultimate.")
        else:
            caller.msg(f"Set {tech['name']} as your ultimate technique.")
        caller.db.equipped_ultimate = tech_key


class CmdCreateUltimate(Command):
    """
    Create a custom ultimate technique
    
    Usage: createultimate
    
    Opens a wizard to design your own signature ultimate technique
    with custom name, attack type, color, and flavor text.
    """
    key = "createultimate"
    aliases = ["createult", "makeultimate"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from commands.ultimate_wizard import start_ultimate_wizard
        caller = self.caller
        if not hasattr(caller, 'db'):
            caller.msg("This command is only available to characters.")
            return
        start_ultimate_wizard(caller)


class CmdUseUltimate(Command):
    """
    Use your equipped ultimate technique
    
    Usage: ultimate [target]
    
    Unleashes your equipped ultimate technique on a target.
    If you have a custom ultimate, it uses your custom flavor text.
    """
    key = "ultimate"
    aliases = ["ult"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check for custom ultimate first
        custom_ult = caller.db.custom_ultimate if hasattr(caller, 'db') else None
        
        if custom_ult:
            # Use custom ultimate
            self._use_custom_ultimate(caller, custom_ult)
            return
        
        # Fall back to equipped technique ultimate
        equipped_ult = caller.db.equipped_ultimate if hasattr(caller, 'db') else None
        
        if not equipped_ult:
            caller.msg("You don't have an ultimate equipped.")
            caller.msg("Use |c/createultimate|n to create a custom ultimate,")
            caller.msg("or |cequipultimate <name>|n to equip a technique as your ultimate.")
            return
        
        if equipped_ult == "custom":
            # Custom was cleared or doesn't exist
            caller.msg("Your custom ultimate seems to be missing. Use |c/createultimate|n to create a new one.")
            return
        
        # Use the equipped technique
        from commands.db_commands import get_technique
        tech_key, tech = get_technique(equipped_ult)
        if not tech:
            caller.msg("Your equipped ultimate technique is not found.")
            caller.msg("Use |cequipultimate <name>|n to equip a different ultimate.")
            return
        
        # Execute the technique
        self.caller.execute_cmd(f"tech {equipped_ult} {self.args}")

    def _use_custom_ultimate(self, caller, custom_ult):
        """Use a custom ultimate with flavor text"""
        # Find target
        target = None
        if self.args:
            # Try to find target by name
            location = caller.location
            if location:
                for obj in location.contents:
                    if obj.key.lower() == self.args.lower() and obj.is_typeclass("typeclasses.characters.Character", exact=False):
                        target = obj
                        break
        
        if not target:
            # Check combat target
            if caller.db.combat_target:
                from evennia.objects.models import ObjectDB
                target = ObjectDB.objects.filter(id=caller.db.combat_target).first()
        
        target_name = target.key if target else "the air"
        
        # Generate flavor text
        flavor_text = custom_ult.get("flavor_text", "")
        if flavor_text:
            final_text = flavor_text.format(target=target_name)
        else:
            final_text = f"{caller.key} unleashes {custom_ult['name']}!"
        
        # Check ki
        ki_cost = 50  # Base ki cost for custom ultimate
        if not caller.spend_ki(ki_cost):
            caller.msg(f"|rYou need {ki_cost} Ki to use {custom_ult['name']}.|n")
            return
        
        # Deal damage if target
        damage = 0
        if target and target.is_typeclass("typeclasses.characters.Character", exact=False):
            damage = 50 + (caller.db.mastery or 10) * 2
            dealt = target.apply_damage(damage, source=caller, kind="ultimate")
            caller.location.msg_contents(f"|m{final_text}|n |r({dealt} damage!)|n")
            
            # Emit events
            from world.events import emit_entity_delta, emit_combat_event
            emit_entity_delta(target)
            if caller.location:
                emit_combat_event(caller.location, caller, target, 
                    {"subtype": "ultimate", "technique": "custom_ultimate", "damage": dealt})
        else:
            caller.location.msg_contents(f"|m{final_text}|n")
        
        # Emit entity update
        from world.events import emit_entity_delta
        emit_entity_delta(caller)


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
        from world.ki_sense_training import (
            KiSenseCommand, start_training, sense_ki, get_training_status, stop_training
        )
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Handle training commands
        if args == "training":
            success, msg = start_training(caller)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        if args == "status" or args == "train":
            caller.msg(get_training_status(caller))
            return
        
        if args == "stop" or args == "end" or args == "quit":
            success, msg = stop_training(caller)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        # Check if in training mode
        if caller.db.get('ki_sense_training'):
            success, msg = sense_ki(caller)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        # Original sense functionality
        if (caller.db.ki_control or 0) < 15:
            caller.msg("Your ki control is too low to sense energy directly (need 15).")
            return
        if not self.args:
            caller.msg("Usage: sense <target or room>")
            caller.msg("Or use 'sense training' to start Ki Sense training!")
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


class CmdMastery(Command):
    """
    Display transformation mastery levels.
    
    Usage: mastery [form_name]
    
    Shows your mastery level for each transformation form you've unlocked.
    Higher mastery means you can hold the transformation longer.
    At 100% mastery, you can hold the form indefinitely.
    """
    key = "mastery"
    aliases = ["transmastery", "formmastery"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if args:
            # Show specific form mastery
            from world.forms import FORMS, get_transformation_duration
            if args not in FORMS:
                caller.msg(f"Unknown form: {args}")
                return
            
            mastery = (caller.db.form_mastery or {}).get(args, 0)
            duration = get_transformation_duration(caller, args)
            
            if mastery >= 100:
                caller.msg(f"{FORMS[args]['name']}: |c100%|n (can hold indefinitely)")
            else:
                caller.msg(f"{FORMS[args]['name']}: |c{mastery}%|n (can hold {duration:.0f} seconds)")
        else:
            # Show all form mastery
            display = get_form_mastery_display(caller)
            caller.msg(display)
            
            # Also show current transformation time remaining if active
            active = caller.db.active_form
            if active:
                from world.forms import get_transformation_time_remaining
                remaining, percentage, _ = get_transformation_time_remaining(caller)
                if remaining > 0:
                    caller.msg(f"\n|cCurrent form:|n {active} - |y{remaining:.0f}s|n remaining ({percentage:.0f}%)")


class CmdPush(Command):
    """
    Push energy into a beam clash.
    
    Usage: push
    
    When in a beam clash, use this command to push energy into the struggle.
    Timing matters - push when the beam is close to your opponent for maximum effect.
    """
    key = "push"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check if there's an active beam clash in the room
        if not caller.location:
            caller.msg("You need to be in a room to push.")
            return
        
        clash = get_beam_clash(caller.location)
        if not clash:
            caller.msg("There's no beam clash happening right now.")
            return
        
        # Check if caller is part of this clash
        if caller != clash.p1 and caller != clash.p2:
            caller.msg("You're not part of this beam clash!")
            return
        
        # Calculate timing bonus (closer to opponent = bigger bonus)
        timing_bonus = 0
        if caller == clash.p1 and clash.position < 40:
            timing_bonus = 5  # Good timing when pushing toward enemy
        elif caller == clash.p2 and clash.position > 60:
            timing_bonus = 5  # Good timing when pushing toward enemy
        
        # Push!
        result = clash.push(caller, timing_bonus)
        
        if result == "continuing":
            caller.msg(f"|cYou push energy into the beam!|n\n{clash.get_position_display()}")
            # Also show to room
            caller.location.msg_contents(
                f"{caller.key} pushes energy into the beam!",
                exclude=caller
            )
        elif result == "p1_wins" and caller == clash.p1:
            caller.msg("|gYou overwhelm the beam and strike your opponent!|n")
        elif result == "p2_wins" and caller == clash.p2:
            caller.msg("|gYou overwhelm the beam and strike your opponent!|n")
        elif result == "p1_wins":
            caller.msg("|rYour beam is overwhelmed!|n")
        elif result == "p2_wins":
            caller.msg("|rYour beam is overwhelmed!|n")


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
        loc = caller.location
        if not loc:
            caller.msg("You are nowhere.")
            return

        if "Kame Island" in loc.tags.get(category="zone", return_list=True) or "Kame Island" in loc.key:
            self._render_kame_map(loc)
        else:
            caller.msg("No map is available for your current area.")

    def _render_kame_map(self, loc):
        is_indoor = "Kame House" in loc.key

        base_indoor = """
==============================================================================
                               |y[|c KAME HOUSE |y]|n 

               |x+---------------------+|n                                |x+---------------------+|n
               |x||n       |cKITCHEN|n       |x||n                                |x||n      |cUPSTAIRS|n       |x||n
               |x||n         {k}         |x||n                                |x||n       |cBEDROOM|n       |x||n
               |x||n                     |x||n                                |x||n         {b}         |x||n
               |x+---------+   +---------+|n                                |x||n                     |x||n
                         |   |                                          |x+---------------------+|n
  |x+------------+|n         |   |
  |x||n  |cBATHROOM|n  |x+---------+   +---------+|n
  |x||n    {a}           |cLIVING ROOM|n     |x||n
  |x||n                      {l}         |x||n
  |x+------------+|x+---------+   +---------+|n
                         |   |
               |x+---------+   +---------+|n
               |x||n        |cPORCH|n        |x||n
               |x||n         {p}         |x||n
               |x+-----------------------+|n

==============================================================================
"""

        base_outdoor = """
==============================================================================
                               |y[|c KAME ISLAND |y]|n                                

         |B≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈|n           
      |B≈  ≈  ≈  ≈  ≈  ≈|n  |y.  .  .  .  .  .  .  .  .  .|n  |B≈  ≈  ≈  ≈  ≈  ≈|n       
   |B≈  ≈  ≈  ≈|n  |y.  .  . {n} .  .  .  . {N} .  .  .  .  . |n|B≈  ≈  ≈  ≈|n       
      |B≈  ≈|n  |y.  .  .  |G,  .  ,  .  ,  .  ,  .  ,  .  ,  .|y  .  .  .|n|B≈  ≈|n          
   |B≈  ≈|n  |y.  .  .  . |G.  ,  .  |W+-------+|G  .  ,  .  ,  .  , |y .  .  .|n |B≈  ≈|n       
|B≈ {w} ≈|n |y. {W} |n|G ,  .  ,  . |RKAME   |W||G  .  ,  .  ,  .  ,  |y. {E} .|n|B≈ {e} ≈|n
   |B≈  ≈|n  |y.  .  .  . |G.  ,  .  |W| HOUSE ||G  .  ,  .   |g\\|G   , |y .  .  .|n |B≈  ≈|n       
      |B≈  ≈|n  |y.  .  .  |G,  .  ,  |W+- |w{p}|W -+|G  .  ,  . |g(`)|G .|y  .  .  .|n  |B≈  ≈|n          
   |B≈  ≈  ≈  ≈|n  |y.  .  .  .  .  .  . {S} .  .  .  .  .  .  .|n  |B≈  ≈  ≈  ≈|n       
      |B≈  ≈  ≈  ≈  ≈  ≈|n  |y.  .  .  .  .  .  .  .  .  .|n  |B≈  ≈  ≈  ≈  ≈  ≈|n       
         |B≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈ {s} ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈|n           

==============================================================================
"""

        n = {k: "|Y(O)|n" for k in [
            "n", "s", "e", "w", 
            "N", "S", "E", "W", 
            "p", "k", "a", "l", "b"
        ]}
        
        curr = loc.key
        marker = "|r(@)|n"
        
        if "Ocean" in curr:
            desc = loc.db.desc.lower() if loc.db.desc else ""
            if "sits to the north" in desc: n["s"] = marker
            elif "sits to the south" in desc: n["n"] = marker
            elif "sits to the west" in desc: n["e"] = marker
            elif "sits to the east" in desc: n["w"] = marker
            else: n["n"] = marker
        elif "North" in curr or "Rear" in curr: n["N"] = marker
        elif "South" in curr: n["S"] = marker
        elif "East" in curr: n["E"] = marker
        elif "West" in curr: n["W"] = marker
        elif "Kitchen" in curr: n["k"] = marker
        elif "Bathroom" in curr: n["a"] = marker
        elif "Living" in curr: n["l"] = marker
        elif "Porch" in curr: n["p"] = marker
        elif "Bedroom" in curr: n["b"] = marker

        if is_indoor:
            self.caller.msg(base_indoor.format(**n).strip("\n"))
        else:
            self.caller.msg(base_outdoor.format(**n).strip("\n"))


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


class CmdSpiritBomb(Command):
    """
    Charge and release a Spirit Bomb - room-destroying energy orb.
    """
    key = "spiritbomb"
    aliases = ["sb"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Check ki control requirement
        if (caller.db.ki_control or 0) < 25:
            caller.msg("Your ki control is too low to form a Spirit Bomb (need 25).")
            return
        
        # Get or create spirit bomb
        sb = get_spirit_bomb(caller)
        
        if args in {"charge", "start", "begin"}:
            # Start charging
            if sb.is_charging:
                caller.msg("You are already charging a Spirit Bomb!")
                return
            sb.start_charge()
            caller.msg("|rYou begin gathering energy for a Spirit Bomb...|n")
            # Announce to room
            caller.location.msg_contents(
                f"{caller.key} begins gathering energy, a glowing orb forming in their hands!",
                exclude=caller
            )
            
        elif args in {"release", "fire", "launch"}:
            # Release the Spirit Bomb
            if not sb.is_charging:
                caller.msg("You aren't charging a Spirit Bomb!")
                return
            
            # Calculate damage
            charge_time = 20  # Default if just typed release
            damage = sb.calculate_damage(charge_time)
            
            # Get targets in room
            targets = []
            if caller.location:
                for obj in caller.location.contents:
                    if obj != caller and hasattr(obj, 'take_damage'):
                        targets.append(obj)
            
            # Apply AoE damage
            results = []
            for target in targets:
                actual = target.take_damage(damage, 'spirit_bomb')
                results.append(f"{target.key} takes {actual} damage!")
            
            # Clear bomb
            clear_spirit_bomb(caller)
            
            # Messages
            caller.msg(f"|rYou release the Spirit Bomb for {damage} damage!|n")
            if results:
                caller.location.msg_contents(
                    f"{caller.key} releases a massive Spirit Bomb! " + " ".join(results),
                    exclude=caller
                )
            else:
                caller.location.msg_contents(
                    f"{caller.key} releases a massive Spirit Bomb into the empty air!",
                    exclude=caller
                )
                
        elif args in {"cancel", "stop", "abort"}:
            # Cancel the Spirit Bomb (can be interrupted)
            if not sb.is_charging:
                caller.msg("You aren't charging a Spirit Bomb!")
                return
            
            # Interrupt - caster takes damage
            result = sb.interrupt()
            clear_spirit_bomb(caller)
            caller.msg(f"|rThe Spirit Bomb dissipates violently, harming you for {result['self_damage']} damage!|n")
            caller.location.msg_contents(
                f"{caller.key}'s Spirit Bomb explodes in their face!",
                exclude=caller
            )
            
        else:
            caller.msg("Usage: spiritbomb charge | release | cancel")


class CmdFlurry(Command):
    """
    Execute a Flurry Attack - rapid multiple strikes.
    """
    key = "flurry"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check technique level
        if not FlurryAttack.can_trigger(caller):
            caller.msg("Your technique level is too low to perform a Flurry Attack (need 5+).")
            return
        
        # Check if in combat
        if not getattr(caller, 'db', None) or not caller.db.combat_state:
            caller.msg("You must be in combat to use Flurry Attack.")
            return
        
        # Find target
        if not self.args:
            caller.msg("Usage: flurry <target>")
            return
        
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        
        # Check target is valid combatant
        if not hasattr(target, 'take_damage'):
            caller.msg("You can't attack that!")
            return
        
        # Check is in same room
        if target.location != caller.location:
            caller.msg("That target isn't here.")
            return
        
        # Base damage calculation
        pl = caller.db.power_level or 100
        base_damage = int(pl * 0.3)
        
        # Execute flurry
        result = FlurryAttack.execute(caller, target, base_damage)
        
        if result:
            msg = f"|yYou unleash a FLURRY of {result['num_strikes']} strikes!|n\n"
            msg += "\n".join(result['messages'])
            msg += f"\n|yTotal damage: {result['total_damage']}|n"
            caller.msg(msg)
            
            target.msg(f"|r{caller.key} unleashes a flurry of strikes on you!|n")
            caller.location.msg_contents(
                f"{caller.key} unleashes a flurry of strikes on {target.key}!",
                exclude=[caller, target]
            )


class CmdFuse(Command):
    """
    Accept or decline Namekian fusion offers.
    """
    key = "fuse"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Check if Namekian
        race = getattr(caller.db, 'race', None)
        if race != 'namekian':
            caller.msg("Only Namekians can use fusion.")
            return
        
        if args in {"accept", "yes"}:
            offer_id = getattr(caller.db, 'pending_fusion_offer', None)
            if not offer_id:
                caller.msg("You have no pending fusion offers.")
                return
            
            success, msg = accept_fusion(caller, offer_id)
            caller.msg(msg)
            if success:
                caller.location.msg_contents(
                    f"{caller.key} fuses with their partner! Their aura explodes with power!",
                    exclude=caller
                )
            
        elif args in {"decline", "no"}:
            offer_id = getattr(caller.db, 'pending_fusion_offer', None)
            if not offer_id:
                caller.msg("You have no pending fusion offers.")
                return
            
            success, msg = decline_fusion(caller, offer_id)
            caller.msg(msg)
            
        elif args in {"unfuse", "separate"}:
            success, msg = unfuse(caller)
            caller.msg(msg)
            if success:
                caller.location.msg_contents(
                    f"{caller.key} separates from their fusion partner.",
                    exclude=caller
                )
            
        elif args in {"status", "check"}:
            status = get_fusion_status(caller)
            if not status:
                caller.msg("You are not currently fused.")
            else:
                caller.msg(
                    f"Fused with: {status['partner']}\n"
                    f"KI Bonus: {status['ki_bonus']}\n"
                    f"Type: namekian_fusion"
                )
        else:
            caller.msg("Usage: fuse accept | decline | unfuse | status")


class CmdTimeskip(Command):
    """
    Teleport behind your target (requires 50% of target's PL).
    """
    key = "timeskip"
    aliases = ["ts"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: timeskip <target>")
            return
        
        target = _search_target(caller, self.args.strip())
        if not target:
            return
        
        success, msg = timeskip(caller, target)
        caller.msg(msg)
        if success:
            target.msg(f"{caller.key} appears behind you!")
            caller.location.msg_contents(
                f"{caller.key} vanishes and appears behind {target.key}!",
                exclude=[caller, target]
            )


class CmdTeleport(Command):
    """
    Save and teleport to locations.
    """
    key = "teleport"
    aliases = ["tp"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show saved locations
            locations = get_saved_locations(caller)
            if locations:
                caller.msg("\n".join(locations))
            else:
                caller.msg("No saved locations. Use 'teleport save <name>' to save a location.")
            return
        
        parts = args.split()
        action = parts[0]
        
        if action == "save":
            if len(parts) < 2:
                caller.msg("Usage: teleport save <name>")
                return
            location_name = " ".join(parts[1:])
            success, msg = save_teleport_location(caller, location_name)
            caller.msg(msg)
            
        elif action == "to":
            if len(parts) < 2:
                caller.msg("Usage: teleport to <name>")
                return
            location_name = " ".join(parts[1:])
            success, msg = teleport_to_location(caller, location_name)
            caller.msg(msg)
            
        else:
            # Try to teleport to location
            success, msg = teleport_to_location(caller, args)
            caller.msg(msg)


class CmdInstantTransmission(Command):
    """
    Instant Transmission - teleport to an ally.
    """
    key = "instanttransmission"
    aliases = ["it"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        target_name = self.args.strip() if self.args else None
        
        success, msg = instant_transmission(caller, target_name)
        caller.msg(msg)
        if success and target_name:
            caller.location.msg_contents(
                f"{caller.key} vanishes in a flash of light!",
                exclude=caller
            )


class CmdDragonBall(Command):
    """
    Collect and manage Dragon Balls.
    """
    key = "dragonball"
    aliases = ["db"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show Dragon Ball status
            status = get_dragon_ball_status(caller)
            balls = status.get('collected', [])
            msg = f"Dragon Balls collected: {status['count']}/7\n"
            if balls:
                msg += f"Balls: {', '.join(str(b) for b in balls)}\n"
            else:
                msg += "You have no Dragon Balls yet.\n"
            
            if status.get('shenron_active'):
                msg += f"\n|cShenron is active! {status['wishes_remaining']} wishes remaining!|n\n"
                msg += "Use 'wish <1-6>' to make a wish."
            
            caller.msg(msg)
            return
        
        # Handle subcommands
        parts = args.split()
        action = parts[0]
        
        if action == "collect" and len(parts) > 1:
            # For testing/giving - add a dragon ball
            try:
                ball_num = int(parts[1])
                if 1 <= ball_num <= 7:
                    add_dragon_ball(caller, ball_num)
                    caller.msg(f"You obtained Dragon Ball #{ball_num}!")
                else:
                    caller.msg("Dragon Ball number must be 1-7.")
            except:
                caller.msg("Usage: dragonball collect <1-7>")
        else:
            caller.msg("Usage: dragonball [collect <n>|status]")


class CmdSummonShenron(Command):
    """
    Summon Shenron when all 7 Dragon Balls are collected.
    """
    key = "summon_shenron"
    aliases = ["summon"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        if not can_summon_shenron(caller):
            status = get_dragon_ball_status(caller)
            caller.msg(f"You need all 7 Dragon Balls to summon Shenron. You have {status['count']}/7.")
            return
        
        success, msg = summon_shenron(caller)
        caller.msg(msg)
        
        if success:
            caller.location.msg_contents(
                f"{caller.key} summons the eternal dragon Shenron! The sky darkens...",
                exclude=caller
            )


class CmdWish(Command):
    """
    Make a wish from Shenron.
    """
    key = "wish"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: wish <1-6>\n1. Power Boost (+50% PL)\n2. Stat Increase (+20% all)\n3. Unlock Transformation\n4. Heal Full\n5. Revive Ally\n6. Knowledge (XP boost)")
            return
        
        try:
            wish_num = int(self.args.strip())
        except:
            caller.msg("Usage: wish <1-6>")
            return
        
        if not 1 <= wish_num <= 6:
            caller.msg("Wish number must be 1-6.")
            return
        
        success, msg = make_wish(caller, wish_num)
        caller.msg(msg)


class CmdPlanetCracker(Command):
    """
    Use the devastating Planet Cracker technique.
    Requires 1M+ PL, once per day, 10% success rate.
    """
    key = "planetcracker"
    aliases = ["pc"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        can_use, error = can_use_planet_cracker(caller)
        if not can_use:
            caller.msg(error)
            return
        
        result = use_planet_cracker(caller)
        caller.msg(result['message'])
        
        if result.get('success'):
            caller.location.msg_contents(
                f"{caller.key} unleashes a devastating PLANET CRACKER! The ground shakes!",
                exclude=caller
            )


class CmdTrainWith(Command):
    """
    Train with master NPCs for XP bonuses.
    """
    key = "trainwith"
    aliases = ["train"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show available trainers
            trainers = get_available_trainers(caller)
            if not trainers:
                caller.msg("No trainers available yet. Build up your PL!")
                return
            
            msg = "|cAvailable Trainers:|n\n"
            for t in trainers:
                msg += f"  {t['name']} ({t['location']})\n"
                msg += f"    Specialty: {t['specialty']}\n"
                msg += f"    XP Bonus: {t['bonus']}x\n"
                msg += f"    PL Required: {t['prereq_pl']:,}\n\n"
            
            msg += "Use 'trainwith <trainer>' to train."
            caller.msg(msg)
            return
        
        # Train with specific trainer
        success, msg = train_with_npc(caller, args)
        caller.msg(msg)


# =============================================================================
# STATUS EFFECTS COMMANDS
# =============================================================================


class CmdStatus(Command):
    """
    View your current status effects.
    
    Usage: status
    
    Shows all active buff and debuff effects currently affecting you.
    """
    key = "status"
    aliases = ["effects", "affects"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.status_effects import get_status_display
        caller = self.caller
        caller.msg(get_status_display(caller))


class CmdClearStatus(Command):
    """
    Clear status effects from yourself or a target.
    
    Usage: clearstatus [debuffs|buffs|all] [target]
    
    Examples:
      clearstatus debuffs   - Remove all debuffs from yourself
      clearstatus buffs     - Remove all buffs from yourself
      clearstatus all       - Remove all effects from yourself
      clearstatus all enemy - Remove all effects from enemy
    """
    key = "clearstatus"
    aliases = ["cs", "cleanse", "dispel"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.status_effects import remove_all_debuffs, remove_all_buffs, remove_status
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Parse arguments
        parts = args.split() if args else ["debuffs"]
        clear_type = parts[0]
        target = None
        
        # Check for target
        if len(parts) > 1:
            target_name = " ".join(parts[1:])
            target = caller.search(target_name)
            if not target:
                return
        else:
            target = caller
        
        # Perform clear
        if clear_type in ["debuff", "debuffs"]:
            count = remove_all_debuffs(target)
            caller.msg(f"Removed {count} debuffs from {target.name}.")
        elif clear_type in ["buff", "buffs"]:
            count = remove_all_buffs(target)
            caller.msg(f"Removed {count} buffs from {target.name}.")
        elif clear_type == "all":
            debuffs = remove_all_debuffs(target)
            buffs = remove_all_buffs(target)
            caller.msg(f"Removed {debuffs} debuffs and {buffs} buffs from {target.name}.")
        else:
            caller.msg("Usage: clearstatus [debuffs|buffs|all] [target]")


class CmdStatusInfo(Command):
    """
    View information about all status effects.
    
    Usage: statusinfo
    
    Shows a list of all available status effects and their descriptions.
    """
    key = "statusinfo"
    aliases = ["si", "effectinfo"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.status_effects import get_all_status_info
        caller = self.caller
        caller.msg(get_all_status_info())


# =============================================================================
# INVENTORY & EQUIPMENT COMMANDS
# =============================================================================


class CmdInventory(Command):
    """
    View your inventory and equipment.
    
    Usage: inventory
           inv
    
    Shows all items you are carrying and currently equipped.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.inventory import get_inventory_display
        caller = self.caller
        caller.msg(get_inventory_display(caller))


class CmdUse(Command):
    """
    Use an item from your inventory.
    
    Usage: use <item>
    
    Examples:
      use senzu_bean   - Use a senzu bean
      use energy_drink - Use an energy drink
      use antidote     - Use an antidote to cure debuffs
    """
    key = "use"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.inventory import use_item, ITEM_DEFINITIONS
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            caller.msg("Usage: use <item>")
            return
        
        success, msg = use_item(caller, args)
        if success:
            caller.msg(msg)
        else:
            caller.msg(f"|r{msg}|n")


class CmdEquip(Command):
    """
    Equip an item from your inventory.
    
    Usage: equip <item>
           equip <slot>
    
    Examples:
      equip weighted_clothing_heavy
      equip scouter
      equip clothing   - See what's in clothing slot
    """
    key = "equip"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.inventory import equip_item, unequip_item, get_equipped, ITEM_DEFINITIONS
        from world.status_effects import get_all_status_info
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            caller.msg("Usage: equip <item>")
            return
        
        # Check for slot query
        if args in ["clothing", "accessory", "pod"]:
            current = get_equipped(caller, args)
            if current:
                item_def = ITEM_DEFINITIONS.get(current, {})
                caller.msg(f"Currently equipped in {args}: {item_def.get('name', current)}")
            else:
                caller.msg(f"Nothing equipped in {args} slot.")
            return
        
        success, msg = equip_item(caller, args)
        if success:
            caller.msg(f"|g{msg}|n")
        else:
            caller.msg(f"|r{msg}|n")


class CmdUnequip(Command):
    """
    Unequip an item from a slot.
    
    Usage: unequip <slot>
    
    Examples:
      unequip clothing
      unequip accessory
    """
    key = "unequip"
    aliases = ["uneq"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.inventory import unequip_item
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            caller.msg("Usage: unequip <clothing|accessory|pod>")
            return
        
        if args not in ["clothing", "accessory", "pod"]:
            caller.msg("Invalid slot. Use: clothing, accessory, or pod")
            return
        
        success, msg = unequip_item(caller, args)
        if success:
            caller.msg(f"|g{msg}|n")
        else:
            caller.msg(f"|r{msg}|n")


class CmdDrop(Command):
    """
    Drop an item from your inventory.
    
    Usage: drop <item> [amount]
    
    Examples:
      drop senzu_bean
      drop zeni 100
    """
    key = "drop"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.inventory import remove_item, get_item_count, ITEM_DEFINITIONS
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            caller.msg("Usage: drop <item> [amount]")
            return
        
        parts = args.split()
        item_key = parts[0]
        quantity = int(parts[1]) if len(parts) > 1 else 1
        
        if not has_item(caller, item_key):
            caller.msg("You don't have that item.")
            return
        
        if remove_item(caller, item_key, quantity):
            item_def = ITEM_DEFINITIONS.get(item_key, {})
            name = item_def.get("name", item_key)
            caller.msg(f"|yYou dropped {name} x{quantity}.|n")
        else:
            caller.msg("Failed to drop item.")


# =============================================================================
# PARTY SYSTEM COMMANDS
# =============================================================================


class CmdParty(Command):
    """
    Manage party/team functionality.
    
    Usage:
      party                 - Show party info
      party create <name>   - Create new party
      party invite <player> - Invite player
      party accept          - Accept invitation
      party decline         - Decline invitation
      party leave           - Leave party
      party kick <player>   - Kick player (leader)
      party info            - View party info
      party chat <msg>      - Chat with party
    
    Party Benefits:
      - XP sharing bonuses (25-50%)
      - Damage bonuses when fighting together
      - Party buffs
    """
    key = "party"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.party_system import PartyCommand
        caller = self.caller
        result = PartyCommand.handle(caller, self.args)
        if result:
            caller.msg(result)


# =============================================================================
# WORLD BOSS COMMANDS
# =============================================================================


class CmdBoss(Command):
    """
    Manage World Boss events.
    
    Usage:
      boss              - Show boss status
      boss info         - Show boss status
      boss attack       - Join the fight
      boss list         - List available bosses
    
    World Bosses:
      - Frieza (Tier 1): Cold-blooded emperor
      - Cell (Tier 2): Perfect bio-weapon  
      - Buu (Tier 3): Innocent evil
    
    Bosses spawn every 2 hours. Form a party and defeat them together!
    """
    key = "boss"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.world_boss import BossCommand
        caller = self.caller
        result = BossCommand.handle(caller, self.args)
        if result:
            caller.msg(result)


# =============================================================================
# FACTION/GUILD COMMANDS
# =============================================================================


class CmdFaction(Command):
    """
    Manage faction/guild membership.
    
    Usage:
      faction              - Show your faction info
      faction list         - List all factions
      faction join <name> - Join a faction
      faction leave       - Leave your faction
      faction info        - View faction details
      faction reputation  - Check your reputation
      faction techniques  - View faction techniques
    
    Factions:
      - Saiyan Army: Combat & transformation bonuses
      - Capsule Corp: Technology & item bonuses
      - Red Ribbon Army: Military & Zeni bonuses
      - Kame House: Technique mastery bonuses
      - Namekian Clan: Ki & regeneration bonuses
    """
    key = "faction"
    aliases = ["guild", "clan"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.guild_system import FactionCommand
        caller = self.caller
        result = FactionCommand.handle(caller, self.args)
        if result:
            caller.msg(result)


# =============================================================================
# HYPERBOLIC TIME CHAMBER COMMANDS
# =============================================================================


class CmdHTC(Command):
    """
    Manage Hyperbolic Time Chamber.
    
    Usage:
      htc              - Show HTC status
      htc enter       - Enter the HTC
      htc exit        - Exit the HTC
      htc gravity <1-100> - Set gravity
    
    The Hyperbolic Time Chamber provides 10x XP gain.
    Requires gravity_charge item to enter.
    """
    key = "htc"
    aliases = ["chamber", "timechamber"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.hyperbolic_time_chamber import HTCCommand
        caller = self.caller
        result = HTCCommand.handle(caller, self.args)
        if result:
            caller.msg(result)


# =============================================================================
# FLIGHT SYSTEM COMMANDS
# =============================================================================


class CmdFly(Command):
    """
    Take to the skies and fly.
    
    Usage:
      fly              - Take off into the air
      fly north/south/east/west/up/down - Fly in a direction
      fly to <place>  - Fast travel to unlocked location
      
    Flight States (PL requirements):
      Levitate:   1,000 PL - Hover above ground
      Flying:     5,000 PL - Full flight, 2x speed
      Super Speed: 50,000 PL - 3x speed, blur through air
    
    Examples:
      fly
      fly north
      fly to kame_house
    """
    key = "fly"
    aliases = ["fly", "hover", "soar"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.flight_system import FlightCommand, take_off, fly_direction, fly_to_location
        from world.flight_system import get_flight_state, FlightState
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # No args - take off
        if not args:
            current_state = get_flight_state(caller)
            if current_state != FlightState.GROUND:
                caller.msg("You are already flying!")
                return
            
            success, msg = take_off(caller)
            if success:
                caller.msg(msg)
            else:
                caller.msg(f"|r{msg}|n")
            return
        
        # Handle specific directions
        direction_map = {
            "n": "north", "north": "north",
            "s": "south", "south": "south",
            "e": "east", "east": "east",
            "w": "west", "west": "west",
            "u": "up", "up": "up",
            "d": "down", "down": "down",
        }
        
        if args in direction_map:
            success, msg = fly_direction(caller, args)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        # Handle "fly to <location>"
        if args.startswith("to "):
            location_name = args[3:].strip().lower().replace(" ", "_")
            success, msg = fly_to_location(caller, location_name)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        # Show help
        caller.msg(self.__doc__)


class CmdLand(Command):
    """
    Land on the ground from flight.
    
    Usage:
      land
    
    Returns you safely to the ground.
    Warning: Landing in combat may leave you vulnerable!
    """
    key = "land"
    aliases = ["land", "descend", "ground"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.flight_system import land, get_flight_state, FlightState
        
        caller = self.caller
        current_state = get_flight_state(caller)
        
        if current_state == FlightState.GROUND:
            caller.msg("You are already on the ground.")
            return
        
        success, msg = land(caller)
        caller.msg(msg if success else f"|r{msg}|n")


class CmdFlightStatus(Command):
    """
    Check your current flight status.
    
    Usage:
      flight status
      flight list
    
    Shows your current flight state, speed, and available
    fast travel points.
    """
    key = "flight"
    aliases = ["flight", "flight status", "flight list", "flying"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.flight_system import FlightCommand
        from world.flight_system import get_flight_status, get_fast_travel_list
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else "status"
        
        if args == "list" or args == "travel":
            caller.msg(get_fast_travel_list(caller))
        else:
            caller.msg(get_flight_status(caller))


# =============================================================================
# MENTOR SYSTEM COMMANDS
# =============================================================================


class CmdMentor(Command):
    """
    Interact with mentor system to learn techniques.
    
    Usage:
      mentor              - Show available mentors
      mentor list        - List all masters in the world
      learn <technique>  - Learn a technique from a mentor
    
    Masters:
      - Master Roshi: Kamehameha, Turtle Stance
      - King Kai: Kaioken, Spirit Ball
      - Piccolo: Special Beam Cannon, Light Grenade
      - And many more!
    
    Each master teaches unique techniques. Some require
    faction membership or quest completion.
    """
    key = "mentor"
    aliases = ["mentor", "learn", "masters"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.mentor_system import MentorCommand, learn_technique
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Handle "learn <technique>"
        if self.cmdstring == "learn" or args.startswith("learn "):
            if args.startswith("learn "):
                tech = args[6:].strip().lower().replace(" ", "_")
            else:
                caller.msg("Learn what? Usage: learn <technique_name>")
                return
            
            success, msg = learn_technique(caller, tech)
            caller.msg(msg if success else f"|r{msg}|n")
            return
        
        # Handle mentor command
        result = MentorCommand.handle(caller, args)
        if result:
            caller.msg(result)


# =============================================================================
# FRIENDS SYSTEM COMMANDS
# =============================================================================


class CmdFriend(Command):
    """
    Manage your friends list.
    
    Usage:
      friend              - View friends list
      friend add <name>   - Add a friend
      friend remove <name> - Remove a friend
      friend msg <name> <msg> - Send message to friend
    
    Friends can see when you're online and you can
    send quick messages to them.
    """
    key = "friend"
    aliases = ["friend", "friends", "flist"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.friends_system import FriendsCommand
        
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        result = FriendsCommand.handle(caller, args)
        if result:
            caller.msg(result)


# =============================================================================
# DUNGEON SYSTEM COMMANDS
# =============================================================================


class CmdDungeon(Command):
    """
    Manage dungeon exploration.
    
    Usage:
      dungeon              - Show current dungeon status
      dungeon list         - List available dungeons
      dungeon enter <name> - Enter a dungeon
      dungeon exit        - Exit current dungeon
      dungeon floor       - Show floor details
    
    Dungeons:
      - Muscle Tower: Red Ribbon Army fortress (5 floors)
      - Kaiō's Test: Otherworld training (5 floors)
      - Heart of Namek: Defend the village (3 floors)
      - Baba's Mansion: Haunted spirit realm (7 floors)
      - Capsule Corp Lab: Android confrontation (4 floors)
    
    Each floor has enemies to defeat. Boss on final floor!
    """
    key = "dungeon"
    aliases = ["dungeon", "dung"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        from world.dungeon_system import DungeonCommand
        caller = self.caller
        result = DungeonCommand.handle(caller, self.args)
        if result:
            caller.msg(result)
