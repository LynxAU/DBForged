"""
Data-driven transformation framework and registry.
"""

from __future__ import annotations

import time
import random

from world.content_core import build_registry, find_by_key_or_name, make_stub_result
from world.transformation_unlocks import (
    check_transformation_roll,
    check_gravity_training_requirement,
    check_death_witness_trigger,
    get_transformation_fail_count,
    register_transformation_failure,
    get_gravity_training_count,
    register_gravity_training,
    get_near_miss_message,
    calculate_form_mastery_bonus,
    get_witness_death_count,
    check_pl_threshold_requirement,
    check_absorption_requirement,
    get_absorption_count,
    register_absorption,
    get_android_mark,
)


def _form(
    key,
    name,
    race,
    tier,
    *,
    desc,
    pl=1.12,
    speed=1.0,
    damage=1.0,
    ki_efficiency=1.0,
    drain_tick=0,
    drain_tech=0,
    mastery_reduction=0.01,
    prereq=None,
    visuals=None,
    gameplay=None,
    aliases=None,
    special_system=None,
):
    return (
        key,
        {
            "id": key,
            "name": name,
            "display_name": name,
            "description": desc,
            "race": race,
            "tier": tier,
            "visuals": visuals
            or {
                "aura": f"aura_{key}",
                "hair_override": None,
                "shader": None,
            },
            "modifiers": {
                "pl_factor": pl,
                "speed_bias": speed,
                "damage_bias": damage,
                "ki_efficiency": ki_efficiency,
            },
            # backward-compatible fields used by current combat/PL code
            "pl_multiplier": pl,
            "speed_bias": speed,
            "mastery_bias": 1.0 + max(0.0, (damage - 1.0) * 0.25),
            "drain_per_tick": drain_tick,
            "drain_per_tech": drain_tech,
            "mastery_drain_reduction": mastery_reduction,
            "resource_drain": {
                "ki_per_tick": drain_tick,
                "ki_per_tech": drain_tech,
                "mastery_reduction_per_rank": mastery_reduction,
                "mastery_extension_hooks": ["duration_extension", "drain_reduction"],
            },
            "prerequisites": prereq or {},
            "gameplay_modifiers": gameplay or {},
            "aliases": aliases or [],
            "special_system": special_system,
            "framework": "TransformationForm",
            "ready_state": "integration_ready",
        },
    )


