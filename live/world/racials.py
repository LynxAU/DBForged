"""
Racial traits/passives/actives registry.

11 playable races x 3 top racial choices each, balanced as playstyle bias.
"""

from __future__ import annotations

from world.content_core import build_registry, find_by_key_or_name, make_stub_result, summarize_effect


PLAYABLE_RACES = [
    "human",
    "saiyan",
    "half_breed",
    "namekian",
    "majin",
    "android",
    "biodroid",
    "frost_demon",
    "grey",
    "kai",
    "truffle",
]


def _trait(
    key,
    race,
    name,
    kind,
    desc,
    *,
    tags,
    effect,
    ki_cost=0,
    cooldown=0.0,
    prerequisites=None,
):
    return (
        key,
        {
            "id": key,
            "name": name,
            "display_name": name,
            "description": desc,
            "framework": "RacialTrait",
            "race": race,
            "kind": kind,  # passive / active / trait
            "category": "racial",
            "tags": ["racial", kind] + list(tags),
            "resource_costs": {"ki": int(ki_cost)},
            "ki_cost": int(ki_cost),
            "cooldown": float(cooldown),
            "effect": effect,
            "scaling": effect.get("scaling", {}),
            "target_rules": {"target": "self" if kind != "active" or effect.get("target") == "self" else effect.get("target", "enemy"), "range": effect.get("range", "self")},
            "prerequisites": prerequisites or {"race": race},
            "context_extras": effect.get("hooks", {}),
            "ui_summary": summarize_effect({"effect": effect, "scaling": effect.get("scaling", {}), "tags": ["racial", kind] + list(tags)}),
            "ready_state": "integration_ready",
        },
    )


