"""
Legendary Super Saiyan (LSSJ) progression/state system.

Distinct from normal transformations: this tracks unlock state, escalation, control,
mastery and downsides separately while integrating with the form framework and PL hooks.
"""

from __future__ import annotations

from copy import deepcopy

from world.content_core import make_stub_result


LSSJ_CONFIG = {
    "unlock_requirements": {
        "race_any": ["saiyan", "half_breed"],
        "flags_any": ["legendary_seed"],
        "or_quest": "broly_lineage_echoes",
        "ki_control_min": 18,
        "mastery_min": 15,
    },
    "stages": {
        "awakening": {
            "name": "Legendary Awakening",
            "pl_bias": 1.18,
            "damage_bias": 1.10,
            "speed_bias": 1.02,
            "ki_drain_tick": 5,
            "rage_drift": 3,
            "control_penalty": 4,
            "visual_aura": "lssj_green_surge",
        },
        "surge": {
            "name": "Legendary Surge",
            "pl_bias": 1.30,
            "damage_bias": 1.18,
            "speed_bias": 1.03,
            "ki_drain_tick": 8,
            "rage_drift": 5,
            "control_penalty": 8,
            "visual_aura": "lssj_storm_green",
        },
        "cataclysm": {
            "name": "Legendary Cataclysm",
            "pl_bias": 1.45,
            "damage_bias": 1.26,
            "speed_bias": 1.00,
            "ki_drain_tick": 12,
            "rage_drift": 8,
            "control_penalty": 14,
            "visual_aura": "lssj_cataclysm",
        },
    },
    "mastery": {
        "drain_reduction_per_rank": 0.008,
        "control_gain_per_training": 1,
        "rage_decay_bonus_per_rank": 0.05,
        "max_mastery_bonus_pl": 0.10,
    },
    "downsides": {
        "team_safety_risk_threshold": 80,
        "focus_instability_threshold": 65,
        "self_stagger_chance_high_rage": 0.08,
        "post_crash_exhaustion_duration": 12.0,
    },
}

DEFAULT_LSSJ_STATE = {
    "unlocked": False,
    "active": False,
    "stage": None,
    "mastery_rank": 0,
    "control": 40,  # higher is better
    "rage": 0,
    "suppression_training": 0,
    "last_crash": None,
    "lineage_flags": [],
}


def _ensure_state(character):
    state = dict(character.db.lssj_state or {})
    merged = deepcopy(DEFAULT_LSSJ_STATE)
    merged.update(state)
    character.db.lssj_state = merged
    return merged


def _race(character):
    return (character.db.race or "").lower()


def _flags(character):
    flags = set(character.db.account_flags or [])
    flags.update((character.db.story_flags or []) or [])
    state = _ensure_state(character)
    flags.update(state.get("lineage_flags") or [])
    return flags


def meets_unlock_requirements(character):
    req = LSSJ_CONFIG["unlock_requirements"]
    if _race(character) not in req["race_any"]:
        return False, "Only Saiyans and Half-Breeds can awaken Legendary power."
    flags = _flags(character)
    if not any(flag in flags for flag in req["flags_any"]):
        if req.get("or_quest") not in flags:
            return False, "Your lineage has not triggered the Legendary seed."
    if (character.db.ki_control or 0) < req["ki_control_min"]:
        return False, f"Need Ki Control {req['ki_control_min']}."
    if (character.db.mastery or 0) < req["mastery_min"]:
        return False, f"Need Mastery {req['mastery_min']}."
    return True, ""


def unlock_lssj(character, source="quest"):
    state = _ensure_state(character)
    ok, reason = meets_unlock_requirements(character)
    if not ok:
        return False, reason
    state["unlocked"] = True
    if source and source not in (state.get("lineage_flags") or []):
        state.setdefault("lineage_flags", []).append(str(source))
    character.db.lssj_state = state
    return True, "Legendary power unlocked."


def can_activate_lssj(character):
    state = _ensure_state(character)
    if not state.get("unlocked"):
        return False, "Legendary power is not unlocked."
    if _race(character) not in {"saiyan", "half_breed"}:
        return False, "Your race cannot sustain Legendary Super Saiyan."
    if (character.db.ki_current or 0) < 30:
        return False, "Need at least 30 ki."
    return True, ""