_FORMS = [
    # Shared / special
    _form(
        "kaioken",
        "Kaioken",
        "any_organic",
        1,
        desc="Explosive short-burst amplification with growing strain and ki bleed.",
        pl=1.14,
        speed=1.06,
        damage=1.08,
        drain_tick=4,
        drain_tech=3,
        prereq={
            "ki_control_min": 16,
            # Meta unlock: Roll-based (push yourself)
            "roll_chance": 0.20,
            "roll_trigger": {"health_max_pct": 40},
        },
        visuals={"aura": "aura_kaioken_red", "shader": "heat_distortion", "hair_override": None},
        gameplay={"hp_strain_hook": True, "anti_stall_bias": 0.08},
    ),
    _form(
        "potential_unleashed",
        "Potential Unleashed",
        "human",
        3,
        desc="Latent power drawn out without unstable rage, emphasizing efficiency and control.",
        pl=1.18,
        speed=1.03,
        damage=1.06,
        ki_efficiency=0.88,
        drain_tick=2,
        drain_tech=1,
        prereq={
            "race": "human",
            # Meta unlock: Roll-based (push yourself in combat)
            "roll_chance": 0.10,
            "roll_trigger": {"health_max_pct": 30},
        },
        visuals={"aura": "aura_potential_white", "shader": "clean_glow", "hair_override": None},
        gameplay={"cooldown_efficiency_bias": 0.08, "focus_resistance": 0.1},
    ),
    # Saiyan / Half-Breed line
    _form(
        "super_saiyan",
        "Super Saiyan",
        "saiyan",
        2,
        desc="The iconic golden awakening: strong all-around boost with manageable drain.",
        pl=1.20,
        speed=1.06,
        damage=1.08,
        drain_tick=5,
        drain_tech=4,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            # Meta unlock: Roll-based (3%) OR Death Witness trigger (20%)
            "roll_chance": 0.03,
            "roll_trigger": {
                "pl_min": 1000,
                "rage_min": 25,
                "health_max_pct": 50,
            },
            "witness_death_trigger": True,
            "witness_chance": 0.20,
            "pl_min": 1000,
            "rage_min": 20,
        },
        visuals={"aura": "aura_ssj_gold", "hair_override": "gold", "shader": "golden_flicker"},
        gameplay={"rage_trigger_bonus": 0.12},
        aliases=["ssj", "supersaiyan"],
    ),
    _form(
        "super_saiyan_grade2",
        "Super Saiyan Grade 2",
        "saiyan",
        3,
        desc="Ascended Saiyan power trading efficiency for heavier striking force.",
        pl=1.26,
        speed=1.01,
        damage=1.13,
        drain_tick=7,
        drain_tech=5,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "requires_form": "super_saiyan",
            "form_mastery_min": 15,
            # Meta unlock: Roll-based
            "roll_chance": 0.05,
            "roll_trigger": {"rage_min": 30},
        },
        visuals={"aura": "aura_ssj_heavy_gold", "hair_override": "gold", "shader": "thick_flare"},
        gameplay={"guard_chip_bonus": 0.1},
    ),
    _form(
        "super_saiyan_grade3",
        "Super Saiyan Grade 3",
        "saiyan",
        3,
        desc="Massive power with reduced mobility; dangerous as a read-based finisher form.",
        pl=1.30,
        speed=0.94,
        damage=1.16,
        drain_tick=8,
        drain_tech=5,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "requires_form": "super_saiyan",
            "form_mastery_min": 20,
            # Meta unlock: Roll-based
            "roll_chance": 0.05,
            "roll_trigger": {"rage_min": 35},
        },
        visuals={"aura": "aura_ssj_grade3", "hair_override": "gold", "shader": "heavy_bloom"},
        gameplay={"anti_guard_bonus": 0.14, "dash_penalty": 0.12},
    ),
    _form(
        "super_saiyan_2",
        "Super Saiyan 2",
        "saiyan",
        4,
        desc="Lightning-laced refinement of Super Saiyan with sharper speed and output.",
        pl=1.32,
        speed=1.10,
        damage=1.12,
        drain_tick=7,
        drain_tech=5,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "requires_form": "super_saiyan",
            "form_mastery_min": 35,
            # Meta unlock: Roll-based
            "roll_chance": 0.05,
            "roll_trigger": {"rage_min": 40},
        },
        visuals={"aura": "aura_ssj2", "hair_override": "gold", "shader": "electric_arcs"},
        gameplay={"combo_bias": 0.12},
        aliases=["ssj2"],
    ),
    _form(
        "super_saiyan_3",
        "Super Saiyan 3",
        "saiyan",
        5,
        desc="Extreme output form with punishing ki drain and commitment-heavy gameplay.",
        pl=1.42,
        speed=1.04,
        damage=1.18,
        drain_tick=12,
        drain_tech=8,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "requires_form": "super_saiyan_2",
            "form_mastery_min": 45,
            "ki_control_min": 24,
            # Meta unlock: Roll-based
            "roll_chance": 0.04,
            "roll_trigger": {"rage_min": 50},
        },
        visuals={"aura": "aura_ssj3", "hair_override": "ssj3_long", "shader": "violent_gold"},
        gameplay={"charge_bonus": 0.16, "sustain_penalty": True},
        aliases=["ssj3"],
    ),
    _form(
        "super_saiyan_god",
        "Super Saiyan God",
        "saiyan",
        6,
        desc="Lean godly ki form emphasizing control, efficiency and precision over brute force.",
        pl=1.36,
        speed=1.08,
        damage=1.10,
        ki_efficiency=0.82,
        drain_tick=4,
        drain_tech=3,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "ki_control_min": 30,
            # Meta unlock: Requires high ki control + roll
            "roll_chance": 0.05,
            "roll_trigger": {"health_max_pct": 30, "rage_min": 35},
        },
        visuals={"aura": "aura_ssg_red", "hair_override": "red", "shader": "god_flame"},
        gameplay={"sense_clarity_bonus": 0.15, "cooldown_efficiency_bias": 0.1},
        aliases=["ssg"],
    ),
    _form(
        "super_saiyan_blue",
        "Super Saiyan Blue",
        "saiyan",
        7,
        desc="God ki stabilized through Super Saiyan, rewarding discipline and high ki control.",
        pl=1.44,
        speed=1.10,
        damage=1.14,
        ki_efficiency=0.9,
        drain_tick=8,
        drain_tech=6,
        prereq={
            "race_any": ["saiyan", "half_breed"],
            "requires_form": "super_saiyan_god",
            "ki_control_min": 36,
            # Meta unlock: Requires SSG mastered + roll
            "roll_chance": 0.04,
            "roll_trigger": {"rage_min": 40},
        },
        visuals={"aura": "aura_ssb_blue", "hair_override": "blue", "shader": "god_spark"},
        gameplay={"beam_stability_bonus": 0.12},
        aliases=["ssb", "super_saiyan_blu"],
    ),
    _form(
        "beast",
        "Beast",
        "half_breed",
        7,
        desc="A sharp, instinctive surge of latent hybrid potential with burst-heavy offense.",
        pl=1.43,
        speed=1.07,
        damage=1.17,
        drain_tick=9,
        drain_tech=6,
        prereq={
            "race": "half_breed",
            "mastery_min": 28,
            # Meta unlock: Roll-based
            "roll_chance": 0.04,
            "roll_trigger": {"rage_min": 45, "health_max_pct": 25},
        },
        visuals={"aura": "aura_beast_white", "hair_override": "beast_white", "shader": "violet_crackle"},
        gameplay={"counter_bonus": 0.14, "rage_trigger_bonus": 0.08},
    ),
    _form(
        "legendary_super_saiyan",
        "Legendary Super Saiyan",
        "saiyan",
        99,
        desc="Delegates to the distinct Legendary state machine (LSSJ) for stages/control.",
        pl=1.0,
        speed=1.0,
        damage=1.0,
        drain_tick=0,
        drain_tech=0,
        prereq={"race_any": ["saiyan", "half_breed"], "special_unlock": "lssj"},
        visuals={"aura": "aura_lssj_green", "hair_override": "green_gold", "shader": "legendary_storm"},
        gameplay={"delegates_to_lssj_system": True},
        special_system="lssj",
        aliases=["lssj", "legendary"],
    ),
    # Namekian
    # Note: Namekians don't have rage-based transformations. Their "first transformation"
    # comes from fusion - see namekian_fusion.py. Giant form requires fusion first.
    _form(
        "giant_namekian",
        "Giant Namekian",
        "namekian",
        3,
        desc="Expand body size and leverage for reach and control at some mobility cost.",
        pl=1.23,
        speed=0.95,
        damage=1.12,
        drain_tick=5,
        drain_tech=2,
        prereq={
            "race": "namekian",
            # Namekians must fuse first (require fused flag)
            "requires_fusion": True,
        },
        visuals={"aura": "aura_namekian_giant", "shader": "scale_up"},
        gameplay={"reach_bonus": 2, "knockback_resist": 0.12},
    ),
    _form(
        "dragon_clan_focus",
        "Dragon Clan Focus",
        "namekian",
        2,
        desc="Meditative Namekian combat focus prioritizing ki control and recovery.",
        pl=1.15,
        speed=1.01,
        damage=1.03,
        ki_efficiency=0.84,
        drain_tick=2,
        drain_tech=1,
        prereq={"race": "namekian", "trainer": "piccolo"},
        visuals={"aura": "aura_namekian_calm", "shader": "jade_glow"},
        gameplay={"regen_bonus": 0.14, "seal_bonus": 0.1},
    ),
    # Human
    _form(
        "max_power",
        "Max Power",
        "human",
        2,
        desc="Old-school human muscle-up burst with strong melee pressure and brief sustain.",
        pl=1.17,
        speed=0.98,
        damage=1.10,
        drain_tick=4,
        drain_tech=2,
        prereq={
            "race": "human",
            "trainer": "master_roshi",
            # Roll-based transformation
            "roll_chance": 0.10,
            "roll_trigger": {"health_max_pct": 35},
        },
        visuals={"aura": "aura_max_power", "shader": "steam"},
        gameplay={"melee_bonus": 0.12, "beam_penalty": 0.05},
    ),
    # Majin
    _form(
        "super_majin",
        "Super Majin",
        "majin",
        3,
        desc="Majin body elasticity and output rise together, improving sustain and pressure.",
        pl=1.22,
        speed=1.02,
        damage=1.10,
        drain_tick=4,
        drain_tech=2,
        prereq={
            "race": "majin",
            # Meta unlock: Roll-based (anger-based)
            "roll_chance": 0.05,
            "roll_trigger": {"rage_min": 30},
        },
        visuals={"aura": "aura_majin_pink", "shader": "rubber_sheen"},
        gameplay={"regen_bonus": 0.12, "guard_recovery_bonus": 0.1},
    ),
    _form(
        "pure_majin",
        "Pure Majin",
        "majin",
        4,
        desc="Wild, chaotic Majin combat mode with strong offense and weaker control.",
        pl=1.29,
        speed=1.08,
        damage=1.14,
        drain_tick=8,
        drain_tech=5,
        prereq={
            "race": "majin",
            "requires_form": "super_majin",
            # Meta unlock: Roll-based
            "roll_chance": 0.04,
            "roll_trigger": {"rage_min": 40},
        },
        visuals={"aura": "aura_pure_majin", "shader": "chaos_flicker"},
        gameplay={"control_penalty": 0.1, "rush_bonus": 0.14},
    ),
    # Android
    _form(
        "android_overclock",
        "Android Overclock",
        "android",
        2,
        desc="Overclock servos and targeting; no ki drain but heat/instability hooks apply.",
        pl=1.18,
        speed=1.10,
        damage=1.07,
        drain_tick=0,
        drain_tech=0,
        prereq={
            "race": "android",
            # Meta unlock: PL threshold based (Mark upgrade system)
            "unlock_type": "pl_threshold",
            "pl_min": 5000,
        },
        visuals={"aura": "aura_android_blue", "shader": "scanlines"},
        gameplay={"uses_heat_meter_hook": True, "cooldown_bonus": 0.08},
    ),
    _form(
        "infinite_drive",
        "Infinite Drive",
        "android",
        4,
        desc="Advanced reactor mode with sustained throughput and strong ki economy identity.",
        pl=1.26,
        speed=1.06,
        damage=1.10,
        ki_efficiency=0.72,
        drain_tick=0,
        drain_tech=0,
        prereq={
            "race": "android",
            "requires_form": "android_overclock",
            # Meta unlock: PL threshold based
            "unlock_type": "pl_threshold",
            "pl_min": 15000,
        },
        visuals={"aura": "aura_android_infinite", "shader": "clean_neon"},
        gameplay={"resource_regen_bonus": 0.15},
    ),
    # Biodroid
    _form(
        "biodroid_stage_two",
        "Biodroid Stage Two",
        "biodroid",
        2,
        desc="First major biodroid evolution, improving output and adaptive durability.",
        pl=1.18,
        speed=1.02,
        damage=1.08,
        drain_tick=3,
        drain_tech=2,
        prereq={
            "race_any": ["biodroid", "bio_android"],
            # Meta unlock: Absorption-based (absorb NPCs to grow)
            "unlock_type": "absorption",
            "absorbs_min": 5,
        },
        visuals={"aura": "aura_biodroid_stage2", "shader": "cell_sheen"},
        gameplay={"adaptive_resist_hook": True},
    ),
    _form(
        "biodroid_perfect",
        "Perfect Biodroid",
        "biodroid",
        4,
        desc="Perfected biodroid morphology balancing offense, defense, and efficiency.",
        pl=1.31,
        speed=1.07,
        damage=1.13,
        ki_efficiency=0.86,
        drain_tick=4,
        drain_tech=3,
        prereq={
            "race_any": ["biodroid", "bio_android"],
            "requires_form": "biodroid_stage_two",
            # Meta unlock: Absorption-based
            "unlock_type": "absorption",
            "absorbs_min": 15,
        },
        visuals={"aura": "aura_biodroid_perfect", "shader": "green_metallic"},
        gameplay={"copy_tech_bonus_hook": True},
    ),
    _form(
        "super_perfect_biodroid",
        "Super Perfect Biodroid",
        "biodroid",
        5,
        desc="A volatile perfected state with high pressure and comeback-oriented spikes.",
        pl=1.39,
        speed=1.08,
        damage=1.16,
        drain_tick=7,
        drain_tech=5,
        prereq={
            "race_any": ["biodroid", "bio_android"],
            "requires_form": "biodroid_perfect",
            # Meta unlock: Absorption-based
            "unlock_type": "absorption",
            "absorbs_min": 30,
        },
        visuals={"aura": "aura_biodroid_super_perfect", "shader": "electric_green"},
        gameplay={"revenge_power_hook": True},
    ),
    # Frost Demon
    _form(
        "frost_demon_true_form",
        "True Form",
        "frost_demon",
        2,
        desc="A fuller Frost Demon battle body with increased output and menace.",
        pl=1.19,
        speed=1.03,
        damage=1.09,
        drain_tick=3,
        drain_tech=2,
        prereq={
            "race": "frost_demon",
            # Meta unlock: Roll-based (push yourself)
            "roll_chance": 0.10,
            "roll_trigger": {"health_max_pct": 40},
        },
        visuals={"aura": "aura_frost_true", "shader": "cold_glow"},
        gameplay={"fear_pressure_hook": True},
    ),
    _form(
        "frost_demon_final_form",
        "Final Form",
        "frost_demon",
        4,
        desc="Streamlined final battle form emphasizing efficiency and lethal precision.",
        pl=1.30,
        speed=1.08,
        damage=1.11,
        ki_efficiency=0.82,
        drain_tick=4,
        drain_tech=2,
        prereq={
            "race": "frost_demon",
            "requires_form": "frost_demon_true_form",
            # Meta unlock: Roll-based
            "roll_chance": 0.08,
            "roll_trigger": {"health_max_pct": 30},
        },
        visuals={"aura": "aura_frost_final", "shader": "violet_cold"},
        gameplay={"death_beam_bonus": 0.16},
    ),
    _form(
        "golden_frost",
        "Golden Form",
        "frost_demon",
        6,
        desc="High-output golden Frost Demon state with notable strain unless refined.",
        pl=1.41,
        speed=1.10,
        damage=1.15,
        drain_tick=9,
        drain_tech=6,
        prereq={
            "race": "frost_demon",
            "requires_form": "frost_demon_final_form",
            # Meta unlock: Roll-based
            "roll_chance": 0.05,
            "roll_trigger": {"health_max_pct": 20},
        },
        visuals={"aura": "aura_gold_frost", "shader": "gold_metal"},
        gameplay={"stamina_discipline_hook": True},
    ),
    # Grey
    _form(
        "meditative_limit",
        "Meditative Limit",
        "grey",
        2,
        desc="Combat meditation that hardens focus and psychic throughput without flashy output.",
        pl=1.16,
        speed=1.02,
        damage=1.06,
        ki_efficiency=0.86,
        drain_tick=2,
        drain_tech=1,
        prereq={
            "race": "grey",
            # Meta unlock: Roll-based (push yourself)
            "roll_chance": 0.10,
            "roll_trigger": {"health_max_pct": 30},
        },
        visuals={"aura": "aura_grey_focus", "shader": "heatless_white"},
        gameplay={"control_resistance": 0.15, "counter_bonus": 0.08},
    ),
    _form(
        "grey_limit_break",
        "Limit Break State",
        "grey",
        5,
        desc="A disciplined breaking of internal limits, built around resolve rather than rage.",
        pl=1.34,
        speed=1.05,
        damage=1.14,
        drain_tick=7,
        drain_tech=4,
        prereq={
            "race": "grey",
            "requires_form": "meditative_limit",
            # Meta unlock: Roll-based
            "roll_chance": 0.05,
            "roll_trigger": {"health_max_pct": 25},
        },
        visuals={"aura": "aura_grey_limit_break", "shader": "red_ring"},
        gameplay={"guard_break_resist": 0.14, "stagger_resist": 0.12},
    ),
    # Kai
    _form(
        "kai_unsealed",
        "Kai Unsealed State",
        "kai",
        3,
        desc="A Kai's divine reserves open, improving support, control and godly precision.",
        pl=1.20,
        speed=1.02,
        damage=1.07,
        ki_efficiency=0.78,
        drain_tick=2,
        drain_tech=1,
        prereq={
            "race": "kai",
            # Meta unlock: Roll-based (push yourself)
            "roll_chance": 0.15,
            "roll_trigger": {"health_max_pct": 40},
        },
        visuals={"aura": "aura_kai_divine", "shader": "halo_particles"},
        gameplay={"support_bonus": 0.2, "seal_bonus": 0.12},
    ),
    _form(
        "godly_empowerment",
        "Godly Empowerment",
        "kai",
        5,
        desc="Battle-ready divine empowerment balancing offense with supreme ki economy.",
        pl=1.30,
        speed=1.06,
        damage=1.10,
        ki_efficiency=0.74,
        drain_tick=3,
        drain_tech=1,
        prereq={
            "race": "kai",
            "requires_form": "kai_unsealed",
            # Meta unlock: Roll-based
            "roll_chance": 0.08,
            "roll_trigger": {"health_max_pct": 30},
        },
        visuals={"aura": "aura_kai_empowered", "shader": "divine_goldwhite"},
        gameplay={"telekinesis_bonus": 0.16, "sense_bonus": 0.18},
    ),
    # Truffle/Tuffle
    _form(
        "truffle_machine_merge",
        "Truffle Machine Merge",
        "truffle",
        2,
        desc="Merge with a support machine shell for enhanced analysis and ranged pressure.",
        pl=1.15,
        speed=1.00,
        damage=1.08,
        ki_efficiency=0.84,
        drain_tick=1,
        drain_tech=1,
        prereq={
            "race": "truffle",
            # Meta unlock: Roll-based
            "roll_chance": 0.12,
            "roll_trigger": {"health_max_pct": 50},
        },
        visuals={"aura": "aura_tuffle_teal", "shader": "hex_grid"},
        gameplay={"scanner_bonus": 0.2, "trap_bonus": 0.12},
    ),
    _form(
        "truffle_parasite_overdrive",
        "Truffle Parasite Overdrive",
        "truffle",
        4,
        desc="An aggressive parasitic control mode trading subtlety for battlefield disruption.",
        pl=1.24,
        speed=1.03,
        damage=1.10,
        drain_tick=5,
        drain_tech=3,
        prereq={
            "race": "truffle",
            "requires_form": "truffle_machine_merge",
            # Meta unlock: Roll-based
            "roll_chance": 0.08,
            "roll_trigger": {"health_max_pct": 35},
        },
        visuals={"aura": "aura_tuffle_overdrive", "shader": "infective_noise"},
        gameplay={"debuff_bonus": 0.16, "possession_hook": True},
    ),
    # Android/biotech crossover generic
    _form(
        "bioarmor_carapace",
        "Bioarmor Carapace",
        "biodroid",
        2,
        desc="Hardened living armor state favoring defense and attrition over speed.",
        pl=1.17,
        speed=0.97,
        damage=1.07,
        drain_tick=3,
        drain_tech=1,
        prereq={"race_any": ["biodroid", "bio_android"], "trainer": "cell_shade"},
        visuals={"aura": "aura_bioarmor", "shader": "chitin_sheen"},
        gameplay={"damage_reduction_bias": 0.1},
    ),
]


