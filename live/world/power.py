"""
Power-level math for the DB vertical slice.
"""

from __future__ import annotations

import math


def _clamp(value, low, high):
    return max(low, min(high, value))


def compute_current_pl(character):
    """
    Return (combat_pl, breakdown).

    combat_pl is used for combat simulation.
    breakdown contains a displayed_pl key used for scans/UI.
    """

    hp = max(0, character.db.hp_current or 1)
    hp_max = max(1, character.db.hp_max or 1)
    ki = max(0, character.db.ki_current or 0)
    ki_max = max(1, character.db.ki_max or 1)

    base_power = max(50, character.db.base_power or 100)
    strength = character.db.strength or 10
    speed = character.db.speed or 10
    balance = character.db.balance or 10
    mastery = character.db.mastery or 10
    ki_control = character.db.ki_control or 0

    stat_factor = 1.0 + ((strength * 0.035) + (speed * 0.03) + (balance * 0.02) + (mastery * 0.015))
    injury_factor = 0.45 + 0.55 * (hp / hp_max)
    ki_ratio = ki / ki_max
    ki_factor = 0.55 + 0.45 * (ki_ratio**0.7)
    charge_stacks = max(0, character.db.charge_stacks or 0)
    charge_factor = 1.0 + min(0.55, charge_stacks * 0.06)

    form_key = character.db.active_form
    form_factor = 1.0
    form_speed_bias = 1.0
    if form_key:
        from world.forms import FORMS, get_form_modifiers

        form = FORMS.get(form_key, {})
        form_mastery = (character.db.form_mastery or {}).get(form_key, 0)
        mastery_bonus = min(0.30, form_mastery * 0.005)
        form_mods = get_form_modifiers(character, form_key)
        form_factor = (form_mods.get("pl_factor", form.get("pl_multiplier", 1.0)) + mastery_bonus)
        form_speed_bias = form_mods.get("speed_bias", form.get("speed_bias", 1.0))

    suppression_factor = character.db.suppression_factor if character.db.suppressed else 1.0
    combat_readiness = 0.94 if character.db.suppressed else 1.0
    control_efficiency = 1.0 + min(0.12, ki_control * 0.004)
    bruised_factor = 1.0
    if hasattr(character, "has_status") and character.has_status("bruised"):
        bruised_factor = character.get_status_data("bruised", {}).get("pl_penalty", 0.92)

    combat_pl = base_power * stat_factor * injury_factor * ki_factor * charge_factor
    combat_pl *= form_factor * form_speed_bias * combat_readiness * control_efficiency * bruised_factor
    combat_pl = int(max(1, combat_pl))

    displayed_pl = int(max(1, combat_pl * suppression_factor))

    return combat_pl, {
        "base_power": base_power,
        "stat_factor": round(stat_factor, 3),
        "injury_factor": round(injury_factor, 3),
        "ki_factor": round(ki_factor, 3),
        "charge_factor": round(charge_factor, 3),
        "form_factor": round(form_factor * form_speed_bias, 3),
        "active_form": form_key or "base",
        "combat_readiness": combat_readiness,
        "control_efficiency": round(control_efficiency, 3),
        "bruised_factor": bruised_factor,
        "suppression_factor": suppression_factor,
        "displayed_pl": displayed_pl,
    }


def pl_gap_effect(attacker_pl, defender_pl):
    """
    Brutal DB-style nonlinear gap scaling.
    """

    ratio = max(0.05, float(attacker_pl) / max(1.0, float(defender_pl)))
    log_ratio = math.log(ratio, 2)

    if ratio >= 8.0:
        quality = "overwhelming"
    elif ratio >= 3.0:
        quality = "dominant"
    elif ratio >= 1.5:
        quality = "favored"
    elif ratio <= 0.125:
        quality = "hopeless"
    elif ratio <= 0.333:
        quality = "outclassed"
    elif ratio <= 0.66:
        quality = "strained"
    else:
        quality = "even"

    damage_mult = _clamp(1.0 + (log_ratio * 0.38), 0.18, 4.2)
    hit_bias = _clamp(0.50 + (log_ratio * 0.16), 0.08, 0.95)
    stagger_bias = _clamp(0.08 + (log_ratio * 0.10), 0.01, 0.85)

    return {
        "ratio": round(ratio, 3),
        "quality": quality,
        "damage_mult": round(damage_mult, 3),
        "hit_bias": round(hit_bias, 3),
        "stagger_bias": round(stagger_bias, 3),
    }