RACIALS = build_registry(
    [
        # Human
        _trait("human_adaptable_training", "human", "Adaptable Training", "passive", "Humans gain broader value from varied drills and recover technique cooldown rhythm faster.", tags=["mastery", "economy"], effect={"type": "passive", "summary": "+mastery gain from varied actions", "hooks": {"mastery_gain_bias": 0.08, "cooldown_recovery_bias": 0.05}}),
        _trait("human_grit_second_wind", "human", "Second Wind", "passive", "Human grit improves ki stability while wounded, encouraging comeback play.", tags=["survivability", "ki"], effect={"type": "passive", "summary": "Wounded-state ki efficiency bonus", "hooks": {"low_hp_ki_efficiency_bonus": 0.12}}),
        _trait("human_tech_burst", "human", "Technique Burst", "active", "Humans can spike execution tempo for a brief window to rotate utility and pressure tools.", tags=["utility", "combo"], effect={"type": "buff", "summary": "Short cooldown/tempo boost", "duration": 4.0, "hooks": {"cooldown_haste": 0.12, "speed_bias": 0.05}}, ki_cost=14, cooldown=16.0),
        # Saiyan
        _trait("saiyan_battle_instinct", "saiyan", "Battle Instinct", "passive", "Saiyans build momentum in extended fights, favoring aggressive tempo and adaptation.", tags=["combat", "momentum"], effect={"type": "passive", "summary": "Combat time increases pressure", "hooks": {"combat_momentum_gain": 0.1}}),
        _trait("saiyan_zenkai_edge", "saiyan", "Zenkai Edge", "passive", "Hard-fought recoveries can grant small temporary growth spikes without permanent runaway scaling.", tags=["survivability", "growth"], effect={"type": "passive", "summary": "Post-defeat/recovery growth hook", "hooks": {"zenkai_temp_bonus": 0.08}}),
        _trait("saiyan_tail_counter", "saiyan", "Tail Counter", "active", "Tailed Saiyans can whip space for a quick anti-rush punish if uninjured.", tags=["melee", "counter"], effect={"type": "counter_stance", "summary": "Short anti-rush counter window", "duration": 2.5, "hooks": {"anti_rush_counter": True}}, ki_cost=10, cooldown=12.0),
        # Half-Breed
        _trait("half_breed_latent_spike", "half_breed", "Latent Spike", "passive", "Hybrid potential converts emotional spikes into short precision and output bursts.", tags=["burst", "mastery"], effect={"type": "passive", "summary": "Rage-trigger burst without full instability", "hooks": {"rage_precision_bonus": 0.08, "rage_damage_bonus": 0.06}}),
        _trait("half_breed_focus_rebound", "half_breed", "Focus Rebound", "passive", "Hybrids recover composure faster after stuns or breaks, supporting adaptive play.", tags=["control", "defense"], effect={"type": "passive", "summary": "Status recovery bias", "hooks": {"stun_duration_reduction": 0.12}}),
        _trait("half_breed_guardian_drive", "half_breed", "Guardian Drive", "active", "Protective resolve boosts defense and counter-pressure when allies are threatened.", tags=["defense", "support"], effect={"type": "buff", "summary": "Guard/counter boost when protecting", "duration": 5.0, "hooks": {"guard_bonus": 0.12, "counter_bonus": 0.08}}, ki_cost=16, cooldown=18.0),
        # Namekian
        _trait("namekian_regenerative_tissue", "namekian", "Regenerative Tissue", "passive", "Namekian regeneration improves recovery windows and attrition resilience.", tags=["survivability", "recovery"], effect={"type": "passive", "summary": "Passive recovery / regen synergy", "hooks": {"regen_bonus": 0.12}}),
        _trait("namekian_stretching_reach", "namekian", "Stretching Reach", "passive", "Elastic limbs improve melee spacing and punish windows without raw damage inflation.", tags=["melee", "control"], effect={"type": "passive", "summary": "Extended melee reach", "hooks": {"melee_reach_bonus": 1}}),
        _trait("namekian_healing_pulse", "namekian", "Healing Pulse", "active", "Channel supportive ki to stabilize self or ally in short bursts.", tags=["support", "ki"], effect={"type": "heal", "summary": "Single-target heal pulse", "target": "ally", "range": "short", "base_heal": 20}, ki_cost=22, cooldown=20.0),
        # Majin
        _trait("majin_malleable_body", "majin", "Malleable Body", "passive", "Majin anatomy softens impact damage and reduces knockback severity.", tags=["defense", "survivability"], effect={"type": "passive", "summary": "Impact mitigation / knockback resist", "hooks": {"impact_reduction": 0.08, "knockback_resist": 0.15}}),
        _trait("majin_candy_metabolism", "majin", "Candy Metabolism", "passive", "Majins recover faster from downtime, favoring reset-heavy play.", tags=["recovery", "economy"], effect={"type": "passive", "summary": "Out-of-combat recovery bonus", "hooks": {"rest_recovery_bonus": 0.18}}),
        _trait("majin_body_split_feint", "majin", "Body Split Feint", "active", "A weird Majin body fake-out that creates misdirection and escape angle frames.", tags=["utility", "movement"], effect={"type": "movement", "summary": "Feint / evasion burst", "duration": 2.0, "hooks": {"evasion_bonus": 0.14}}, ki_cost=14, cooldown=14.0),
        # Android
        _trait("android_reactor_efficiency", "android", "Reactor Efficiency", "passive", "Androids sustain technique usage with superior energy routing instead of bigger numbers.", tags=["economy", "ki"], effect={"type": "passive", "summary": "Technique ki cost efficiency", "hooks": {"ki_cost_reduction": 0.1}}),
        _trait("android_targeting_suite", "android", "Targeting Suite", "passive", "Combat processors improve scan accuracy and ranged consistency.", tags=["control", "ranged"], effect={"type": "passive", "summary": "Scan/ranged precision bonus", "hooks": {"scan_error_reduction": 0.1, "ranged_hit_bias": 0.06}}),
        _trait("android_barrier_projector", "android", "Barrier Projector", "active", "Deploy a compact energy barrier field for brief burst defense.", tags=["defense", "utility"], effect={"type": "guard", "summary": "Short barrier field", "duration": 2.5, "reduction": 0.55}, ki_cost=0, cooldown=16.0),
        # Biodroid
        _trait("biodroid_adaptive_genome", "biodroid", "Adaptive Genome", "passive", "Biodroids slowly adapt to repeated damage patterns, rewarding long engagements.", tags=["defense", "adaptation"], effect={"type": "passive", "summary": "Repeated-hit adaptation", "hooks": {"adaptive_resistance_gain": 0.05}}),
        _trait("biodroid_predator_sense", "biodroid", "Predator Sense", "passive", "Predatory instincts improve pursuit and punish windows against weakened foes.", tags=["offense", "tracking"], effect={"type": "passive", "summary": "Bonus pressure vs wounded targets", "hooks": {"execute_window_bonus": 0.1}}),
        _trait("biodroid_genetic_siphon", "biodroid", "Genetic Siphon", "active", "Brief contact siphon that steals a little ki and fuels biodroid sustain.", tags=["melee", "resource"], effect={"type": "resource_drain", "summary": "Melee ki siphon", "target": "enemy", "range": "melee", "hooks": {"ki_siphon": 12}}, ki_cost=8, cooldown=18.0),
        # Frost Demon
        _trait("frost_demon_form_discipline", "frost_demon", "Form Discipline", "passive", "Frost Demons maintain transformed efficiency better through rigid control training.", tags=["transformation", "economy"], effect={"type": "passive", "summary": "Form drain reduction", "hooks": {"form_drain_reduction": 0.08}}),
        _trait("frost_demon_cruel_precision", "frost_demon", "Cruel Precision", "passive", "Precision-focused cruelty improves piercing attacks and finisher setup.", tags=["ranged", "piercing"], effect={"type": "passive", "summary": "Piercing technique bonus", "hooks": {"pierce_damage_bias": 0.08, "interrupt_bias": 0.05}}),
        _trait("frost_demon_death_glare", "frost_demon", "Death Glare", "active", "A murderous pressure glare that briefly shakes guard and concentration.", tags=["control", "debuff"], effect={"type": "debuff", "summary": "Short guard/focus debuff", "target": "enemy", "range": "mid", "duration": 3.0, "hooks": {"guard_penalty": 0.1}}, ki_cost=16, cooldown=15.0),
        # Grey
        _trait("grey_relentless_focus", "grey", "Relentless Focus", "passive", "Grey warriors resist crowd control and keep pressure through interruptions.", tags=["control", "defense"], effect={"type": "passive", "summary": "CC resistance bias", "hooks": {"control_resist": 0.12}}),
        _trait("grey_pressure_steps", "grey", "Pressure Steps", "passive", "Subtle footwork improves close-range positioning and anti-kiting pressure.", tags=["movement", "melee"], effect={"type": "passive", "summary": "Close-range footwork bonus", "hooks": {"anti_kite_bias": 0.1}}),
        _trait("grey_dominance_aura", "grey", "Dominance Aura", "active", "Project crushing intent to shrink enemy courage and disrupt charge attempts.", tags=["control", "area"], effect={"type": "aoe_debuff", "summary": "Nearby pressure debuff / anti-charge", "target": "area", "range": "short", "duration": 3.5, "hooks": {"charge_disrupt": True, "speed_penalty": 0.08}}, ki_cost=18, cooldown=20.0),
        # Kai
        _trait("kai_divine_attunement", "kai", "Divine Attunement", "passive", "Kai lineage grants superior ki control and support-style technique efficiency.", tags=["ki", "support"], effect={"type": "passive", "summary": "Ki control scaling bias", "hooks": {"ki_control_scaling_bonus": 0.1}}),
        _trait("kai_sacred_sense", "kai", "Sacred Sense", "passive", "Kais sense signatures with greater clarity across suppression and distance.", tags=["sense", "utility"], effect={"type": "passive", "summary": "Sense/scout clarity bonus", "hooks": {"sense_precision_bonus": 0.16}}),
        _trait("kai_blessing_seal", "kai", "Blessing Seal", "active", "A divine binding sigil that weakens a target's ability to sustain transformations.", tags=["control", "transformation"], effect={"type": "seal", "summary": "Form drain debuff / weaken", "target": "enemy", "range": "mid", "duration": 4.0, "hooks": {"form_drain_increase": 0.12}}, ki_cost=24, cooldown=22.0),
        # Truffle / Tuffle
        _trait("truffle_tactical_analytics", "truffle", "Tactical Analytics", "passive", "Tuffle analytics improve read quality, scan precision and loadout planning.", tags=["utility", "analysis"], effect={"type": "passive", "summary": "Scan/UI intel bonus", "hooks": {"scan_error_reduction": 0.14, "target_pattern_bonus": 0.08}}),
        _trait("truffle_gadget_integration", "truffle", "Gadget Integration", "passive", "Integrated tech supports utility actions and control-oriented techniques.", tags=["utility", "control"], effect={"type": "passive", "summary": "Utility/control efficiency", "hooks": {"utility_ki_cost_reduction": 0.1}}),
        _trait("truffle_probe_swarm", "truffle", "Probe Swarm", "active", "Launch support probes to harass, reveal, and disrupt evasive targets.", tags=["control", "ranged"], effect={"type": "debuff", "summary": "Tracking/reveal swarm", "target": "enemy", "range": "long", "duration": 4.0, "hooks": {"reveal": True, "anti_afterimage": 0.18}}, ki_cost=12, cooldown=17.0),
    ]
)