FORMS = build_registry(_FORMS)
TRANSFORMATIONS = FORMS


def get_form(key_or_name):
    return find_by_key_or_name(FORMS, key_or_name)


def _norm_race(race):
    return (race or "").lower().replace("-", "_").replace(" ", "_")


def _character_race(character):
    race = _norm_race(getattr(character.db, "race", "") if hasattr(character, "db") else character)
    if race == "bio_android":
        return "biodroid"
    if race == "halfbreed":
        return "half_breed"
    if race == "tuffle":
        return "truffle"
    return race


def _meets_race(form, race):
    req = form.get("prerequisites", {})
    if form.get("race") == "any_organic":
        return race not in {"android"}
    if req.get("race_any"):
        return race in {_norm_race(r) for r in req["race_any"]}
    if req.get("race"):
        return race == _norm_race(req["race"])
    # fallback to form.race
    return race == _norm_race(form.get("race"))


def _check_prereqs(character, form_key, form):
    race = _character_race(character)
    if not _meets_race(form, race):
        return False, f"{form['name']} is not available to your race."
    
    req = form.get("prerequisites", {})
    
    # Check ki_control requirement
    if req.get("ki_control_min") and (character.db.ki_control or 0) < req["ki_control_min"]:
        return False, f"Need Ki Control {req['ki_control_min']}."
    
    # Check mastery requirement
    if req.get("mastery_min") and (character.db.mastery or 0) < req["mastery_min"]:
        return False, f"Need Mastery {req['mastery_min']}."
    
    # Check requires_form (must have previous form unlocked)
    if req.get("requires_form"):
        known_forms = set(character.db.unlocked_forms or [])
        if req["requires_form"] not in known_forms and character.db.active_form != req["requires_form"]:
            return False, f"Requires {req['requires_form']} unlocked."
    
    # Check form_mastery requirement
    if req.get("form_mastery_min"):
        needed_form = req.get("requires_form") or form_key
        mastery = (character.db.form_mastery or {}).get(needed_form, 0)
        if mastery < req["form_mastery_min"]:
            return False, f"Requires {needed_form} mastery {req['form_mastery_min']}."
    
    # Check gravity training requirements
    ok, msg = check_gravity_training_requirement(character, form)
    if not ok:
        return False, msg
    
    # Check death witness trigger requirements
    ok, msg = check_death_witness_trigger(character, form)
    if not ok:
        return False, msg
    
    # Check PL threshold requirements (Android Mark upgrades)
    ok, msg = check_pl_threshold_requirement(character, form)
    if not ok:
        return False, msg
    
    # Check absorption requirements (Bio-Android)
    ok, msg = check_absorption_requirement(character, form)
    if not ok:
        return False, msg
    
    # Check random roll transformation (for first transformations)
    # Only runs if unlock_type is "roll" or if roll_chance/roll_trigger is explicitly set
    unlock_type = req.get("unlock_type")
    if unlock_type == "roll" or req.get("roll_chance") or req.get("roll_trigger"):
        ok, msg = check_transformation_roll(character, form_key, form, race)
        if not ok:
            return False, msg
    
    # Check LSSJ special unlock
    if req.get("special_unlock") == "lssj":
        from world.lssj import can_activate_lssj

        ok, msg = can_activate_lssj(character)
        return (ok, msg or "") if not ok else (True, "")
    
    return True, ""