def activate_lssj(character, initial_stage="awakening"):
    state = _ensure_state(character)
    ok, reason = can_activate_lssj(character)
    if not ok:
        return False, reason
    stage_key = initial_stage if initial_stage in LSSJ_CONFIG["stages"] else "awakening"
    state["active"] = True
    state["stage"] = stage_key
    state["rage"] = max(state.get("rage", 0), 25)
    # Control starts lower when raw power surges; mastery mitigates this.
    state["control"] = max(20, min(100, state.get("control", 40) - 5 + state.get("mastery_rank", 0) // 3))
    character.db.lssj_state = state
    return True, f"LSSJ activated: {LSSJ_CONFIG['stages'][stage_key]['name']}."


def deactivate_lssj(character, crashed=False):
    state = _ensure_state(character)
    if not state.get("active"):
        return False, "LSSJ is not active."
    state["active"] = False
    state["stage"] = None
    state["rage"] = max(0, state.get("rage", 0) - (40 if crashed else 20))
    if crashed:
        state["last_crash"] = "recent"
    character.db.lssj_state = state
    return True, "LSSJ deactivated."


def train_lssj_control(character, amount=1):
    state = _ensure_state(character)
    state["mastery_rank"] = max(0, state.get("mastery_rank", 0) + int(amount))
    state["control"] = min(100, state.get("control", 40) + int(amount) * LSSJ_CONFIG["mastery"]["control_gain_per_training"])
    character.db.lssj_state = state
    return state


def escalate_lssj(character, force=False):
    state = _ensure_state(character)
    if not state.get("active"):
        return False, "LSSJ is not active."
    order = ["awakening", "surge", "cataclysm"]
    current = state.get("stage") or "awakening"
    idx = order.index(current)
    rage = state.get("rage", 0)
    control = state.get("control", 40)
    thresholds = {"awakening": 45, "surge": 75}
    if idx >= len(order) - 1:
        return False, "Already at maximum Legendary stage."
    need = thresholds.get(current, 999)
    if not force and rage < need:
        return False, f"Need rage {need}+ to escalate."
    if not force and control < 25:
        return False, "Control is too unstable to escalate safely."
    state["stage"] = order[idx + 1]
    state["rage"] = min(100, rage + 10)
    state["control"] = max(0, control - 6)
    character.db.lssj_state = state
    return True, f"LSSJ escalates to {LSSJ_CONFIG['stages'][state['stage']]['name']}."


def tick_lssj_state(character, event=None):
    """
    Advance legendary state. Safe to call from a future combat heartbeat.
    Returns a stub payload for integration logging.
    """
    state = _ensure_state(character)
    if not state.get("active") or not state.get("stage"):
        return make_stub_result("lssj_tick", "lssj", caller=character, payload={"active": False})
    stage = LSSJ_CONFIG["stages"][state["stage"]]
    mastery_rank = state.get("mastery_rank", 0)
    drain_reduction = min(0.6, mastery_rank * LSSJ_CONFIG["mastery"]["drain_reduction_per_rank"])
    drain = max(1, int(stage["ki_drain_tick"] * (1.0 - drain_reduction)))
    character.db.ki_current = max(0, (character.db.ki_current or 0) - drain)
    rage = min(100, state.get("rage", 0) + stage["rage_drift"])
    control_decay = max(1, stage["control_penalty"] - mastery_rank // 5)
    state["rage"] = rage
    state["control"] = max(0, state.get("control", 40) - control_decay)
    crashed = False
    if (character.db.ki_current or 0) <= 0 or state["control"] <= 5:
        crashed = True
        deactivate_lssj(character, crashed=True)
    else:
        character.db.lssj_state = state
    return make_stub_result(
        "lssj_tick",
        "lssj",
        caller=character,
        payload={
            "stage": state.get("stage"),
            "rage": rage,
            "control": state.get("control"),
            "ki_drain": drain,
            "crashed": crashed,
            "event": event or {},
        },
    )


def get_lssj_modifiers(character):
    state = _ensure_state(character)
    if not state.get("active") or not state.get("stage"):
        return {
            "active": False,
            "pl_factor": 1.0,
            "damage_bias": 1.0,
            "speed_bias": 1.0,
            "ki_drain_tick": 0,
            "control_penalty": 0,
            "visual_aura": None,
            "downsides": {},
        }

    stage = LSSJ_CONFIG["stages"][state["stage"]]
    mastery_rank = state.get("mastery_rank", 0)
    mastery_pl_bonus = min(
        LSSJ_CONFIG["mastery"]["max_mastery_bonus_pl"],
        mastery_rank * 0.004,
    )
    rage = state.get("rage", 0)
    control = state.get("control", 40)
    downsides = {
        "focus_instability": rage >= LSSJ_CONFIG["downsides"]["focus_instability_threshold"] and control < 45,
        "ally_risk": rage >= LSSJ_CONFIG["downsides"]["team_safety_risk_threshold"] and control < 35,
        "self_stagger_chance": LSSJ_CONFIG["downsides"]["self_stagger_chance_high_rage"] if rage > 85 else 0.0,
    }
    return {
        "active": True,
        "stage": state["stage"],
        "pl_factor": stage["pl_bias"] + mastery_pl_bonus,
        "damage_bias": stage["damage_bias"],
        "speed_bias": stage["speed_bias"],
        "ki_drain_tick": stage["ki_drain_tick"],
        "control_penalty": stage["control_penalty"],
        "visual_aura": stage["visual_aura"],
        "rage": rage,
        "control": control,
        "mastery_rank": mastery_rank,
        "downsides": downsides,
    }


def get_lssj_ui_state(character):
    state = _ensure_state(character)
    mods = get_lssj_modifiers(character)
    return {
        "config": LSSJ_CONFIG,
        "state": state,
        "modifiers": mods,
    }
