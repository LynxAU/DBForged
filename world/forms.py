"""
Data-driven transformation framework and registry.
"""

from __future__ import annotations

from world.content_core import build_registry, find_by_key_or_name, make_stub_result


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
        desc="Explosive short-burst amplification with growing strain and ki bleed. Hold to charge - higher multipliers increase power but also strain and drain.",
        pl=1.14,
        speed=1.06,
        damage=1.08,
        drain_tick=4,
        drain_tech=3,
        prereq={"trainer": "king_kai", "quest": "snake_way_endurance", "ki_control_min": 16},
        visuals={"aura": "aura_kaioken_red", "shader": "heat_distortion", "hair_override": None},
        gameplay={"hp_strain_hook": True, "anti_stall_bias": 0.08, "hold_to_charge": True, "charge_levels": {"x1": 1.14, "x3": 1.28, "x10": 1.45, "x20": 1.60}, "max_charge_level": "x20"},
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
        prereq={"trainer": "supreme_kai", "quest": "elder_kai_ritual", "mastery_min": 18},
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
        prereq={"race_any": ["saiyan", "half_breed"], "quest": "ssj_breakpoint", "mastery_min": 12},
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
        prereq={"race_any": ["saiyan", "half_breed"], "requires_form": "super_saiyan", "form_mastery_min": 15},
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
        prereq={"race_any": ["saiyan", "half_breed"], "requires_form": "super_saiyan", "form_mastery_min": 20},
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
        prereq={"race_any": ["saiyan", "half_breed"], "requires_form": "super_saiyan", "form_mastery_min": 35, "quest": "storm_ascension"},
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
        prereq={"race_any": ["saiyan", "half_breed"], "requires_form": "super_saiyan_2", "form_mastery_min": 45, "ki_control_min": 24},
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
        prereq={"race_any": ["saiyan", "half_breed"], "quest": "god_ki_ritual", "ki_control_min": 30},
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
        prereq={"race_any": ["saiyan", "half_breed"], "requires_form": "super_saiyan_god", "ki_control_min": 36, "quest": "whis_control_trials"},
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
        prereq={"race": "half_breed", "quest": "hybrid_limit_break", "mastery_min": 28},
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
    _form(
        "great_ape",
        "Great Ape",
        "saiyan",
        1,
        desc="Saiyan tail transformation under Blutz Wave. Massive power but requires moon/blutz source.",
        pl=1.35,
        speed=0.85,
        damage=1.25,
        ki_efficiency=1.2,
        drain_tick=0,
        drain_tech=0,
        prereq={"race_any": ["saiyan", "half_breed"], "has_tail": True, "quest": "tail_training"},
        visuals={"aura": "aura_great_ape", "shader": "ape_fury", "hair_override": "ape_fur"},
        gameplay={"requires_moon_or_blutz": True, "berserker_bias": 0.15, "control_penalty": 0.2},
        aliases=["ape", "greatape", "ozaru"],
    ),
    _form(
        "golden_great_ape",
        "Golden Great Ape",
        "saiyan",
        5,
        desc="Great Ape powered by Super Saiyan. Devastating but nearly uncontrollable.",
        pl=1.55,
        speed=0.90,
        damage=1.35,
        ki_efficiency=1.1,
        drain_tick=6,
        drain_tech=4,
        prereq={"requires_form": "great_ape", "requires_form_2": "super_saiyan", "quest": "golden_ape_mastery"},
        visuals={"aura": "aura_golden_ape", "shader": "golden_beast", "hair_override": "gold_ape"},
        gameplay={"requires_moon_or_blutz": True, "berserker_bias": 0.25, "control_penalty": 0.3, "aoe_pressure": True},
        aliases=["golden_ape", "gape"],
    ),
    # Namekian
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
        prereq={"race": "namekian", "quest": "namekian_gianting", "mastery_min": 14},
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
        prereq={"race": "human", "trainer": "master_roshi"},
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
        prereq={"race": "majin", "quest": "majin_body_discipline"},
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
        prereq={"race": "majin", "requires_form": "super_majin", "quest": "kid_chaos_trial"},
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
        prereq={"race": "android", "quest": "capsule_lab_calibration"},
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
        prereq={"race": "android", "requires_form": "android_overclock", "quest": "reactor_limiters_removed"},
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
        prereq={"race_any": ["biodroid", "bio_android"], "quest": "evolution_catalyst_alpha"},
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
        prereq={"race_any": ["biodroid", "bio_android"], "requires_form": "biodroid_stage_two", "quest": "evolution_catalyst_omega"},
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
        prereq={"race_any": ["biodroid", "bio_android"], "requires_form": "biodroid_perfect", "quest": "zenkai_evolution_event"},
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
        prereq={"race": "frost_demon", "quest": "imperial_unsealing"},
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
        prereq={"race": "frost_demon", "requires_form": "frost_demon_true_form", "quest": "final_form_control"},
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
        prereq={"race": "frost_demon", "requires_form": "frost_demon_final_form", "quest": "golden_refinement"},
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
        prereq={"race": "grey", "trainer": "jiren_echo"},
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
        prereq={"race": "grey", "requires_form": "meditative_limit", "quest": "tournament_resolve"},
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
        prereq={"race": "kai", "quest": "sacred_world_attunement"},
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
        prereq={"race": "kai", "requires_form": "kai_unsealed", "quest": "kai_guardian_vow"},
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
        prereq={"race": "truffle", "quest": "tuffle_mech_sync"},
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
        prereq={"race": "truffle", "requires_form": "truffle_machine_merge", "quest": "parasite_protocols"},
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
    if req.get("ki_control_min") and (character.db.ki_control or 0) < req["ki_control_min"]:
        return False, f"Need Ki Control {req['ki_control_min']}."
    if req.get("mastery_min") and (character.db.mastery or 0) < req["mastery_min"]:
        return False, f"Need Mastery {req['mastery_min']}."
    if req.get("requires_form"):
        known_forms = set(character.db.unlocked_forms or [])
        if req["requires_form"] not in known_forms and character.db.active_form != req["requires_form"]:
            return False, f"Requires {req['requires_form']} unlocked."
    if req.get("form_mastery_min"):
        needed_form = req.get("requires_form") or form_key
        mastery = (character.db.form_mastery or {}).get(needed_form, 0)
        if mastery < req["form_mastery_min"]:
            return False, f"Requires {needed_form} mastery {req['form_mastery_min']}."
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
    mastery = dict(character.db.form_mastery or {})
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
    return True, f"You transform into {form['name']}!", stub