def list_forms_for_race(race):
    race = _character_race(race)
    results = []
    for key, form in FORMS.items():
        if _meets_race(form, race):
            results.append((key, form))
    return sorted(results, key=lambda item: (item[1].get("tier", 0), item[1].get("name", item[0])))


def get_form_modifiers(character, form_key=None):
    key = form_key or getattr(character.db, "active_form", None)
    if not key:
        return {
            "pl_factor": 1.0,
            "speed_bias": 1.0,
            "damage_bias": 1.0,
            "ki_efficiency": 1.0,
            "drain_per_tick": 0,
            "drain_per_tech": 0,
            "source": None,
            "lssj": None,
        }
    form = FORMS.get(key, {})
    mods = dict(form.get("modifiers", {}))
    mods.setdefault("pl_factor", form.get("pl_multiplier", 1.0))
    mods.setdefault("speed_bias", form.get("speed_bias", 1.0))
    mods.setdefault("damage_bias", 1.0)
    mods.setdefault("ki_efficiency", 1.0)
    mods["drain_per_tick"] = form.get("drain_per_tick", 0)
    mods["drain_per_tech"] = form.get("drain_per_tech", 0)
    mods["source"] = key
    try:
        from world.racials import get_racial_hook_value

        drain_reduction = float(get_racial_hook_value(character, "form_drain_reduction", 0.0) or 0.0)
        if drain_reduction > 0:
            mods["drain_per_tick"] = max(0, int(round(mods["drain_per_tick"] * (1.0 - min(0.6, drain_reduction)))))
            mods["drain_per_tech"] = max(0, int(round(mods["drain_per_tech"] * (1.0 - min(0.6, drain_reduction)))))
            mods["racial_form_drain_reduction"] = min(0.6, drain_reduction)
    except Exception:
        pass

    if form.get("special_system") == "lssj":
        from world.lssj import get_lssj_modifiers

        lssj_mods = get_lssj_modifiers(character)
        mods["lssj"] = lssj_mods
        if lssj_mods.get("active"):
            mods["pl_factor"] *= lssj_mods.get("pl_factor", 1.0)
            mods["speed_bias"] *= lssj_mods.get("speed_bias", 1.0)
            mods["damage_bias"] *= lssj_mods.get("damage_bias", 1.0)
            mods["drain_per_tick"] += lssj_mods.get("ki_drain_tick", 0)
    return mods


