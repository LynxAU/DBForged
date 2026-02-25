"""
Server-authoritative combat handler for the DB vertical slice.
"""

from __future__ import annotations

import random
import time

from evennia.objects.models import ObjectDB
from evennia.scripts.scripts import DefaultScript
from evennia.utils import logger

from world.color_utils import aura_phrase
from world.events import emit_combat_event, emit_entity_delta, emit_vfx
from world.forms import FORMS, get_form_tick_drain
from world.power import pl_gap_effect
from world.techniques import TECHNIQUES

COMBAT_SCRIPT_KEY = "db_combat"


def _obj(obj_id):
    return ObjectDB.objects.filter(id=obj_id).first()


def get_combat_handler():
    script = DefaultScript.objects.filter(db_key=COMBAT_SCRIPT_KEY).first()
    if script and script.is_typeclass("world.combat.CombatHandler", exact=False):
        return script
    return DefaultScript.objects.filter(db_typeclass_path="world.combat.CombatHandler").first()


def _ensure_sets(script):
    script.db.combatants = set(script.db.combatants or [])
    script.db.chargers = set(script.db.chargers or [])
    script.db.pending_beams = list(script.db.pending_beams or [])


def engage(attacker, target):
    script = get_combat_handler()
    if not script:
        return
    _ensure_sets(script)
    attacker.db.combat_target = target.id
    target.db.combat_target = target.db.combat_target or attacker.id
    attacker.db.in_combat = True
    target.db.in_combat = True
    script.db.combatants.add(attacker.id)
    script.db.combatants.add(target.id)


def disengage(character):
    script = get_combat_handler()
    character.db.combat_target = None
    character.db.in_combat = False
    character.db.charge_stacks = 0
    if script:
        _ensure_sets(script)
        script.db.combatants.discard(character.id)
        script.db.chargers.discard(character.id)


def start_charging(character, duration=6):
    script = get_combat_handler()
    if not script:
        return
    _ensure_sets(script)
    character.db.is_charging = True
    character.add_status("charging", duration)
    script.db.chargers.add(character.id)
    emit_vfx(character.location, "vfx_charge_glow", source=character)


def stop_charging(character, interrupted=False):
    script = get_combat_handler()
    character.db.is_charging = False
    character.remove_status("charging")
    character.db.charge_stacks = 0 if interrupted else max(0, character.db.charge_stacks or 0)
    if script:
        _ensure_sets(script)
        script.db.chargers.discard(character.id)
    if interrupted:
        character.msg("|rYour charge is interrupted!|n")


def register_beam(character, target, tech_key, base_damage):
    script = get_combat_handler()
    if not script:
        return False
    _ensure_sets(script)
    script.db.pending_beams.append(
        {
            "attacker": character.id,
            "target": target.id,
            "tech": tech_key,
            "base_damage": max(1, int(base_damage)),
            "expires": time.time() + 1.2,
        }
    )
    return True