def deactivate_form(character, reason="manual"):
    active = getattr(character.db, "active_form", None)
    if not active:
        return False, "You are already in base form.", None
    form = FORMS.get(active, {})
    if form.get("special_system") == "lssj":
        from world.lssj import deactivate_lssj

        deactivate_lssj(character, crashed=(reason == "crash"))
    character.db.active_form = None
    return True, "You revert to base form.", make_stub_result(
        "form_deactivate",
        active,
        caller=character,
        payload={"reason": reason},
    )


def apply_form_drain_tick(character, event=None):
    """
    Safe heartbeat stub for future combat/service loop integration.
    """
    active = getattr(character.db, "active_form", None)
    if not active:
        return make_stub_result("form_tick", "base", caller=character, payload={"active": False})
    form = FORMS.get(active, {})
    drain, debug = get_form_tick_drain(character, active)
    mods = debug.get("mods", get_form_modifiers(character, active))
    mastery = debug.get("mastery", (character.db.form_mastery or {}).get(active, 0))
    if drain:
        character.db.ki_current = max(0, (character.db.ki_current or 0) - drain)
    if (character.db.ki_current or 0) <= 0 and active:
        deactivate_form(character, reason="exhausted")
    return make_stub_result(
        "form_tick",
        active,
        caller=character,
        payload={"drain": drain, "mastery": mastery, "event": event or {}, "mods": mods},
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