def get_form_tick_drain(character, form_key=None):
    key = form_key or getattr(character.db, "active_form", None)
    if not key or key not in FORMS:
        return 0, {"active": False, "form_key": key}
    form = FORMS[key]
    mods = get_form_modifiers(character, key)
    mastery = (character.db.form_mastery or {}).get(key, 0)
    reduction = min(0.7, mastery * form.get("mastery_drain_reduction", 0.0))
    base_drain = int(max(0, mods.get("drain_per_tick", form.get("drain_per_tick", 0)) or 0))
    drain = max(0, int(base_drain * (1.0 - reduction)))
    return drain, {
        "active": True,
        "form_key": key,
        "mastery": mastery,
        "mastery_reduction": reduction,
        "base_drain": base_drain,
        "mods": mods,
    }


def activate_form(character, form_key, context=None):
    if form_key not in FORMS:
        return False, "Unknown form.", None
    form = FORMS[form_key]
    ok, reason = _check_prereqs(character, form_key, form)
    if not ok:
        return False, reason, None
    if getattr(character.db, "active_form", None) == form_key:
        return False, "Already in that form.", None
    if form.get("special_system") == "lssj":
        from world.lssj import activate_lssj

        success, msg = activate_lssj(character)
        if not success:
            return False, msg, None
        character.db.active_form = form_key
    else:
        character.db.active_form = form_key
    
    # Set transformation start time for mastery tracking
    import time
    character.db.trans_start_time = time.time()
    character.db.trans_last_warning = 0  # Reset warning state
    
    # Handle Kaioken special start
    if form_key == "kaioken":
        activate_kaioken(character)
    
    # Show mastery info to player
    mastery = dict(character.db.form_mastery or {})
    current_mastery = mastery.get(form_key, 0)
    duration = get_transformation_duration(character, form_key)
    
    mastery_msg = ""
    if current_mastery > 0:
        if current_mastery >= 100:
            mastery_msg = f" |x( mastery: {current_mastery}%, can hold indefinitely)"
        else:
            mastery_msg = f" |x( mastery: {current_mastery}%, can hold {duration:.0f} seconds)"
    
    mastery[form_key] = mastery.get(form_key, 0) + 1
    character.db.form_mastery = mastery
    unlocked = set(character.db.unlocked_forms or [])
    unlocked.add(form_key)
    character.db.unlocked_forms = sorted(unlocked)
    stub = make_stub_result(
        "form_activate",
        form_key,
        caller=character,
        payload={"context": context or {}, "form": form},
    )
    return True, f"You transform into {form['name']}!{mastery_msg}", stub


