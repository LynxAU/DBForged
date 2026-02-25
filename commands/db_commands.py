"""
Dragon Ball vertical-slice commands.

NOTE: This module now re-exports commands from specialized modules for
backward compatibility. New code should import directly from:
- commands.combat_cmds
- commands.character_cmds
- commands.social_cmds
"""

from __future__ import annotations

# Re-export from specialized modules for backward compatibility
from commands.combat_cmds import (
    CmdAttack, CmdFlee, CmdTarget, CmdCharge, CmdGuard, CmdCounter,
)
from commands.character_cmds import (
    CmdDBStats, CmdPlayerProfile, CmdTransform, CmdTech, CmdEquipTech,
    CmdListTech, CmdForms, CmdLSSJ, CmdRacials, CmdRacial,
    CmdScan, CmdSense, CmdSuppress, CmdFly,
)
from commands.social_cmds import (
    CmdQuests, CmdQuest, CmdTalk, CmdShop, CmdBuy, CmdSell, CmdInventory, CmdGuild,
)

# Legacy imports - some commands still live here
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
from world.tournaments import (
    get_tournament_state, get_world_boss_state, is_tournament_active, is_world_boss_active,
    open_tournament_signups, close_tournament_signups, join_tournament, leave_tournament,
    register_match_win, end_tournament, spawn_world_boss, damage_world_boss,
    get_world_boss_damage_leaderboard, try_spawn_world_boss, TOURNAMENT_INACTIVE,
    TOURNAMENT_SIGNUPS, TOURNAMENT_IN_PROGRESS, WORLD_BOSS_DURATION,
)
from world.guilds import (
    create_guild, get_guild, get_guild_by_name, get_player_guild, join_guild, leave_guild,
    invite_to_guild, kick_from_guild, promote_member, set_guild_motd, disband_guild,
    list_guilds, get_guild_members, GUILD_ROLE_LEADER, GUILD_ROLE_OFFICER, GUILD_ROLE_MEMBER,
    GUILD_CREATION_COST,
)


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