def _normalize_race(race):
    race = (race or "").lower().replace(" ", "_")
    if race in {"bio_android", "biodroid"}:
        return "biodroid"
    if race in {"tuffle", "truffle"}:
        return "truffle"
    if race == "halfbreed":
        return "half_breed"
    return race


def get_racial(key_or_name):
    return find_by_key_or_name(RACIALS, key_or_name)


def get_racials_for_race(race):
    race = _normalize_race(race)
    return [(k, v) for k, v in RACIALS.items() if _normalize_race(v.get("race")) == race]


def ensure_character_racials(character):
    race = _normalize_race(character.db.race)
    traits = [k for k, _ in get_racials_for_race(race)]
    character.db.racial_traits = sorted(traits)
    return traits


def execute_racial_stub(caller, racial_key, target=None, context=None):
    if racial_key not in RACIALS:
        raise KeyError(f"Unknown racial: {racial_key}")
    return make_stub_result(
        "racial",
        racial_key,
        caller=caller,
        target=target,
        payload={"effect": RACIALS[racial_key]["effect"], "context": context or {}},
    )


def validate_racial_registry():
    errors = []
    for race in PLAYABLE_RACES:
        count = len(get_racials_for_race(race))
        if count != 3:
            errors.append(f"{race}: expected 3 racials, found {count}")
    return errors