def deactivate_form(character, reason="manual"):
    active = getattr(character.db, "active_form", None)
    if not active:
        return False, "You are already in base form.", None
    form = FORMS.get(active, {})
    if form.get("special_system") == "lssj":
        from world.lssj import deactivate_lssj

        deactivate_lssj(character, crashed=(reason == "crash"))
    character.db.active_form = None
    # Clear transformation start time
    character.db.trans_start_time = None
    # Handle Kaioken special cleanup
    if active == "kaioken":
        deactivate_kaioken(character)
    return True, "You revert to base form.", make_stub_result(
        "form_deactivate",
        active,
        caller=character,
        payload={"reason": reason},
    )


def get_transformation_duration(character, form_key):
    """
    Calculate how long a transformation can be held.
    Base: 60 seconds
    Bonus: +2.4 seconds per mastery point (max 300s at 100 mastery)
    """
    mastery = (character.db.form_mastery or {}).get(form_key, 0)
    base_duration = 60
    bonus_per_point = 2.4
    max_duration = 300  # 5 minutes at max mastery
    duration = base_duration + (mastery * bonus_per_point)
    return min(duration, max_duration)


def get_transformation_time_remaining(character):
    """
    Get remaining transformation time and percentage.
    Returns (remaining_seconds, percentage_remaining, is_expired)
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return 0, 0, False
    
    start_time = getattr(character.db, "trans_start_time", None)
    if not start_time:
        return 0, 0, False
    
    import time
    elapsed = time.time() - start_time
    max_duration = get_transformation_duration(character, active)
    remaining = max(0, max_duration - elapsed)
    percentage = (remaining / max_duration) * 100 if max_duration > 0 else 0
    
    return remaining, percentage, elapsed >= max_duration


def check_transformation_warnings(character):
    """
    Check if transformation warnings need to be displayed.
    Returns warning message if threshold crossed, None otherwise.
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return None
    
    start_time = getattr(character.db, "trans_start_time", None)
    if not start_time:
        return None
    
    import time
    elapsed = time.time() - start_time
    max_duration = get_transformation_duration(character, active)
    percentage = (elapsed / max_duration) * 100 if max_duration > 0 else 0
    
    # Track last warning sent to avoid spam
    last_warning = getattr(character.db, "trans_last_warning", 0)
    
    if percentage >= 90 and last_warning < 90:
        character.db.trans_last_warning = 90
        return "Your transformation is slipping! You can't hold this form much longer!"
    elif percentage >= 80 and last_warning < 80:
        character.db.trans_last_warning = 80
        return "Your golden aura flickers..."
    
    return None


def apply_transformation_mastery_gain(character):
    """
    Apply mastery gain while transformed.
    +1 mastery per 10 seconds while in form.
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return 0
    
    start_time = getattr(character.db, "trans_start_time", None)
    if not start_time:
        return 0
    
    import time
    elapsed = time.time() - start_time
    
    # Get current mastery
    mastery_dict = dict(character.db.form_mastery or {})
    current_mastery = mastery_dict.get(active, 0)
    
    # Calculate mastery gain: +1 per 10 seconds
    # But cap at 100
    if current_mastery >= 100:
        return current_mastery
    
    # Calculate how much mastery should have been gained
    expected_mastery = min(100, int(elapsed / 10))
    
    if expected_mastery > current_mastery:
        mastery_dict[active] = expected_mastery
        character.db.form_mastery = mastery_dict
        return expected_mastery
    
    return current_mastery


def apply_transformation_pl_drain(character):
    """
    Apply PL drain while transformed.
    SSJ1: 1% max PL per minute
    SSJ2: 2% max PL per minute
    SSJ3: 3% max PL per minute
    SSJ4: 4% max PL per minute
    SSJ5: 5% max PL per minute
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return 0
    
    # Get drain rate based on form tier
    form = FORMS.get(active, {})
    tier = form.get("tier", 1)
    
    # Drain rates: 1% at tier 1, up to 5% at tier 5
    drain_rates = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    rate = drain_rates.get(tier, 1)
    
    # Calculate per-second drain (rate / 60)
    from world.power import compute_current_pl
    pl, _ = compute_current_pl(character)
    max_pl = character.db.base_power * 50  # Approximate max PL
    
    # Apply 1 second worth of drain
    drain = (max_pl * (rate / 100)) / 60
    
    # Apply to HP as drain (transformations drain your life force)
    current_hp = character.db.hp_current or 0
    if current_hp > 0:
        character.db.hp_current = max(1, current_hp - int(drain))
        
        # Check if too weak to maintain transformation
        hp_percentage = (character.db.hp_current / (character.db.hp_max or 1)) * 100
        if hp_percentage < 10:
            deactivate_form(character, reason="exhausted")
            return -1  # Signal deactivation
    
    return drain