class CmdTarget(Command):
    key = "target"
    locks = "cmd:all()"
    help_category = "DB"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: target <name>")
            return
            
        target = _search_target(caller, self.args.strip())
        if not target or target == caller:
            return
        
        # SECURITY: Validate target is in same room
        if target.location != caller.location:
            caller.msg("You can only target someone in your current location.")
            return
        
        # SECURITY: Validate target is a valid combatant
        if not hasattr(target, "db") or target.db.hp_current is None:
            caller.msg("You cannot attack that.")
            return
            
        caller.db.combat_target = target.id
        caller.msg(f"Target set to {target.key}.")
        # Send target's stats back to caller for the Scouter HUD
        if hasattr(target, "get_current_pl"):
            emit_entity_delta(target, recipients=[caller])


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
        
        # Show strain status when checking form status
        if self.args.strip().lower() in {"status", "info", "strain"}:
            active = caller.db.active_form
            if not active:
                caller.msg("You are in base form.")
                return
            strain = getattr(caller.db, 'form_strain', 0)
            mastery = (caller.db.form_mastery or {}).get(active, 0)
            form = FORMS.get(active, {})
            gameplay = form.get("gameplay", {})
            drain_tick = form.get("drain_per_tick", 0)
            
            caller.msg(f"Active form: {form.get('name', active)}")
            caller.msg(f"Mastery: {mastery} | Ki drain/tick: {drain_tick}")
            
            if strain > 0 or gameplay.get("strain_accumulation", 0) > 0:
                bar = "|g" + "=" * (strain // 10) + "|r" + "-" * ((100 - strain) // 10) + "|n"
                caller.msg(f"Body Strain: {strain}/100")
                caller.msg(bar)
                if strain >= 80:
                    caller.msg("|rWARNING: Critical strain! Form may crash!|n")
            return
        
        if not self.args:
            caller.msg("Usage: transform <form> or transform status or revert")
            return
        form_key, form = get_form(self.args.strip())
        if not form:
            caller.msg("Unknown form.")
            return
        if caller.db.ki_current < 20 and form.get("resource_drain", {}).get("ki_per_tick", 0) > 0:
            caller.msg("You need at least 20 ki to transform.")
            return
        
        # Show strain warning for Kaioken forms with high strain accumulation
        gameplay = form.get("gameplay", {})
        if gameplay.get("strain_accumulation", 0) > 0:
            caller.msg("|yWARNING: This form accumulates body strain!|n")
        
        ok, msg, _stub = activate_form(caller, form_key, context={"command": "transform"})
        if not ok:
            caller.msg(msg)
            return
        caller.msg(f"|y{msg}|n Your {aura_phrase(caller.db.aura_color)} flares.")
        
        # Show strain info after transforming into high-strain forms
        if gameplay.get("strain_accumulation", 0) > 0:
            caller.msg("|yWatch your strain! Use 'transform status' to monitor.|n")
        
        emit_vfx(caller.location, form.get("vfx_id", "vfx_transform"), source=caller)
        emit_entity_delta(caller)


class CmdPotara(Command):
    """
    Initiate Potara Fusion with another player.
    
    Usage: potara <target>
    
    The Potara earrings allow two warriors to merge into one.
    This fusion is nearly permanent - it will last until you
    choose to unfuse.
    """
    key = "potara"
    aliases = ["fusion"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check if already fused
        from world.fusions import is_fused, format_fusion_status, send_fusion_request, has_pending_request
        
        if is_fused(caller):
            caller.msg(format_fusion_status(caller))
            caller.msg("Use 'unfuse' to end your current fusion.")
            return
        
        if has_pending_request(caller):
            caller.msg("You already have a pending fusion request. Wait for it to expire or use 'decline fusion' if you're the target.")
            return
        
        if not self.args:
            caller.msg("Usage: potara <player>")
            caller.msg("The Potara earrings merge two warriors into one being permanently.")
            caller.msg("The other player must accept your request.")
            return
        
        # Find target
        target_name = self.args.strip()
        target = caller.search(target_name, candidates=caller.location.contents_get(exclude=caller))
        
        if not target:
            caller.msg("Target not found. Make sure they're in the same room.")
            return
        
        # Check if target is a player (has db attributes we need)
        if not hasattr(target, 'db'):
            caller.msg(f"{target.key} is not a valid fusion target.")
            return
        
        # Send fusion request (will check requirements internally)
        ok, msg = send_fusion_request(caller, target, "potara")
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDance(Command):
    """
    Initiate Metamoran Dance Fusion with another player.
    
    Usage: dance <target>
    
    The Metamoran dance fuses two warriors into one for a limited
    time (30 minutes). This fusion is more powerful than Potara
    but temporary.
    """
    key = "dance"
    aliases = ["metamoran", "fusion_dance"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        from world.fusions import is_fused, send_fusion_request, format_fusion_status, has_pending_request
        
        if is_fused(caller):
            caller.msg(format_fusion_status(caller))
            caller.msg("Use 'unfuse' to end your current fusion.")
            return
        
        if has_pending_request(caller):
            caller.msg("You already have a pending fusion request. Wait for it to expire or use 'decline fusion' if you're the target.")
            return
        
        if not self.args:
            caller.msg("Usage: dance <player>")
            caller.msg("The Metamoran dance fuses two warriors for 30 minutes.")
            caller.msg("The other player must accept your request.")
            return
        
        # Find target
        target_name = self.args.strip()
        target = caller.search(target_name, candidates=caller.location.contents_get(exclude=caller))
        
        if not target:
            caller.msg("Target not found. Make sure they're in the same room.")
            return
        
        if not hasattr(target, 'db'):
            caller.msg(f"{target.key} is not a valid fusion target.")
            return
        
        # Send fusion request
        ok, msg = send_fusion_request(caller, target, "metamoran")
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdUnfuse(Command):
    """
    End your current fusion.
    
    Usage: unfuse
    
    Separates a Potara or Metamoran fusion back into the
    original two warriors.
    """
    key = "unfuse"
    aliases = ["defuse", "separate"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        from world.fusions import is_fused, unfuse, format_fusion_status
        
        if not is_fused(caller):
            caller.msg("You are not currently fused.")
            return
        
        ok, msg = unfuse(caller)
        if ok:
            caller.msg(f"|g{msg}|n")
            caller.location.msg_contents(
                f"{caller.key} suddenly splits into two separate beings!",
                exclude=[caller]
            )
        else:
            caller.msg(f"|r{msg}|n")


class CmdFusionStatus(Command):
    """
    Check your current fusion status.
    
    Usage: fusion
    
    Shows information about your current fusion, including
    partner and remaining time (for Metamoran).
    """
    key = "fusion"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        from world.fusions import is_fused, format_fusion_status, get_fusion_time_remaining, is_metamoran_fusion
        
        if not is_fused(caller):
            caller.msg("You are not currently in a fusion.")
            caller.msg("Use 'potara <target>' or 'dance <target>' to fuse with another warrior.")
            return
        
        caller.msg(format_fusion_status(caller))
        
        # Show additional info
        from world.fusions import get_fusion_data
        data = get_fusion_data(caller)
        if data:
            caller.msg(f"Fusion type: {data.get('type', 'unknown').title()}")
            if is_metamoran_fusion(caller):
                remaining = get_fusion_time_remaining(caller)
                minutes = remaining // 60
                seconds = remaining % 60
                caller.msg(f"Time remaining: |y{minutes}m {seconds}s|n")


class CmdAcceptFusion(Command):
    """
    Accept a fusion request from another player.
    
    Usage: accept fusion
    """
    key = "accept"
    aliases = ["accept fusion"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if args and args != "fusion":
            caller.msg("Usage: accept fusion")
            return
        
        from world.fusions import accept_fusion, has_pending_request
        
        if not has_pending_request(caller):
            caller.msg("You don't have any pending fusion requests.")
            caller.msg("Use 'potara <player>' or 'dance <player>' to send a fusion request.")
            return
        
        ok, msg = accept_fusion(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")
        # Success messages are handled in accept_fusion


class CmdDeclineFusion(Command):
    """
    Decline a fusion request from another player.
    
    Usage: decline fusion
    """
    key = "decline"
    aliases = ["decline fusion", "refuse"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if args and args != "fusion":
            caller.msg("Usage: decline fusion")
            return
        
        from world.fusions import decline_fusion, has_pending_request
        
        if not has_pending_request(caller):
            caller.msg("You don't have any pending fusion requests to decline.")
            return
        
        ok, msg = decline_fusion(caller)
        if ok:
            caller.msg(f"|g{msg}|n")


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
        
        # Handle item/consumable effects
        tech_category = tech.get("category", "")
        if tech_category == "item":
            # Senzu bean - full heal
            caller.db.hp_current = caller.db.hp_max
            caller.db.ki_current = caller.db.ki_max
            caller.heal_all_limbs()
            caller.msg("|g>>> SENZU BEAN CONSUMED! <<<|n Full HP/KI restored, all limbs healed!")
            emit_vfx(caller.location, "vfx_heal", source=caller)
            emit_entity_delta(caller)
            return
        
        # Handle location healing (healing chambers)

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
        
        # Android heat generation
        race = (caller.db.race or "").lower()
        if race == "android":
            heat_gain = int(tech.get("ki_cost", 10) * 0.8)  # 80% of ki cost as heat
            caller.db.android_heat = min(100, (caller.db.android_heat or 0) + heat_gain)
        
        # Check limb requirements for techniques
        limbs = caller.db.limbs or {}
        tech_tags = tech.get("tags", [])
        
        # Check for melee/leg techniques
        if "melee" in tech_tags or "kick" in str(tech_key).lower() or "leg" in str(tech_key).lower():
            left_leg = limbs.get("left_leg", {}).get("state", "intact")
            right_leg = limbs.get("right_leg", {}).get("state", "intact")
            if left_leg in ["broken", "lost"] and right_leg in ["broken", "lost"]:
                caller.msg("|rYou can't perform melee attacks - both legs are too damaged!|n")
                return
            if left_leg == "broken" or right_leg == "broken":
                caller.msg("|yYour legs are damaged - melee attacks weakened!|n")
        
        if "punch" in str(tech_key).lower() or "strike" in str(tech_key).lower() or "melee" in tech_tags:
            left_arm = limbs.get("left_arm", {}).get("state", "intact")
            right_arm = limbs.get("right_arm", {}).get("state", "intact")
            if left_arm in ["broken", "lost"] and right_arm in ["broken", "lost"]:
                caller.msg("|rYou can't perform melee attacks - both arms are too damaged!|n")
                return
            if left_arm == "broken" or right_arm == "broken":
                caller.msg("|yYour arms are damaged - melee attacks weakened!|n")
        
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


class CmdCombatHUD(Command):
    """
    Display combat HUD showing equipped abilities
    
    Usage:
      hud
    
    Shows your equipped techniques in combat format.
    """
    key = "hud"
    aliases = ["abilities", "ab"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        equipped = list(caller.db.equipped_techniques or [])
        if not equipped:
            caller.msg("No techniques equipped. Use 'equiptech <name>' to equip one.")
            return
        
        # Get technique details
        techs = []
        for i, tech_key in enumerate(equipped[:4], 1):
            if tech_key in TECHNIQUES:
                tech = TECHNIQUES[tech_key]
                cd = _cooldown_remaining(caller, tech_key)
                cd_str = f"|rCD:{cd:.1f}|n" if cd > 0 else "     "
                ki_cost = tech.get("ki_cost", 0)
                techs.append(f"[|w{i}|n] {tech['name'][:18]:<18} {cd_str} |c{ki_cost} Ki|n")
        
        # Build HUD
        hud = [
            "",
            "|b╔═══════════════════════════════════════╗|n",
            "|b║        |wCOMBAT HUD|n                    |b║|n",
            "|b╠═══════════════════════════════════════╣|n",
        ]
        
        # Two columns for abilities
        for i in range(0, len(techs), 2):
            col1 = techs[i] if i < len(techs) else "" 
            col2 = techs[i+1] if i+1 < len(techs) else ""
            hud.append(f"|b║  {col1:<25}  {col2:<25}|n")
        
        # Guard status
        guard_active = caller.has_status("guard")
        guard_str = "{YON {x" if guard_active else "{dOFF{x"
        
        # Add charge and guard options
        hud.extend([
            "|b╠═══════════════════════════════════════╣|n",
            f"|b║  [|wC|n] Charge           [|wG|n] Guard: {guard_str:10s} |n",
            "|b║  [|wB|n] Block/Guard     [|wF|n] Flee            |n",
            "|b║  [|wR|n] Revert Form    [|wT|n] Transform       |n",
            "|b╚═══════════════════════════════════════╝|n",
            "",
        ])
        
        caller.msg("\n".join(hud))


class CmdGuard(Command):
    """
    Enter defensive stance.
    Usage: guard
           guard on
           guard off
    
    Guard reduces incoming damage by 50%. You cannot
    attack while guarding. Guard costs 5 ki per use.
    """
    key = "guard"
    aliases = ["block", "defend", "g"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else "toggle"
        
        # Check if in combat
        if not caller.db.combat_id:
            caller.msg("You can only guard during combat!")
            return
        
        current_guard = caller.has_status("guard")
        
        if args in ["on", "toggle"] and not current_guard:
            # Turn on guard
            ki_cost = 5
            current_ki = caller.db.ki_current or 0
            if current_ki < ki_cost:
                caller.msg(f"You need {ki_cost} ki to maintain guard stance.")
                return
            
            caller.db.ki_current = max(0, current_ki - ki_cost)
            caller.add_status("guard", 30, reduction=0.50)
            caller.msg("{YYou raise your guard, preparing to block incoming attacks!{x")
            if caller.location:
                caller.location.msg_contents(f"{caller.key} raises their guard!", exclude=caller)
            return
        
        if args in ["off", "toggle"] and current_guard:
            # Turn off guard
            caller.remove_status("guard")
            caller.msg("{YYou lower your guard.{x")
            return
        
        if current_guard and args in ["on", "toggle"]:
            caller.msg("You are already guarding! Use 'guard off' to lower it.")
        elif not current_guard and args in ["off", "toggle"]:
            caller.msg("You aren't guarding! Use 'guard on' to raise it.")
        else:
            caller.msg("Usage: guard [on/off/toggle]")


class CmdCounter(Command):
    """
    Counter an enemy's attack.
    Usage: counter
    
    Wait for an enemy to attack, then counter for
    bonus damage + stun. Must be used within 2 seconds
    of being attacked.
    """
    key = "counter"
    aliases = ["ct"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check if in combat
        if not caller.db.combat_id:
            caller.msg("You can only counter during combat!")
            return
        
        # Check for counter window (after being attacked)
        counter_window = caller.db.counter_window or 0
        import time
        now = time.time()
        
        if now - counter_window > 2:  # 2 second window
            caller.msg("You need to time your counter after an enemy's attack! Watch for the 'counter window' cue.")
            return
        
        # Get the attacker
        target = caller.db.last_attacker
        if not target:
            caller.msg("There's no one to counter right now!")
            return
        
        # Check if target is still in room
        if not target.location or target.location != caller.location:
            caller.msg("Your target is no longer here!")
            return
        
        # Apply counter damage
        caller.db.ki_current = max(0, (caller.db.ki_current or 0) - 15)
        
        # Counter is a critical hit
        from world.power import calculate_gap
        gap = calculate_gap(caller, target)
        base_damage = int(caller.db.base_power * 0.8)
        damage = int(base_damage * gap.get("damage_mult", 1.0) * 1.5)
        
        target.apply_damage(damage, source=caller, kind="counter")
        
        # Stun the target
        target.add_status("stunned", 3)
        
        caller.msg(f"{{YYou counter {target.key}'s attack! {{r{damage} damage!{{x")
        msg = f"{caller.key} counters {target.key}'s attack!"
        caller.location.msg_contents("{|Y" + msg + "{|x", exclude=caller)
        
        # Clear counter window
        caller.db.counter_window = 0


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
    aliases = ["learn", "practice"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Find trainer in room
        trainer = None
        trainer_key = None
        for obj in caller.location.contents:
            if _is_npc(obj) and obj.db.npc_role == "trainer":
                trainer = obj
                trainer_key = obj.db.trainer_key or obj.db.npc_content_key
                break
        
        if not trainer:
            caller.msg("No trainer is available here.")
            return
        
        # Handle arguments - learn <technique>
        if self.args.strip():
            # Player wants to learn a specific technique
            tech_key, tech = get_technique(self.args.strip())
            if not tech:
                caller.msg("Unknown technique. Use 'train' alone to see available techniques.")
                return
            
            # Get trainer's available techniques
            from world.npc_content import get_npc_definition
            npc_def = get_npc_definition(trainer_key) if trainer_key else {}
            trainer_techs = npc_def.get("trainer_rewards", {}).get("techniques", [])
            
            if tech_key not in trainer_techs:
                caller.msg(f"{trainer.key} doesn't teach that technique.")
                return
            
            if tech_key in (caller.db.known_techniques or []):
                caller.msg("You already know that technique.")
                return
            
            # Learn the technique
            known = list(caller.db.known_techniques or [])
            known.append(tech_key)
            caller.db.known_techniques = known
            
            # Auto-equip if has room
            equipped = list(caller.db.equipped_techniques or [])
            if len(equipped) < 4:
                equipped.append(tech_key)
                caller.db.equipped_techniques = equipped
                caller.msg(f"Learned {tech['name']}! It's now equipped.")
            else:
                caller.msg(f"Learned {tech['name']}! Use 'equiptech {tech_key}' to equip it.")
            
            emit_entity_delta(caller)
            return
        
        # No arguments - show training options
        if caller.is_in_combat():
            caller.msg("You cannot train in active combat.")
            return
        
        # Show stats training
        gains = ["strength", "speed", "balance", "mastery"]
        stat = random.choice(gains)
        caller.db[stat] = (caller.db[stat] or 10) + 1
        caller.db.base_power = (caller.db.base_power or 100) + 3
        caller.db.ki_control = min(100, (caller.db.ki_control or 0) + 1)
        caller.msg(
            f"{trainer.key} drills fundamentals. +1 {stat}, +3 base power, +1 ki_control."
        )
        
        # Show available techniques to learn
        from world.npc_content import get_npc_definition
        npc_def = get_npc_definition(trainer_key) if trainer_key else {}
        trainer_techs = npc_def.get("trainer_rewards", {}).get("techniques", [])
        
        if trainer_techs:
            known = set(caller.db.known_techniques or [])
            available = [t for t in trainer_techs if t not in known]
            if available:
                tech_names = [TECHNIQUES[t]["name"] for t in available if t in TECHNIQUES]
                caller.msg(f"\n|w{trainer.key} can teach you:|n {', '.join(tech_names)}")
                caller.msg("|wUse 'train <technique>' to learn one.|n")
        
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


class CmdShop(Command):
    """
    View shop inventory from a shopkeeper NPC.
    
    Usage: shop [npc]
    
    Shows the items available for purchase from a shopkeeper NPC.
    If no NPC is specified, looks for one in the current room.
    """
    key = "shop"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Find a shopkeeper NPC in the room or use the specified one
        target = None
        if self.args:
            target = _search_target(caller, self.args.strip())
        else:
            # Search for shopkeeper in the room
            if caller.location:
                for obj in caller.location.contents:
                    if _is_npc(obj):
                        content_key = obj.db.trainer_key or obj.db.npc_content_key
                        npc_data = get_npc_definition(content_key)
                        if npc_data and npc_data.get('role') == 'shopkeeper':
                            target = obj
                            break
        
        if not target:
            caller.msg("Usage: shop [npc] - No shopkeeper found.")
            return
        
        # Get NPC shop data
        content_key = target.db.trainer_key or target.db.npc_content_key
        npc_data = get_npc_definition(content_key)
        
        if not npc_data:
            caller.msg(f"{target.key} is not a valid shopkeeper.")
            return
        
        shop_items = npc_data.get('shop_items', {})
        if not shop_items:
            caller.msg(f"{npc_data['name']} has nothing for sale.")
            return
        
        caller.msg(f"|w{npc_data['name']}'s Shop|n - {npc_data.get('bio', '')}")
        caller.msg("=" * 50)
        caller.msg(f"|wYour Zeni:|n {caller.db.zeni or 0}")
        caller.msg("")
        caller.msg("|wItems for sale:|n")
        for item_id, item_data in shop_items.items():
            caller.msg(f"  |c{item_id}|n - {item_data['description']}")
            caller.msg(f"    Price: {item_data['price']}zeni |y[buy {item_id}]|n")
        caller.msg("")
        caller.msg("Use 'buy <item>' to purchase an item.")


class CmdBuy(Command):
    """
    Buy an item from a shopkeeper.
    
    Usage: buy <item>
    
    Purchases an item from the nearest shopkeeper.
    """
    key = "buy"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: buy <item>")
            return
        
        item_id = self.args.strip().lower().replace(' ', '_')
        
        # Find a shopkeeper in the room
        shopkeeper = None
        if caller.location:
            for obj in caller.location.contents:
                if _is_npc(obj):
                    content_key = obj.db.trainer_key or obj.db.npc_content_key
                    npc_data = get_npc_definition(content_key)
                    if npc_data and npc_data.get('role') == 'shopkeeper':
                        shopkeeper = (obj, npc_data)
                        break
        
        if not shopkeeper:
            caller.msg("There is no shopkeeper here. Use 'shop' to find one.")
            return
        
        npc_obj, npc_data = shopkeeper
        shop_items = npc_data.get('shop_items', {})
        
        if item_id not in shop_items:
            caller.msg(f"'{item_id}' is not available. Use 'shop' to see available items.")
            return
        
        item_data = shop_items[item_id]
        price = item_data['price']
        
        # Check if player has enough zen
        current_zeni = caller.db.zeni or 0
        if current_zeni < price:
            caller.msg(f"You need {price}zeni but only have {current_zeni}.")
            return
        
        # Deduct zen and add item to inventory
        caller.db.zeni = current_zeni - price
        
        inventory = list(caller.db.inventory or [])
        inventory.append(item_id)
        caller.db.inventory = inventory
        
        caller.msg(f"You purchased {item_data['description']} for {price}zeni.")
        caller.msg(f"Remaining Zeni: {caller.db.zeni}")


class CmdSell(Command):
    """
    Sell an item to a shopkeeper.
    
    Usage: sell <item>
    
    Sells an item from your inventory for half its value.
    """
    key = "sell"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: sell <item>")
            return
        
        item_id = self.args.strip().lower().replace(' ', '_')
        
        # Find a shopkeeper in the room
        shopkeeper = None
        if caller.location:
            for obj in caller.location.contents:
                if _is_npc(obj):
                    content_key = obj.db.trainer_key or obj.db.npc_content_key
                    npc_data = get_npc_definition(content_key)
                    if npc_data and npc_data.get('role') == 'shopkeeper':
                        shopkeeper = (obj, npc_data)
                        break
        
        if not shopkeeper:
            caller.msg("There is no shopkeeper here.")
            return
        
        npc_obj, npc_data = shopkeeper
        shop_items = npc_data.get('shop_items', {})
        
        # Check if the item is in the player's inventory
        inventory = list(caller.db.inventory or [])
        if item_id not in inventory:
            caller.msg(f"You don't have '{item_id}' in your inventory.")
            caller.msg(f"Your inventory: {', '.join(inventory) or 'empty'}")
            return
        
        # Check if the shop buys this item (it must be in their shop_items for pricing reference)
        if item_id not in shop_items:
            caller.msg(f"{npc_data['name']} doesn't want to buy '{item_id}'.")
            return
        
        item_data = shop_items[item_id]
        sell_price = item_data['price'] // 2  # Half the buy price
        
        # Remove item and add zen
        inventory.remove(item_id)
        caller.db.inventory = inventory
        caller.db.zeni = (caller.db.zeni or 0) + sell_price
        
        caller.msg(f"You sold {item_data['description']} for {sell_price}zeni.")
        caller.msg(f"Current Zeni: {caller.db.zeni}")


class CmdInventory(Command):
    """
    View your inventory.
    
    Usage: inventory
    
    Shows your current equipment and items.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        caller.msg("|wYour Inventory|n")
        caller.msg("=" * 30)
        caller.msg(f"|wZeni:|n {caller.db.zeni or 0}")
        
        # Show Dragon Balls
        dragon_balls = caller.db.dragon_balls or []
        if dragon_balls:
            caller.msg(f"")
            caller.msg(f"|wDragon Balls:|n {len(dragon_balls)}/7")
            for db in sorted(dragon_balls):
                caller.msg(f"  - {db}")
        
        # Show inventory items
        inventory = caller.db.inventory or []
        caller.msg(f"")
        caller.msg(f"|wItems:|n")
        if inventory:
            for item in inventory:
                # Get item description from shop data if possible
                caller.msg(f"  - {item}")
        else:
            caller.msg("  (empty)")


class CmdSearch(Command):
    """
    Search the area for Dragon Balls.
    
    Usage: search
    
    Searches the current location for hidden Dragon Balls.
    There is a chance to find one each time you search.
    """
    key = "search"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check cooldown
        last_search = caller.db.last_search_time or 0
        current_time = time.time()
        if current_time - last_search < 30:  # 30 second cooldown
            remaining = 30 - (current_time - last_search)
            caller.msg(f"You need to wait {remaining:.0f} seconds before searching again.")
            return
        
        caller.db.last_search_time = current_time
        
        # Get already found dragon balls
        found_balls = caller.db.dragon_balls or []
        
        # Define all possible Dragon Ball locations (by name)
        all_balls = [
            "One-Star Dragon Ball",
            "Two-Star Dragon Ball", 
            "Three-Star Dragon Ball",
            "Four-Star Dragon Ball",
            "Five-Star Dragon Ball",
            "Six-Star Dragon Ball",
            "Seven-Star Dragon Ball",
        ]
        
        # Find balls not yet collected
        unfound_balls = [b for b in all_balls if b not in found_balls]
        
        if not unfound_balls:
            caller.msg("You have already collected all 7 Dragon Balls!")
            caller.msg("Use 'summon_shenron' to call forth the Eternal Dragon.")
            return
        
        # Random chance to find a ball (30% base chance)
        if random.random() < 0.3:
            # Found one!
            found_ball = random.choice(unfound_balls)
            found_balls.append(found_ball)
            caller.db.dragon_balls = found_balls
            
            caller.msg("")
            caller.msg("|g★ ★ ★ YOU FOUND A DRAGON BALL! ★ ★ ★|n")
            caller.msg(f"")
            caller.msg(f"You found the |y{found_ball}|n!")
            caller.msg(f"")
            caller.msg(f"Dragon Balls collected: {len(found_balls)}/7")
            
            if len(found_balls) == 7:
                caller.msg("")
                caller.msg("|c✧✧✧ ALL 7 DRAGON BALLS COLLECTED! ✧✧✧|n")
                caller.msg("Use 'summon_shenron' to call forth the Eternal Dragon and make a wish!")
        else:
            caller.msg("You search the area but find nothing of interest.")
            caller.msg("Try searching again later - Dragon Balls are rare!")


class CmdSummonShenron(Command):
    """
    Summon the Eternal Dragon Shenron.
    
    Usage: summon_shenron
    
    Requires all 7 Dragon Balls to be collected.
    Summons Shenron who will grant one wish.
    """
    key = "summon_shenron"
    aliases = ["summon", "call_shenron"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check if player has all 7 Dragon Balls
        found_balls = caller.db.dragon_balls or []
        
        if len(found_balls) < 7:
            caller.msg(f"You need all 7 Dragon Balls to summon Shenron.")
            caller.msg(f"You currently have {len(found_balls)}/7 Dragon Balls.")
            return
        
        # Check cooldown ( Shenron can only be summoned once per RL day)
        last_summon = caller.db.last_shenron_summon or 0
        current_time = time.time()
        cooldown = 86400  # 24 hours in seconds
        if current_time - last_summon < cooldown:
            remaining = cooldown - (current_time - last_summon)
            hours = remaining // 3600
            caller.msg(f"Shenron has already been summoned recently. You must wait {hours:.0f} hours.")
            return
        
        # Summon Shenron
        caller.msg("")
        caller.msg("══════════════════════════════════════════════════════")
        caller.msg("|c✧✧✧ S H E N R O N   I S   S U M M O N E D ✧✧✧|n")
        caller.msg("══════════════════════════════════════════════════════")
        caller.msg("")
        caller.msg("|gThe sky darkens and a swirling vortex opens in the heavens!|n")
        caller.msg("|gA massive green dragon with horns emerges, his eyes glowing with ancient power!|n")
        caller.msg("")
        caller.msg("|cShenron: |gI am the Eternal Dragon. You who have gathered all seven Dragon Balls...|n")
        caller.msg("|c...state your wish, and it shall be granted!|n")
        caller.msg("")
        caller.msg("Available wishes:")
        caller.msg("  |yfull_heal|n - Fully restore your health and ki")
        caller.msg("  |ypermanent_pl_boost|n - Get a permanent +10% power level boost")
        caller.msg("  |ylearn_technique|n - Learn a random advanced technique")
        caller.msg("  |yzeni|n - Receive 10,000zeni")
        caller.msg("")
        caller.msg("Usage: |ywish <desire>|n (e.g., 'wish full_heal')")
        
        # Mark as having active shenron
        caller.db.shenron_active = True


class CmdWish(Command):
    """
    Make a wish to Shenron.
    
    Usage: wish <desire>
    
    Available wishes (when Shenron is summoned):
    - full_heal: Fully restore health and ki
    - permanent_pl_boost: +10% permanent power level boost
    - learn_technique: Learn a random advanced technique
    - zeni: Receive 10,000zeni
    """
    key = "wish"
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check if Shenron is active
        if not caller.db.get('shenron_active'):
            caller.msg("Shenron is not currently summoned.")
            caller.msg("You need all 7 Dragon Balls to summon Shenron.")
            return
        
        if not self.args:
            caller.msg("Usage: wish <desire>")
            caller.msg("Available wishes: full_heal, permanent_pl_boost, learn_technique, zeni")
            return
        
        wish = self.args.strip().lower().replace(' ', '_')
        
        # Define wishes
        wishes = {
            "full_heal": self._do_full_heal,
            "permanent_pl_boost": self._do_pl_boost,
            "learn_technique": self._do_learn_tech,
            "zeni": self._do_zeni,
        }
        
        if wish not in wishes:
            caller.msg(f"Unknown wish: '{wish}'")
            caller.msg("Available wishes: full_heal, permanent_pl_boost, learn_technique, zeni")
            return
        
        # Execute the wish
        result = wishes[wish](caller)
        
        # Reset Dragon Balls and Shenron status
        caller.db.dragon_balls = []
        caller.db.shenron_active = False
        caller.db.last_shenron_summon = time.time()
        
        caller.msg("")
        caller.msg("|cShenron: |gYour wish... has been granted!|n")
        caller.msg("|gThe Eternal Dragon rises skyward and vanishes into the clouds!|n")
        caller.msg("The Dragon Balls scatter across the world once more...")

    def _do_full_heal(self, caller):
        """Grant full heal wish."""
        caller.db.hp_current = caller.db.hp_max
        caller.db.ki_current = caller.db.ki_max
        caller.msg("✧ Your health and ki have been fully restored! ✧")
        
    def _do_pl_boost(self, caller):
        """Grant permanent PL boost wish."""
        current_boost = caller.db.permanent_pl_boost or 0
        caller.db.permanent_pl_boost = current_boost + 10
        caller.msg("✧ Your power has increased by 10%! ✧")
        
    def _do_learn_tech(self, caller):
        """Grant technique learning wish."""
        # Grant a random powerful technique
        bonus_techs = [
            "super_kamehameha", "final_flash", "special_beam_cannon",
            "big_bang_attack", "galick_gun", "destructo_disc",
            "instant_transmission", "dragon_fist"
        ]
        techs = caller.db.known_techniques or []
        available = [t for t in bonus_techs if t not in techs]
        
        if available:
            new_tech = random.choice(available)
            techs.append(new_tech)
            caller.db.known_techniques = techs
            caller.msg(f"✧ You learned {TECHNIQUES[new_tech]['name']}! ✧")
        else:
            # Already knows all, give zen instead
            caller.db.zeni = (caller.db.zeni or 0) + 5000
            caller.msg("✧ You already know all available techniques! Received 5000zeni instead. ✧")
            
    def _do_zeni(self, caller):
        """Grant zeni wish."""
        caller.db.zeni = (caller.db.zeni or 0) + 10000
        caller.msg("✧ You received 10,000zeni! ✧")


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
        if coords is None:
            coords = (0, 0, 0)
        from world.map_utils import render_map
        map_str = render_map(coords[0], coords[1], radius=7, target_obj=caller)
        
        zone_name = "Unknown Area"
        if loc.tags.get(category="zone"):
            zone_name = loc.tags.get(category="zone")
            
        caller.msg(f"|y[|c {zone_name} |y]|n |w({coords[0]}, {coords[1]})|n\n" + map_str)
        
        from world.events import emit_map_data
        emit_map_data(caller, coords[0], coords[1], radius=7)


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


class CmdTournament(Command):
    """
    View and manage tournament participation.
    
    Usage: tournament [info|join|leave]
    """
    key = "tournament"
    aliases = ["t"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else "info"
        
        if args == "info":
            state = get_tournament_state()
            caller.msg("|w=== WORLD MARTIAL ARTS TOURNAMENT ===|n")
            status = state["status"]
            if status == TOURNAMENT_INACTIVE:
                caller.msg("Status: |rInactive|n")
            elif status == TOURNAMENT_SIGNUPS:
                caller.msg("Status: |gSignups Open|n")
                caller.msg(f"Participants: {len(state['participants'])}")
            elif status == TOURNAMENT_IN_PROGRESS:
                caller.msg("Status: |yIn Progress|n")
                caller.msg(f"Round: {state['round']}")
                caller.msg(f"Prize Pool: {state['prize_pool']}zeni")
            else:
                caller.msg("Status: Finished")
                if "champion" in state:
                    caller.msg(f"Champion: {state['champion']}")
        elif args == "join":
            result = join_tournament(caller)
            if result["success"]:
                caller.msg(f"|gJoined tournament!|n ({result['participants']} participants)")
            else:
                caller.msg(f"|r{result['reason']}|n")
        elif args == "leave":
            result = leave_tournament(caller)
            if result["success"]:
                caller.msg("|gLeft tournament.|n")
            else:
                caller.msg(f"|r{result['reason']}|n")
        else:
            caller.msg("Usage: tournament [info|join|leave]")


class CmdWorldBoss(Command):
    """
    World Boss event commands.
    
    Usage: boss [info|damage|attack]
    """
    key = "boss"
    aliases = ["worldboss", "wb"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else "info"
        
        boss_state = get_world_boss_state()
        
        if args == "info":
            caller.msg("|w=== WORLD BOSS EVENT ===|n")
            if not boss_state["active"]:
                caller.msg("Status: |rNo active boss|n")
                return
            remaining = boss_state["end_time"] - time.time()
            caller.msg(f"Boss: |y{boss_state['boss_name']}|n")
            caller.msg(f"PL: {boss_state['boss_pl']:,} | HP: {boss_state['boss_hp']:,}/{boss_state['boss_max_hp']:,}")
            caller.msg(f"Time: {remaining/60:.1f} min")
        elif args == "attack":
            if not boss_state["active"]:
                caller.msg("No world boss active.")
                return
            # SECURITY: Server calculates damage based on player's actual stats
            # Client no longer provides damage value
            result = damage_world_boss(str(caller.id))
            if result.get("success") is False:
                caller.msg(result.get("reason", "Failed to deal damage"))
                return
            
            # Get the actual damage dealt (for display)
            # The damage was calculated server-side, but we can estimate for display
            current_pl, _ = caller.get_current_pl()
            displayed_damage = int(current_pl * 1.0)  # Approximate middle-ground
            
            if result.get("boss_hp", 0) <= 0:
                caller.msg("|g★ WORLD BOSS DEFEATED! ★|n")
            else:
                caller.msg(f"You deal {displayed_damage:,} damage! HP: {result['boss_hp']:,}")
        elif args == "leaderboard" or args == "damage":
            leaderboard = get_world_boss_damage_leaderboard()
            caller.msg("|w=== DAMAGE LEADERBOARD ===|n")
            for i, entry in enumerate(leaderboard[:10], 1):
                caller.msg(f"{i}. {entry['player_id']}: {entry['damage']:,}")
        else:
            caller.msg("Usage: boss [info|attack|leaderboard]")


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


class CmdFly(Command):
    """
    Take to the skies!
    Usage: fly [direction]
           fly land
    
    Flying allows you to move faster and travel between areas.
    Requires at least 1,000 PL to fly.
    """
    key = "fly"
    aliases = ["flying", "hover"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        
        # Check PL requirement
        current_pl = caller.attributes.get("base_power", 0) or 0
        if current_pl < 1000:
            caller.msg("You need at least 1,000 PL to fly. Keep training!")
            return
        
        # Check if in combat
        if caller.db.combat_id:
            caller.msg("You can't fly while in combat!")
            return
        
        args = self.args.strip().lower() if self.args else ""
        
        # Check current flight state
        flight_state = caller.db.flight_state or "ground"
        
        if args == "land" or args == "ground":
            # Land on ground
            if flight_state == "ground":
                caller.msg("You're already on the ground.")
                return
            caller.db.flight_state = "ground"
            caller.msg("{YYou descend gently to the ground.{x")
            return
        
        # Determine direction
        directions = {"north": "n", "south": "s", "east": "e", "west": "w", 
                     "n": "n", "s": "s", "e": "e", "w": "w",
                     "up": "up", "down": "down"}
        
        # Toggle flight or move
        if not args:
            # Toggle flight on/off
            if flight_state == "ground":
                caller.db.flight_state = "flying"
                caller.msg("{YYou soar into the air! Your feet leave the ground as you take flight.{x")
            else:
                caller.db.flight_state = "ground"
                caller.msg("{YYou descend and land on the ground.{x")
            return
        
        # Moving in a direction while flying
        direction = directions.get(args)
        if direction:
            if flight_state == "ground":
                # Auto-take off
                caller.db.flight_state = "flying"
                caller.msg("{YYou leap into the air and take flight!{x")
            
            # Get exit
            location = caller.location
            exit_obj = None
            
            # Map direction to exit
            dir_map = {"n": "north", "s": "south", "e": "east", "w": "west", "up": "up", "down": "down"}
            exit_name = dir_map.get(direction, direction)
            
            for exit in location.exits:
                if exit.key.lower() == exit_name or exit.aliases.get(direction, "") == exit_name:
                    exit_obj = exit
                    break
            
            if exit_obj:
                # Check ki cost for flight
                ki_cost = 5
                current_ki = caller.db.ki_current or 0
                if current_ki < ki_cost:
                    caller.msg("You don't have enough ki to fly that far. Rest a moment.")
                    return
                
                caller.db.ki_current = max(0, current_ki - ki_cost)
                caller.move_to(exit_obj.destination)
                
                # Flight message
                fly_msgs = [
                    "You fly {direction} through the sky!",
                    "Soaring through the air, you travel {direction}.",
                    "With a burst of speed, you fly {direction}."
                ]
                msg = random.choice(fly_msgs).format(direction=exit_name)
                caller.msg(f"{{Y{msg}{{x")
            else:
                caller.msg(f"You can't fly {exit_name} from here.")
        else:
            caller.msg("Usage: fly [north/south/east/west/up/down] or fly land")


class CmdTeleportPlayer(Command):
    """
    Save location or teleport to saved location.
    Usage: teleport save
           teleport recall
           teleport <player>
    
    Save your current location to return to later.
    Recall costs 20 ki.
    """
    key = "teleport"
    aliases = ["tp", "recall", "home"]
    locks = "cmd:all()"
    help_category = "DB"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show saved location
            saved = caller.db.saved_location
            if saved:
                caller.msg(f"Your saved location: {saved.get('name', 'Unknown')} at {saved.get('coords', 'unknown')}")
            else:
                caller.msg("You haven't saved a location. Use 'teleport save' to remember this spot.")
            return
        
        if args == "save":
            # Save current location
            location = caller.location
            coords = caller.db.coords
            
            if hasattr(location, "db") and location.db.key:
                name = location.db.key
            else:
                name = location.key
            
            caller.db.saved_location = {
                "name": name,
                "coords": coords,
                "room_id": location.id
            }
            caller.msg(f"{{GLocation saved: {{y{name}{{G. Use 'teleport recall' to return here.{{x")
            return
        
        if args == "recall" or args == "home":
            # Teleport to saved location
            saved = caller.db.saved_location
            if not saved:
                caller.msg("You haven't saved a location. Use 'teleport save' first.")
                return
            
            # Check ki cost
            ki_cost = 20
            current_ki = caller.db.ki_current or 0
            if current_ki < ki_cost:
                caller.msg(f"You need {ki_cost} ki to teleport. You have {current_ki}.")
                return
            
            # Check combat
            if caller.db.combat_id:
                caller.msg("You can't teleport while in combat!")
                return
            
            # Try to get the room
            from world.map_utils import get_room_at
            room_id = saved.get("room_id")
            coords = saved.get("coords")
            
            target_room = None
            if room_id:
                from evennia import search_object
                results = search_object(room_id)
                if results:
                    target_room = results[0]
            elif coords:
                target_room = get_room_at(coords[0], coords[1], coords[2] if len(coords) > 2 else 0)
            
            if target_room:
                caller.db.ki_current = max(0, current_ki - ki_cost)
                old_name = saved.get("name", "unknown")
                caller.move_to(target_room)
                caller.msg(f"{{YYou vanish in a flash of light and reappear at {{c{old_name}{{Y!{{x")
            else:
                caller.msg("Your saved location no longer exists. Save a new one.")
                caller.db.saved_location = None
            return
        
        # Otherwise, try to find a player to teleport to
        from evennia import search_object
        targets = search_object(args)
        if not targets:
            caller.msg("Unknown target. Use 'teleport save' or 'teleport recall'.")
            return
        
        target = targets[0]
        if not target.location:
            caller.msg("That target is not currently anywhere.")
            return
        
        # Check ki
        ki_cost = 30
        current_ki = caller.db.ki_current or 0
        if current_ki < ki_cost:
            caller.msg(f"You need {ki_cost} ki to teleport to a player.")
            return
        
        if caller.db.combat_id:
            caller.msg("You can't teleport while in combat!")
            return
        
        caller.db.ki_current = max(0, current_ki - ki_cost)
        old_name = target.key
        caller.move_to(target.location)
        caller.msg(f"{{YYou teleport directly to {{c{old_name}{{Y!{{x")


class CmdGuild(Command):
    """
    Guild management commands.
    Usage:
        guild create <name> - Create a new guild
        guild list - List all guilds
        guild info - View your guild info
        guild invite <player> - Invite a player to your guild
        guild kick <player> - Kick a player from your guild
        guild promote <player> - Promote a member to officer
        guild demote <player> - Demote an officer to member
        guild leave - Leave your guild
        guild disband - Disband your guild (leader only)
        guild motd <message> - Set the guild message of the day
        guild chat <message> - Send a message to guild chat
        guild deposit <amount> - Deposit zeni to guild bank
        guild withdraw <amount> - Withdraw zeni from guild bank (leader only)
        guild bank - View guild bank balance
    """
    key = "guild"
    aliases = ["clan", "g"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        account = caller.account if hasattr(caller, 'account') else None
        
        if not account:
            caller.msg("You need an account to use guild commands.")
            return
        
        args = self.args.strip() if self.args else ""
        
        if not args:
            # Show guild info
            guild = get_player_guild(str(account.id))
            if guild:
                self._show_guild_info(caller, guild)
            else:
                caller.msg("You are not in a guild. Use 'guild create <name>' to create one.")
            return
        
        parts = args.split(None, 1)
        action = parts[0].lower() if parts else ""
        target = parts[1] if len(parts) > 1 else ""
        
        if action == "create":
            self._create_guild(account, caller, target)
        elif action == "list":
            self._list_guilds(caller)
        elif action == "info":
            self._show_guild_info(caller, get_player_guild(str(account.id)))
        elif action == "invite":
            self._invite_player(account, caller, target)
        elif action == "kick":
            self._kick_player(account, caller, target)
        elif action == "promote":
            self._promote_player(account, caller, target)
        elif action == "demote":
            self._demote_player(account, caller, target)
        elif action == "leave":
            self._leave_guild(account, caller)
        elif action == "disband":
            self._disband_guild(account, caller)
        elif action == "motd":
            self._set_motd(account, caller, target)
        elif action == "chat" or action == "gchat":
            self._guild_chat(account, caller, target)
        elif action == "deposit":
            self._deposit_zeni(account, caller, target)
        elif action == "withdraw":
            self._withdraw_zeni(account, caller, target)
        elif action == "bank":
            self._show_bank(caller, get_player_guild(str(account.id)))
        else:
            caller.msg("Unknown guild command. Use 'help guild' for available commands.")
    
    def _create_guild(self, account, caller, name):
        from world.guilds import create_guild, GUILD_CREATION_COST, get_player_guild
        
        if not name:
            caller.msg("Usage: guild create <name>")
            return
        
        if len(name) > 30:
            caller.msg("Guild name must be 30 characters or less.")
            return
        
        # Check if already in a guild
        existing = get_player_guild(str(account.id))
        if existing:
            caller.msg("You are already in a guild. Leave it first.")
            return
        
        # Check zeni cost
        zeni = caller.db.zeni or 0
        if zeni < GUILD_CREATION_COST:
            caller.msg(f"You need {GUILD_CREATION_COST} zeni to create a guild. You have {zeni}.")
            return
        
        # Create the guild
        char_name = caller.key
        result = create_guild(name, str(account.id), char_name)
        
        if result.get("success"):
            caller.db.zeni = zeni - GUILD_CREATION_COST
            caller.msg(f"{{GGuild '{name}' created! You are now the leader.{{x")
            # Update character with guild info
            caller.db.guild = name
            caller.db.guild_rank = "Leader"
        else:
            caller.msg(f"{{R{result.get('reason', 'Could not create guild')}{{x")
    
    def _list_guilds(self, caller):
        from world.guilds import list_guilds
        
        guilds = list_guilds()
        
        if not guilds:
            caller.msg("No guilds exist yet. Be the first to create one!")
            return
        
        caller.msg("{{C=== Available Guilds ==={{x")
        for g in guilds:
            caller.msg(f"  {{c{g['name']}{{x - Leader: {g['leader']} - Members: {g['members']}")
    
    def _show_guild_info(self, caller, guild):
        from world.guilds import get_guild_members
        
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        members = get_guild_members(guild)
        
        caller.msg(f"{{C=== Guild: {guild.db.guild_name} ==={{x")
        caller.msg(f"{{yLeader:{{x {guild._get_leader_name()}")
        caller.msg(f"{{yMOTD:{{x {guild.get_motd()}")
        caller.msg(f"{{yBank:{{x {guild.get_zeni()} zeni")
        caller.msg(f"{{yMembers: {{x{len(members)}")
        
        # Show members
        for m in members:
            role_indicator = "" if m['role'] == 'member' else f" ({{m['role']}})"
            caller.msg(f"  - {m['name']}{role_indicator}")
    
    def _invite_player(self, account, caller, target_name):
        from world.guilds import invite_to_guild, get_player_guild, is_guild_officer
        
        if not target_name:
            caller.msg("Usage: guild invite <player>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_officer(str(account.id), guild):
            caller.msg("You must be an officer to invite players.")
            return
        
        # Find target player
        from evennia import search_object
        targets = search_object(target_name)
        if not targets:
            caller.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        if not hasattr(target, 'account'):
            caller.msg("That is not a player.")
            return
        
        target_account = target.account
        if not target_account:
            caller.msg("That character has no associated account.")
            return
        
        result = invite_to_guild(guild, str(account.id), str(target_account.id))
        
        if result.get("success"):
            caller.msg(f"{{GInvited {target.key} to the guild.{{x")
            if target_account.is_connected():
                target_account.msg(f"{{GYou have been invited to guild '{guild.db.guild_name}'. Use 'guild join {guild.db.guild_name}' to join.{{x")
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _kick_player(self, account, caller, target_name):
        from world.guilds import kick_from_guild, get_player_guild, is_guild_officer
        
        if not target_name:
            caller.msg("Usage: guild kick <player>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_officer(str(account.id), guild):
            caller.msg("You must be an officer to kick players.")
            return
        
        # Find target
        from evennia import search_object
        targets = search_object(target_name)
        if not targets:
            caller.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        if not hasattr(target, 'account'):
            caller.msg("That is not a player.")
            return
        
        target_account = target.account
        result = kick_from_guild(guild, str(account.id), str(target_account.id))
        
        if result.get("success"):
            caller.msg(f"{{G}}Kicked {{c{target.key}{{x from the guild{{x")
            # Clear guild info from character
            target.db.guild = None
            target.db.guild_rank = None
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _promote_player(self, account, caller, target_name):
        from world.guilds import promote_member, get_player_guild, is_guild_leader, GUILD_ROLE_OFFICER
        
        if not target_name:
            caller.msg("Usage: guild promote <player>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_leader(str(account.id), guild):
            caller.msg("Only the leader can promote players to officer.")
            return
        
        # Find target
        from evennia import search_object
        targets = search_object(target_name)
        if not targets:
            caller.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        if not hasattr(target, 'account'):
            caller.msg("That is not a player.")
            return
        
        target_account = target.account
        result = promote_member(guild, str(account.id), str(target_account.id), GUILD_ROLE_OFFICER)
        
        if result.get("success"):
            caller.msg(f"{{GPromoted {target.key} to officer.{{x")
            target.db.guild_rank = "Officer"
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _demote_player(self, account, caller, target_name):
        from world.guilds import promote_member, get_player_guild, is_guild_leader, GUILD_ROLE_MEMBER
        
        if not target_name:
            caller.msg("Usage: guild demote <player>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_leader(str(account.id), guild):
            caller.msg("Only the leader can demote officers.")
            return
        
        # Find target
        from evennia import search_object
        targets = search_object(target_name)
        if not targets:
            caller.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        if not hasattr(target, 'account'):
            caller.msg("That is not a player.")
            return
        
        target_account = target.account
        result = promote_member(guild, str(account.id), str(target_account.id), GUILD_ROLE_MEMBER)
        
        if result.get("success"):
            caller.msg(f"{{GDemoted {target.key} to member.{{x")
            target.db.guild_rank = "Member"
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _leave_guild(self, account, caller):
        from world.guilds import leave_guild, get_player_guild
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        result = leave_guild(guild, str(account.id))
        
        if result.get("success"):
            caller.msg("{{GYou have left the guild.{{x")
            caller.db.guild = None
            caller.db.guild_rank = None
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _disband_guild(self, account, caller):
        from world.guilds import disband_guild, get_player_guild, is_guild_leader
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_leader(str(account.id), guild):
            caller.msg("Only the leader can disband the guild.")
            return
        
        result = disband_guild(guild, str(account.id))
        
        if result.get("success"):
            caller.msg("{{GThe guild has been disbanded.{{x")
            caller.db.guild = None
            caller.db.guild_rank = None
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _set_motd(self, account, caller, message):
        from world.guilds import set_guild_motd, get_player_guild, is_guild_officer
        
        if not message:
            caller.msg("Usage: guild motd <message>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        if not is_guild_officer(str(account.id), guild):
            caller.msg("You must be an officer to set the MOTD.")
            return
        
        result = set_guild_motd(guild, str(account.id), message)
        
        if result.get("success"):
            caller.msg("{{GMOTD updated.{{x")
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")
    
    def _guild_chat(self, account, caller, message):
        from world.guilds import get_player_guild, get_guild_members
        
        if not message:
            caller.msg("Usage: guild chat <message>")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You must be in a guild to use guild chat.")
            return
        
        # Get all online members
        members = get_guild_members(guild)
        char_name = caller.key
        
        for member in members:
            # Try to find the account and send message
            from evennia.objects.models import ObjectDB
            try:
                member_obj = ObjectDB.objects.get(id=member['id'])
                if member_obj and member_obj.account:
                    if member_obj.account.is_connected():
                        if member['id'] == str(account.id):
                            member_obj.account.msg(f"{{C[Guild] {{c{char_name}{{C: {message}{{x")
                        else:
                            member_obj.account.msg(f"{{C[Guild] {{c{char_name}{{C: {message}{{x")
            except Exception:
                pass

    def _deposit_zeni(self, account, caller, amount_str):
        from world.guilds import deposit_to_guild, get_player_guild
        
        if not amount_str:
            caller.msg("Usage: guild deposit <amount>")
            return
        
        try:
            amount = int(amount_str)
        except ValueError:
            caller.msg("Please enter a valid number.")
            return
        
        if amount <= 0:
            caller.msg("Amount must be positive.")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        result = deposit_to_guild(guild, str(account.id), amount, caller)
        
        if result.get("success"):
            caller.msg("{{G}}Deposited " + str(amount) + " zeni to guild bank. New balance: " + str(result.get('zeni')) + " zeni{{x")
            caller.msg("{{G}}Your new zeni balance: " + str(result.get('player_zeni')) + " zeni{{x")
        else:
            caller.msg(f"{{R{result.get('reason')}{{x")

    def _withdraw_zeni(self, account, caller, amount_str):
        from world.guilds import withdraw_guild_zeni, get_player_guild
        
        if not amount_str:
            caller.msg("Usage: guild withdraw <amount>")
            return
        
        try:
            amount = int(amount_str)
        except ValueError:
            caller.msg("Please enter a valid number.")
            return
        
        if amount <= 0:
            caller.msg("Amount must be positive.")
            return
        
        guild = get_player_guild(str(account.id))
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        result = withdraw_guild_zeni(guild, str(account.id), amount)
        
        if result.get("success"):
            caller.db.zeni = (caller.db.zeni or 0) + amount
            caller.msg("{{G}}Withdrew " + str(amount) + " zeni from guild bank. Guild balance: " + str(result.get('zeni')) + " zeni{{x")
            caller.msg("{{G}}Your new zeni balance: " + str(caller.db.zeni) + " zeni{{x")
        else:
            caller.msg("{{R}}" + result.get('reason') + "{{x")

    def _show_bank(self, caller, guild):
        if not guild:
            caller.msg("You are not in a guild.")
            return
        
        caller.msg("{{C}}=== Guild Bank ==={{x")
        caller.msg("{{y}}Balance:{{x " + str(guild.get_zeni()) + " zeni")


# ═══════════════════════════════════════════════════════════════════════════════
# ROSHI'S ERRAND COMMANDS - For Kame Island Quest Chain
# ═══════════════════════════════════════════════════════════════════════════════


class CmdGather(Command):
    """
    Gather items from the environment for Roshi's quests.
    
    Usage: gather crabs   - Collect hermit crabs from the beach
    Usage: gather debris - Clean up driftwood from the beach
    """
    key = "gather"
    aliases = ["collect"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        arg = self.args.strip().lower() if self.args else ""
        
        # Check location
        room_name = caller.location.db_key if caller.location and hasattr(caller.location, 'db_key') else str(caller.location)
        
        if not arg:
            caller.msg("Usage: gather crabs |or gather debris")
            return
        
        if arg == "crabs":
            # Check for quest
            from world.quests import get_quest_status
            status = get_quest_status(caller, "roshi_errand_hermit_crabs")
            if not status.get("accepted"):
                caller.msg("You don't have any reason to gather crabs. Talk to Master Roshi first!")
                return
            if status.get("completed"):
                caller.msg("You've already completed this task.")
                return
            
            # Track progress
            progress = caller.db.roshi_crabs_gathered or 0
            caller.db.roshi_crabs_gathered = progress + 1
            
            new_progress = caller.db.roshi_crabs_gathered
            caller.msg(f"You round up a hermit crab... ({new_progress}/5)")
            
            if new_progress >= 5:
                from world.quests import mark_quest_turn_in_ready
                ok, msg = mark_quest_turn_in_ready(caller, "roshi_errand_hermit_crabs")
                if ok:
                    caller.msg(f"{{g★ Quest complete: Return to Master Roshi to turn in!{{x")
                    caller.msg("Return to Kame House and type 'quest complete' or talk to Roshi!")
        
        elif arg == "debris":
            # Check for quest
            from world.quests import get_quest_status
            status = get_quest_status(caller, "roshi_errand_debris")
            if not status.get("accepted"):
                caller.msg("You don't have any reason to gather debris. Talk to Master Roshi first!")
                return
            if status.get("completed"):
                caller.msg("You've already completed this task.")
                return
            
            # Track progress
            progress = caller.db.roshi_debris_gathered or 0
            caller.db.roshi_debris_gathered = progress + 1
            
            new_progress = caller.db.roshi_debris_gathered
            caller.msg(f"You pick up driftwood and debris... ({new_progress}/3)")
            
            if new_progress >= 3:
                from world.quests import mark_quest_turn_in_ready
                ok, msg = mark_quest_turn_in_ready(caller, "roshi_errand_debris")
                if ok:
                    caller.msg(f"{{g★ Quest complete: Return to Master Roshi to turn in!{{x")
        
        else:
            caller.msg("You can gather 'crabs' or 'debris'. Maybe other things if you look hard enough...")


class CmdFind(Command):
    """
    Search for items or creatures in the area.
    
    Usage: find turtle   - Search for a lost turtle
    """
    key = "find"
    aliases = ["search", "lookfor"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        arg = self.args.strip().lower() if self.args else ""
        
        if not arg:
            caller.msg("Usage: find <thing>")
            return
        
        if arg == "turtle":
            from world.quests import get_quest_status
            status = get_quest_status(caller, "roshi_errand_turtle")
            if not status.get("accepted"):
                caller.msg("You don't have any reason to find a turtle. Talk to Master Roshi first!")
                return
            if status.get("completed"):
                caller.msg("You've already completed this task.")
                return
            
            # Complete the quest
            from world.quests import mark_quest_turn_in_ready
            ok, msg = mark_quest_turn_in_ready(caller, "roshi_errand_turtle")
            if ok:
                caller.msg("You find Old Turtle's lost child hiding behind a bush!")
                caller.msg("{{g★ Quest complete: The turtle follows you back! Return to Master Roshi!{{x")
        else:
            caller.msg(f"You search for {arg} but find nothing notable...")


class CmdMeditate(Command):
    """
    Meditate to focus your mind and ki.
    
    Usage: meditate
    
    Required for some training quests.
    """
    key = "meditate"
    aliases = ["meditation", "focus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Check for quest
        from world.quests import get_quest_status
        status = get_quest_status(caller, "roshi_meditation_training")
        if not status.get("accepted"):
            caller.msg("You sit and clear your mind, focusing on your breathing...")
            caller.msg("You feel a bit more centered.")
            return
        if status.get("completed"):
            caller.msg("You've already completed your meditation training.")
            return
        
        # Do meditation
        caller.msg("You sit in a meditative pose and focus on your breathing...")
        caller.msg("Your mind clears and you feel your ki becoming more focused!")
        
        from world.quests import mark_quest_turn_in_ready
        ok, msg = mark_quest_turn_in_ready(caller, "roshi_meditation_training")
        if ok:
            caller.msg("{{g★ Quest complete: Your focus is stronger! Return to Master Roshi!{{x")