class CombatHandler(DefaultScript):
    """
    Global 1s combat tick.
    """

    def at_script_creation(self):
        self.key = COMBAT_SCRIPT_KEY
        self.interval = 1
        self.persistent = True
        self.start_delay = True
        self.desc = "DB vertical slice combat loop"
        _ensure_sets(self)

    def at_repeat(self):
        try:
            _ensure_sets(self)
            self._process_charging()
            self._process_hostile_ai()
            self._resolve_beams()
            self._process_passive_tick()
            self._process_form_drain()
            self._process_android_heat()
            self._process_combos()
        except Exception:  # pragma: no cover - safety in live loop
            logger.log_trace("DB combat tick error")

    def _iter_ids(self, idset):
        stale = set()
        for obj_id in set(idset):
            try:
                obj = _obj(obj_id)
                if obj and hasattr(obj, 'location') and obj.location:
                    yield obj
                else:
                    stale.add(obj_id)
            except Exception as e:
                # SECURITY: Catch any errors during iteration to prevent crashes
                logger.log_warning(f"Error iterating combatant {obj_id}: {e}")
                stale.add(obj_id)
        for obj_id in stale:
            idset.discard(obj_id)

    def _process_charging(self):
        for obj in list(self._iter_ids(self.db.chargers)):
            if not obj.location or not obj.has_status("charging"):
                stop_charging(obj)
                continue
            if obj.has_status("stunned"):
                stop_charging(obj, interrupted=True)
                continue
            obj.db.charge_stacks = min(9, (obj.db.charge_stacks or 0) + 1)
            ki_gain = 3 + int((obj.db.ki_control or 0) * 0.08)
            obj.restore_ki(ki_gain)
            
            # EPIC charging messages based on stack level
            stacks = obj.db.charge_stacks
            if stacks >= 7:
                aura_desc = "BLINDING"
                msg = f"|m>>> CHARGING UP! >>>|n {aura_phrase(obj.db.aura_color).upper()} aura blazes! Ki +{ki_gain}, charge stacks: {stacks}/9"
            elif stacks >= 4:
                aura_desc = "INTENSIFYING"
                msg = f"|mCharging...|n {aura_phrase(obj.db.aura_color).capitalize()} intensifies. Ki +{ki_gain}, charge stacks: {stacks}/9"
            else:
                aura_desc = "growing"
                msg = f"|cCharging...|n {aura_phrase(obj.db.aura_color)} aura {aura_desc}. Ki +{ki_gain}, charge stacks: {stacks}/9"
            
            obj.msg(msg)
            emit_entity_delta(obj)

    def _process_hostile_ai(self):
        hostile_npcs = ObjectDB.objects.filter(db_typeclass_path="typeclasses.npcs.HostileNPC")
        for npc in hostile_npcs:
            # Get typed object, not raw DB object
            npc = npc.get_typeclass()
            if npc.db.hp_current <= 0 or not npc.location:
                continue
            if npc.has_status("stunned"):
                continue
            current_target = _obj(npc.db.combat_target) if npc.db.combat_target else None
            if current_target and current_target.location == npc.location and current_target.db.hp_current > 0:
                continue
            players = [
                obj
                for obj in npc.location.contents
                if obj.is_typeclass("typeclasses.characters.Character", exact=False)
                and not obj.is_typeclass("typeclasses.npcs.DBNPC", exact=False)
                and obj.db.hp_current > 0
            ]
            if players:
                target = random.choice(players)
                engage(npc, target)
                npc.location.msg_contents(f"|r{npc.key}|n lunges at {target.key}!")
                emit_combat_event(npc.location, npc, target, {"subtype": "ai_engage"})

        # Also process test combat NPCs
        test_npcs = ObjectDB.objects.filter(db_is_test_dummy=True)
        for npc in test_npcs:
            if npc.db.hp_current <= 0 or not npc.location:
                continue
            if npc.has_status("stunned"):
                continue
            current_target = _obj(npc.db.combat_target) if npc.db.combat_target else None
            if not current_target or current_target.location != npc.location:
                continue
            if current_target.db.hp_current <= 0:
                continue
            # Run the test NPC's AI
            if hasattr(npc, 'run_test_ai'):
                npc.run_test_ai()

    def _resolve_beams(self):
        now = time.time()
        pending = [entry for entry in self.db.pending_beams if _obj(entry["attacker"]) and _obj(entry["target"])]
        consumed = set()
        for i, beam_a in enumerate(pending):
            if i in consumed:
                continue
            a_attacker = _obj(beam_a["attacker"])
            a_target = _obj(beam_a["target"])
            if not a_attacker or not a_target or a_attacker.location != a_target.location:
                continue

            clash_index = None
            for j, beam_b in enumerate(pending):
                if j <= i or j in consumed:
                    continue
                if beam_b["attacker"] == beam_a["target"] and beam_b["target"] == beam_a["attacker"]:
                    clash_index = j
                    break
            if clash_index is not None:
                beam_b = pending[clash_index]
                self._resolve_beam_struggle(beam_a, beam_b)
                consumed.add(i)
                consumed.add(clash_index)
                continue

            if beam_a["expires"] <= now:
                self._resolve_single_beam(beam_a)
                consumed.add(i)

        self.db.pending_beams = [entry for idx, entry in enumerate(pending) if idx not in consumed]

    def _resolve_single_beam(self, beam):
        attacker = _obj(beam["attacker"])
        target = _obj(beam["target"])
        if not attacker or not target or attacker.location != target.location:
            return
        a_pl, _ = attacker.get_current_pl()
        d_pl, _ = target.get_current_pl()
        gap = pl_gap_effect(a_pl, d_pl)
        damage = int(beam["base_damage"] * gap["damage_mult"])
        dealt = target.apply_damage(damage, source=attacker, kind="beam")
        attacker.location.msg_contents(
            f"|c{TECHNIQUES[beam['tech']]['name']}|n from {attacker.key} slams {target.key} for |r{dealt}|n!"
        )
        emit_vfx(attacker.location, TECHNIQUES[beam["tech"]]["vfx_id"], source=attacker, target=target)
        emit_combat_event(
            attacker.location,
            attacker,
            target,
            {"subtype": "beam_hit", "technique": beam["tech"], "damage": dealt, "gap_quality": gap["quality"]},
        )
        emit_entity_delta(target)

    def _resolve_beam_struggle(self, beam_a, beam_b):
        a = _obj(beam_a["attacker"])
        b = _obj(beam_b["attacker"])
        if not a or not b or a.location != b.location:
            return
        a_pl, _ = a.get_current_pl()
        b_pl, _ = b.get_current_pl()
        a_score = a_pl + ((a.db.mastery or 0) * 9) + ((a.db.balance or 0) * 7) + ((a.db.ki_current or 0) * 2)
        b_score = b_pl + ((b.db.mastery or 0) * 9) + ((b.db.balance or 0) * 7) + ((b.db.ki_current or 0) * 2)
        a_score += (a.db.charge_stacks or 0) * 18
        b_score += (b.db.charge_stacks or 0) * 18
        winner, loser = (a, b) if a_score >= b_score else (b, a)
        win_gap = max(1.0, abs(a_score - b_score))
        damage = int(24 + (win_gap**0.35))
        dealt = loser.apply_damage(damage, source=winner, kind="beam_struggle")
        
        # EPIC beam struggle messages
        if win_gap > 50:
            # Decisive victory
            winner.location.msg_contents(
                f"|m>>> BEAM CLASH! >>>|n {winner.key}'s |c{TECHNIQUES[beam_a['tech'] if beam_a['attacker'] == winner.id else beam_b['tech']]['name']}|n |woverpowers|n {loser.key} with overwhelming force! |r{dealt}|n damage!"
            )
        elif win_gap > 20:
            # Clear victory
            winner.location.msg_contents(
                f"|m>>> BEAM CLASH! >>>|n {winner.key} pushes through {loser.key}'s beam! |r{dealt}|n damage!"
            )
        else:
            # Close struggle
            winner.location.msg_contents(
                f"|mBeam struggle!|n {winner.key} overpowers {loser.key}, dealing |r{dealt}|n!"
            )
        emit_vfx(winner.location, "vfx_beam_struggle", source=winner, target=loser)
        emit_combat_event(
            winner.location,
            winner,
            loser,
            {"subtype": "beam_struggle", "winner_id": winner.id, "loser_id": loser.id, "damage": dealt},
        )
        emit_entity_delta(loser)

    def _process_passive_tick(self):
        room_lines = {}
        for attacker in list(self._iter_ids(self.db.combatants)):
            target = _obj(attacker.db.combat_target) if attacker.db.combat_target else None
            if not target or attacker.location != target.location:
                disengage(attacker)
                continue
            if attacker.db.hp_current <= 0 or target.db.hp_current <= 0:
                disengage(attacker)
                continue
            if attacker.has_status("stunned"):
                continue

            a_pl, _ = attacker.get_current_pl()
            d_pl, _ = target.get_current_pl()
            gap = pl_gap_effect(a_pl, d_pl)
            base = max(1, int(((attacker.db.strength or 10) + (attacker.db.speed or 10)) / 8))
            
            # Apply combo bonus
            combo = getattr(attacker.db, 'combo_count', 0)
            combo_bonus = 1.0 + (combo * 0.05)  # 5% per combo hit, max 50%
            combo_bonus = min(1.5, combo_bonus)
            
            hit_roll = random.random()
            if hit_roll > gap["hit_bias"]:
                line = f"{attacker.key} misses {target.key}."
                room_lines.setdefault(attacker.location.id, [attacker.location, []])[1].append(line)
                continue

            damage = int(base * gap["damage_mult"])
            
            # Apply combo bonus
            combo = getattr(attacker.db, 'combo_count', 0)
            combo_bonus = 1.0 + (combo * 0.05)  # 5% per combo hit, max 50%
            combo_bonus = min(1.5, combo_bonus)
            damage = int(damage * combo_bonus)
            
            # Apply limb damage penalties
            attacker_limbs = attacker.db.limbs or {}
            limb_penalty = 1.0
            if attacker_limbs.get("left_arm", {}).get("state") in ["broken", "lost"]:
                limb_penalty *= 0.7
            if attacker_limbs.get("right_arm", {}).get("state") in ["broken", "lost"]:
                limb_penalty *= 0.7
            if attacker_limbs.get("left_leg", {}).get("state") in ["broken", "lost"]:
                limb_penalty *= 0.7
            if attacker_limbs.get("right_leg", {}).get("state") in ["broken", "lost"]:
                limb_penalty *= 0.7
            damage = int(damage * limb_penalty)
            
            # Apply rage bonus if attacker is enraged
            if attacker.has_status("rage"):
                rage_data = attacker.get_status_data("rage", {})
                damage_boost = rage_data.get("damage_boost", 1.5)
                damage = int(damage * damage_boost)
            
            dealt = target.apply_damage(damage, source=attacker, kind="tick")
            
            # Increment combo on hit
            if dealt > 0:
                attacker.db.combo_count = combo + 1
                attacker.db.last_combo_hit = time.time()
                
                # Combo milestone messages
                new_combo = combo + 1
                if new_combo == 5:
                    attacker.msg("|c>>> COMBO x5! <<<|n")
                elif new_combo == 10:
                    attacker.msg("|c>>> MEGA COMBO x10! <<<|n")
                elif new_combo == 15:
                    attacker.msg("|c>>> ULTRA COMBO x15! <<<|n")
            
            # Limb damage chance on heavy hits
            if dealt >= 10 and random.random() < 0.08:  # 8% chance on heavy hits
                limb_keys = ["left_arm", "right_arm", "left_leg", "right_leg", "torso"]
                target.damage_limb(random.choice(limb_keys), dealt // 2, source=attacker)
            
            # Epic combat messages based on damage
            if dealt > 15:
                line = f"|r!!! {attacker.key} CRUSHES {target.key} for {dealt}!!!|n"
            elif dealt > 8:
                line = f"|r{attacker.key} smashes {target.key} for {dealt}|n"
            else:
                line = f"|r{attacker.key} clips {target.key} for {dealt}|n"
            
            room_lines.setdefault(attacker.location.id, [attacker.location, []])[1].append(line)
            emit_combat_event(
                attacker.location,
                attacker,
                target,
                {"subtype": "passive_tick", "damage": dealt, "gap_quality": gap["quality"]},
            )

            if target.db.hp_current <= 0:
                disengage(target)
                disengage(attacker)
            else:
                emit_entity_delta(target)

        for _, (room, lines) in room_lines.items():
            if lines:
                room.msg_contents("|rCombat|n " + " ".join(lines[:3]))

    def _process_form_drain(self):
        for obj in list(self._iter_ids(self.db.combatants | self.db.chargers)):
            form_key = obj.db.active_form
            if not form_key:
                continue
            form = FORMS.get(form_key)
            if not form:
                obj.db.active_form = None
                continue
            
            # Process strain accumulation for Kaioken forms with hp_strain_hook
            gameplay = form.get("gameplay", {})
            strain_accum = gameplay.get("strain_accumulation", 0)
            crash_on_drain = gameplay.get("crash_on_drain", False)
            
            if strain_accum > 0:
                current_strain = getattr(obj.db, 'form_strain', 0)
                obj.db.form_strain = current_strain + strain_accum
                
                # Warning messages at strain thresholds
                if obj.db.form_strain == 50:
                    obj.msg("|r>>> WARNING: Body strain at 50%! <<<|n")
                elif obj.db.form_strain == 80:
                    obj.msg("|r>>> CRITICAL: Body strain at 80%! Risk of form crash! <<<|n")
                elif obj.db.form_strain >= 100:
                    # Form crash!
                    obj.msg("|r>>> BODY CANNOT SUSTAIN THE FORM! <<<|n Your body gives out!")
                    obj.db.active_form = None
                    obj.db.form_strain = 0
                    obj.db.hp_current = max(1, int((obj.db.hp_current or 0) * 0.5))
                    emit_vfx(obj.location, "vfx_revert", source=obj)
                    emit_entity_delta(obj)
                    continue
            
            # Drain ki from form
            tick_drain, _debug = get_form_tick_drain(obj, form_key)
            if tick_drain <= 0:
                # Still process strain decay for forms without drain
                if strain_accum > 0 and obj.db.form_strain > 0:
                    obj.db.form_strain = max(0, obj.db.form_strain - 1)
                continue
            
            if not obj.spend_ki(tick_drain):
                obj.msg("|rYou lack the ki to sustain your transformation and revert.|n")
                obj.db.active_form = None
                obj.db.form_strain = 0
                emit_vfx(obj.location, "vfx_revert", source=obj)
            else:
                # Decay strain slightly when successfully spending ki
                if obj.db.form_strain > 0:
                    obj.db.form_strain = max(0, obj.db.form_strain - 1)
                emit_entity_delta(obj)

    def _process_android_heat(self):
        """Process Android heat meter - builds with tech use, decays over time."""
        for obj in list(self._iter_ids(self.db.combatants | self.db.chargers)):
            race = (obj.db.race or "").lower()
            if race != "android":
                continue
            
            # Get or init heat
            heat = getattr(obj.db, 'android_heat', 0)
            max_heat = 100
            
            # Heat decay per tick
            heat_decay = 2  # 2% per second
            heat = max(0, heat - heat_decay)
            
            # Check for overheating
            if heat >= max_heat and not obj.has_status("overheated"):
                obj.add_status("overheated", 10, speed_penalty=0.3, damage_penalty=0.25)
                obj.msg("|r>>> SYSTEM OVERHEAT! <<<|n Android systems compromised!")
                heat = 50  # Reduced after overheat
            
            # Update heat
            obj.db.android_heat = heat
            
            # Emit updates periodically (every 10 ticks)
            if random.random() < 0.1:
                emit_entity_delta(obj)

    def _process_combos(self):
        """Process combo tracking and decay."""
        for obj in list(self._iter_ids(self.db.combatants)):
            combo = getattr(obj.db, 'combo_count', 0)
            last_hit = getattr(obj.db, 'last_combo_hit', 0)
            
            # Decay combo if too long since last hit
            if combo > 0 and (time.time() - last_hit) > 3.0:
                obj.db.combo_count = 0
                obj.msg("|cCombo broken!|n")