def handle_transformation_timeout(character):
    """
    Check and handle transformation timeout.
    Returns True if transformation was reverted due to timeout.
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return False
    
    remaining, percentage, is_expired = get_transformation_time_remaining(character)
    
    if is_expired:
        deactivate_form(character, reason="timeout")
        character.msg("|yYour transformation fades away... you can no longer maintain this form.|n")
        return True
    
    return False


def get_form_mastery_display(character):
    """
    Get formatted display of all form mastery levels.
    """
    mastery_dict = character.db.form_mastery or {}
    unlocked = character.db.unlocked_forms or []
    
    lines = ["", "|yTransformation Mastery:|n"]
    
    for form_key in unlocked:
        if form_key not in FORMS:
            continue
        form = FORMS[form_key]
        mastery = mastery_dict.get(form_key, 0)
        duration = get_transformation_duration(character, form_key)
        
        if mastery >= 100:
            status = "|g[n indefinite]|n"
        else:
            status = f"[|g{duration:.0f}s|n hold time]"
        
        lines.append(f"  {form['name']}: |c{mastery}%|n {status}")
    
    return "\n".join(lines)


# =============================================================================
# KAIOKEN HOLD-DOWN SYSTEM
# =============================================================================

def get_kaioken_multiplier(character):
    """
    Calculate Kaioken multiplier based on hold time.
    Multiplier = elapsed_seconds * 2 (max x20 at 10s)
    """
    active = getattr(character.db, "active_form", None)
    if active != "kaioken":
        return 1
    
    start_time = getattr(character.db, "kaioken_start_time", None)
    if not start_time:
        return 1
    
    import time
    elapsed = time.time() - start_time
    
    # Cap at 10 seconds = max multiplier of 20
    capped_elapsed = min(elapsed, 10)
    multiplier = int(capped_elapsed * 2)
    
    return max(1, multiplier)


def get_kaioken_self_damage(character):
    """
    Calculate self-damage from Kaioken hold.
    Damage = elapsed_seconds^2 (1, 4, 9, 16... 100)
    """
    active = getattr(character.db, "active_form", None)
    if active != "kaioken":
        return 0
    
    start_time = getattr(character.db, "kaioken_start_time", None)
    if not start_time:
        return 0
    
    import time
    elapsed = time.time() - start_time
    
    # Cap at 10 seconds
    capped_elapsed = min(elapsed, 10)
    damage = int(capped_elapsed ** 2)
    
    return damage


def apply_kaioken_drain(character):
    """
    Apply self-damage while using Kaioken.
    Also handles warning messages and force revert on low HP.
    Returns (damage_dealt, warning_message, should_revert)
    """
    active = getattr(character.db, "active_form", None)
    if active != "kaioken":
        return 0, None, False
    
    # Calculate self-damage
    damage = get_kaioken_self_damage(character)
    if damage > 0:
        character.db.hp_current = max(1, (character.db.hp_current or 1) - damage)
    
    # Check for warning (5+ seconds)
    start_time = getattr(character.db, "kaioken_start_time", None)
    warning = None
    if start_time:
        import time
        elapsed = time.time() - start_time
        last_warning = getattr(character.db, "kaioken_last_warning", 0)
        
        if elapsed >= 5 and last_warning < 5:
            character.db.kaioken_last_warning = 5
            warning = "|rYour body is straining from Kaioken! You can't hold this much longer!|n"
    
    # Check if HP is too low
    hp_percentage = ((character.db.hp_current or 1) / (character.db.hp_max or 1)) * 100
    should_revert = hp_percentage < 10
    
    if should_revert:
        deactivate_form(character, reason="exhausted")
        character.msg("|rYour body can't handle the Kaioken strain! You revert to normal form.|n")
    
    return damage, warning, should_revert


def activate_kaioken(character):
    """
    Activate Kaioken - starts the hold timer.
    """
    import time
    character.db.kaioken_start_time = time.time()
    character.db.kaioken_last_warning = 0


def deactivate_kaioken(character):
    """
    Deactivate Kaioken - clear the hold timer.
    """
    character.db.kaioken_start_time = None
    character.db.kaioken_last_warning = 0
    character.db.kaioken_multiplier = 1


def apply_form_drain_tick(character, event=None):
    """
    Safe heartbeat stub for future combat/service loop integration.
    Handles Ki drain, PL drain, mastery gain, timeout warnings, and auto-revert.
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return make_stub_result("form_tick", "base", caller=character, payload={"active": False})
    
    form = FORMS.get(active, {})
    
    # Check for transformation timeout first
    if handle_transformation_timeout(character):
        # Transformation was reverted due to timeout
        return make_stub_result(
            "form_tick",
            active,
            caller=character,
            payload={"active": False, "reason": "timeout"},
        )
    
    # Check and send warning messages
    warning = check_transformation_warnings(character)
    
    # Apply mastery gain while transformed
    mastery = apply_transformation_mastery_gain(character)
    
    # Apply PL drain while transformed
    pl_drain = apply_transformation_pl_drain(character)
    
    # Original Ki drain logic
    drain, debug = get_form_tick_drain(character, active)
    mods = debug.get("mods", get_form_modifiers(character, active))
    mastery = debug.get("mastery", (character.db.form_mastery or {}).get(active, 0))
    if drain:
        character.db.ki_current = max(0, (character.db.ki_current or 0) - drain)
    if (character.db.ki_current or 0) <= 0 and active:
        deactivate_form(character, reason="exhausted")
    
    # Check HP for transformation maintenance
    hp_percentage = ((character.db.hp_current or 0) / (character.db.hp_max or 1)) * 100
    
    # Apply Kaioken-specific drain (self-damage while holding Kaioken)
    kaioken_damage = 0
    kaioken_warning = None
    kaioken_revert = False
    if active == "kaioken":
        kaioken_damage, kaioken_warning, kaioken_revert = apply_kaioken_drain(character)
    
    return make_stub_result(
        "form_tick",
        active,
        caller=character,
        payload={
            "drain": drain,
            "pl_drain": pl_drain,
            "mastery": mastery,
            "warning": warning,
            "hp_percentage": hp_percentage,
            "kaioken_damage": kaioken_damage,
            "kaioken_warning": kaioken_warning,
            "kaioken_multiplier": get_kaioken_multiplier(character),
            "event": event or {},
            "mods": mods,
        },
    )


def get_form_ui_payload():
    return {
        "forms": FORMS,
        "counts": {
            "total": len(FORMS),
        },
    }


def validate_form_registry():
    required = {"id", "name", "description", "tier", "visuals", "modifiers", "resource_drain", "prerequisites"}
    errors = []
    for key, form in FORMS.items():
        missing = required - set(form.keys())
        if missing:
            errors.append(f"{key}: missing {', '.join(sorted(missing))}")
    return errors


# =============================================================================
# ULTRA INSTINCT DEATH TRIGGER SYSTEM (Category 5)
# =============================================================================

import random


def check_ultra_instinct_trigger(character):
    """
    Check if Ultra Instinct should trigger when HP drops below 10%.
    20% chance to trigger, auto-transforms to highest available form.
    Returns (triggered: bool, message: str)
    """
    # Check if already in UI
    if getattr(character.db, 'ultra_instinct_active', False):
        return False, None
        
    # Get HP percentage
    hp_current = character.db.hp_current or 0
    hp_max = character.db.hp_max or 1
    hp_percent = (hp_current / hp_max) * 100
    
    # Only trigger if below 10%
    if hp_percent >= 10:
        return False, None
    
    # 20% chance to trigger
    if random.random() > 0.20:
        return False, None
    
    # Find highest available transformation
    available_forms = getattr(character.db, 'unlocked_forms', [])
    if not available_forms:
        return False, None
    
    # Get form tiers
    form_tiers = {}
    for form_id, form_data in FORMS.items():
        if form_id in available_forms:
            form_tiers[form_id] = form_data.get('tier', 0)
    
    if not form_tiers:
        return False, None
    
    # Find highest tier form
    highest_form = max(form_tiers.items(), key=lambda x: x[1])[0]
    form_info = FORMS.get(highest_form, {})
    
    # Trigger Ultra Instinct
    character.db.ultra_instinct_active = True
    character.db.ultra_instinct_form = highest_form
    character.db.ultra_instinct_start = __import__('time').time()
    character.db.ultra_instinct_invulnerable = True
    
    # Store previous form to restore later
    character.db.ultra_instinct_previous_form = character.db.active_form
    
    # Apply the transformation
    character.db.active_form = highest_form
    
    # Create dramatic message
    form_name = form_info.get('name', highest_form)
    message = f"|cYour body moves on instinct! You instantly transform into {form_name}!|n\n"
    message += f"|yYour attacks are now impossible to predict! You have 1-2 seconds of invulnerability!|n"
    
    return True, message


def apply_ultra_instinct_boost(character):
    """
    Apply 30-second boosted stats duration after Ultra Instinct triggers.
    """
    import time
    
    if not getattr(character.db, 'ultra_instinct_active', False):
        return
    
    start_time = character.db.ultra_instinct_start
    elapsed = time.time() - start_time
    
    # 30 second duration
    if elapsed < 30:
        # Apply boosted stats (1.5x damage, 1.5x speed)
        character.db.ultra_instinct_damage_boost = 1.5
        character.db.ultra_instinct_speed_boost = 1.5
    else:
        # Duration ended, reset
        end_ultra_instinct(character)


def end_ultra_instinct(character):
    """
    End Ultra Instinct effect - reset HP to 50%.
    """
    hp_max = character.db.hp_max or 1
    
    # Reset HP to 50%
    character.db.hp_current = int(hp_max * 0.5)
    
    # Clear UI flags
    character.db.ultra_instinct_active = False
    character.db.ultra_instinct_invulnerable = False
    character.db.ultra_instinct_damage_boost = 1.0
    character.db.ultra_instinct_speed_boost = 1.0
    
    # Restore previous form if any
    previous_form = getattr(character.db, 'ultra_instinct_previous_form', None)
    if previous_form and previous_form != 'ultra_instinct':
        character.db.active_form = previous_form
    else:
        character.db.active_form = None
    
    character.msg("|cUltra Instinct fades... Your body returns to normal, but you feel refreshed! HP restored to 50%.|n")


def get_ultra_instinct_status(character):
    """
    Get Ultra Instinct status for UI display.
    """
    if not getattr(character.db, 'ultra_instinct_active', False):
        return None
    
    import time
    start_time = character.db.ultra_instinct_start
    elapsed = time.time() - start_time
    remaining = max(0, 30 - elapsed)
    
    return {
        'active': True,
        'form': character.db.ultra_instinct_form,
        'remaining': remaining,
        'invulnerable': character.db.ultra_instinct_invulnerable,
        'damage_boost': character.db.ultra_instinct_damage_boost or 1.0,
        'speed_boost': character.db.ultra_instinct_speed_boost or 1.0,
    }
