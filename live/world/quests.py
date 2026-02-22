"""
Minimal questline scaffolding for trainer/content unlocks.
"""

from __future__ import annotations

from world.content_core import make_stub_result
from world.npc_content import NPC_DEFINITIONS


def _quest(key, title, giver, summary, rewards, *, unlock_level=1, objectives=None, location=None):
    return (
        key,
        {
            "id": key,
            "title": title,
            "giver": giver,
            "summary": summary,
            "unlock_level": unlock_level,
            "location": location or NPC_DEFINITIONS.get(giver, {}).get("location_hint"),
            "objectives": objectives
            or [
                {"type": "spar", "target": "training_dummy_or_sim", "count": 1},
                {"type": "report_back", "npc": giver},
            ],
            "rewards": rewards,
            "state_model": {
                "accepted": False,
                "completed": False,
                "turn_in_ready": False,
            },
            "framework": "QuestScaffold",
            "ready_state": "integration_ready",
        },
    )


QUESTLINES = dict(
    [
        _quest("turtle_school_fundamentals", "Turtle School Fundamentals", "master_roshi", "Complete stance, breath, and timing drills to earn Turtle School trust.", {"techniques": ["kame_wave", "solar_flare"]}),
        _quest("kami_sealing_trials", "Kami's Sealing Trials", "master_roshi", "Gather ritual tools and practice containment timing to unlock sealing techniques.", {"techniques": ["evil_containment_wave"]}),
        _quest("ssj_breakpoint", "Saiyan Breakpoint", "goku", "Push through controlled sparring rage triggers without losing form.", {"forms": ["super_saiyan"], "techniques": ["kame_wave"]}),
        _quest("storm_ascension", "Storm Ascension", "vegeta", "Train lightning-fast pressure transitions to stabilize SSJ2-level output.", {"forms": ["super_saiyan_2"]}),
        _quest("dragon_fist_trial", "Dragon Fist Trial", "goku", "Land a committed finisher after reading a simulated giant-class target.", {"techniques": ["dragon_fist"]}),
        _quest("instant_shift_attunement", "Instant Shift Attunement", "goku", "Learn to lock onto ki signatures before teleport pursuit.", {"techniques": ["instant_transmission"]}),
        _quest("gravity_chamber_proving", "Gravity Chamber Proving", "vegeta", "Clear escalating gravity drills while maintaining technique output.", {"techniques": ["galick_gun", "big_bang_attack"], "forms": ["super_saiyan_grade2"]}),
        _quest("whis_control_trials", "Whis Control Trials", "whis", "Refine god-ki output and emotional control under angelic supervision.", {"forms": ["super_saiyan_blue"]}),
        _quest("god_ki_ritual", "God Ki Ritual", "whis", "Undergo ritual attunement and maintain stable divine ki flow.", {"forms": ["super_saiyan_god"]}),
        _quest("precision_drill_spiral", "Precision Drill Spiral", "piccolo", "Charge and land piercing beams against moving plates.", {"techniques": ["special_beam_cannon"]}),
        _quest("lookout_focus_trials", "Lookout Focus Trials", "piccolo", "Complete silence training and high-control beam routing.", {"techniques": ["masenko", "makosen"], "forms": ["dragon_clan_focus"]}),
        _quest("namekian_gianting", "Namekian Gianting", "piccolo", "Practice controlled giantification without losing balance.", {"forms": ["giant_namekian"]}),
        _quest("disc_control_drills", "Disc Control Drills", "krillin", "Master delayed lines and return angles on cutting discs.", {"techniques": ["destructo_disc", "kienzan_barrage"]}),
        _quest("survivor_instinct_course", "Survivor Instinct Course", "krillin", "Complete pressure escapes and blind-angle counters.", {"techniques": ["scatter_shot", "afterimage_dash"]}),
        _quest("crane_discipline_course", "Crane Discipline Course", "tien", "Crane School precision and composure drills.", {"techniques": ["dodon_ray", "feint_step"]}),
        _quest("tri_beam_endurance", "Tri-Beam Endurance", "tien", "Survive recoil discipline and controlled commitment training.", {"techniques": ["tri_beam"]}),
        _quest("snake_way_endurance", "Snake Way Endurance", "king_kai", "Cross impossible endurance milestones and preserve ki control.", {"forms": ["kaioken"], "techniques": ["kaioken"]}),
        _quest("kaioken_stability_trials", "Kaioken Stability Trials", "king_kai", "Hold Kaioken under movement and combo pressure.", {"forms": ["kaioken"]}),
        _quest("elder_kai_ritual", "Elder Kai Ritual", "supreme_kai", "A ritual awakening of latent power requiring patience and focus.", {"forms": ["potential_unleashed"], "techniques": ["potential_unleashed_focus"]}),
        _quest("sacred_world_attunement", "Sacred World Attunement", "supreme_kai", "Attune to divine fields and sacred ki signatures.", {"forms": ["kai_unsealed"], "techniques": ["telekinesis_hold"]}),
        _quest("kai_guardian_vow", "Kai Guardian's Vow", "supreme_kai", "Bind your ki to a guardian role and refine divine discipline.", {"forms": ["godly_empowerment"]}),
        _quest("imperial_unsealing", "frieza", "Imperial Unsealing", "Unlock and maintain Frost Demon combat body states under ruthless standards.", {"forms": ["frost_demon_true_form"], "techniques": ["death_beam"]}),
        _quest("final_form_control", "frieza", "Final Form Control", "Sustain the final streamlined body without leaking power.", {"forms": ["frost_demon_final_form"]}),
        _quest("golden_refinement", "frieza", "Golden Refinement", "Refine golden power to reduce instability and improve precision.", {"forms": ["golden_frost"], "techniques": ["supernova", "death_ball"]}),
        _quest("emperor_precision_drills", "frieza", "Emperor Precision Drills", "Precision kill-shot and pressure routing exercises.", {"techniques": ["crusher_ball"]}),
        _quest("evolution_catalyst_alpha", "cell_shade", "Evolution Catalyst Alpha", "Simulated adaptation trials for biodroid stage evolution.", {"forms": ["biodroid_stage_two"], "techniques": ["spirit_breaking_fist"]}),
        _quest("evolution_catalyst_omega", "cell_shade", "Evolution Catalyst Omega", "Perfect-form stabilization under hostile combat conditions.", {"forms": ["biodroid_perfect"]}),
        _quest("zenkai_evolution_event", "cell_shade", "Zenkai Evolution Event", "Survive a critical simulation comeback to trigger a superior state.", {"forms": ["super_perfect_biodroid"], "techniques": ["omega_blaster"]}),
        _quest("broly_lineage_echoes", "broly", "Broly Lineage Echoes", "Confront Legendary lineage resonance without complete loss of control.", {"flags": ["legendary_seed"], "techniques": ["legendary_surge"]}),
        _quest("legendary_control_protocol", "broly", "Legendary Control Protocol", "Stage-based LSSJ control drills with forced de-escalation practice.", {"lssj": {"unlock": True, "mastery_rank": 1}}),
        _quest("legendary_rage_forge", "broly", "Legendary Rage Forge", "Train escalation and containment under heavy combat stress.", {"lssj": {"mastery_rank": 2}}),
        _quest("capsule_lab_calibration", "cell_shade", "Capsule Lab Calibration", "Calibrate cybernetic throughput and overclock safety limits.", {"forms": ["android_overclock"], "techniques": ["android_overclock"]}),
        _quest("reactor_limiters_removed", "cell_shade", "Reactor Limiters Removed", "Sustain reactor output safely under repeated attack patterns.", {"forms": ["infinite_drive"]}),
        _quest("tuffle_mech_sync", "baby", "Tuffle Mech Sync", "Link with Tuffle machine support arrays and maintain signal integrity.", {"forms": ["truffle_machine_merge"], "techniques": ["truffle_probe_swarm"]}),
        _quest("parasite_protocols", "baby", "Parasite Protocols", "Learn suppressive battlefield control through parasite-network tactics.", {"forms": ["truffle_parasite_overdrive"], "techniques": ["gravity_bind"]}),
        _quest("tactical_probe_network", "baby", "Tactical Probe Network", "Deploy and route a probe web across multiple targets.", {"techniques": ["truffle_probe_swarm"]}),
        _quest("tournament_resolve", "jiren_echo", "Tournament Resolve", "Hold form under relentless pressure and break your limits deliberately.", {"forms": ["grey_limit_break"]}),
        _quest("grey_dominance_trials", "jiren_echo", "Grey Dominance Trials", "Pressure-focused control sparring against evasive opponents.", {"forms": ["meditative_limit"], "techniques": ["psychic_burst"]}),
        _quest("majin_body_discipline", "cell_shade", "Majin Body Discipline (Sim)", "Simulation drills for elastic-body timing and sustain control.", {"forms": ["super_majin"], "techniques": ["vanishing_ball"]}),
        _quest("kid_chaos_trial", "cell_shade", "Kid Chaos Trial (Sim)", "Survive chaotic movement and convert it into pressure windows.", {"forms": ["pure_majin"]}),
        _quest("hybrid_limit_break", "goku", "Hybrid Limit Break", "Unlock explosive hybrid potential through controlled emotional pressure.", {"forms": ["beast"]}),
    ]
)


def get_quest_definition(key):
    return QUESTLINES.get(key)


def get_quests_for_npc(npc_key):
    return [quest for quest in QUESTLINES.values() if quest["giver"] == npc_key]


def get_player_quest_state(character):
    return dict(character.db.quest_state or {})


def ensure_player_quest_state(character):
    state = dict(character.db.quest_state or {})
    character.db.quest_state = state
    return state


def offer_quests_stub(npc, caller):
    npc_key = getattr(npc.db, "trainer_key", None) or getattr(npc.db, "npc_content_key", None)
    quests = get_quests_for_npc(npc_key) if npc_key else []
    return make_stub_result(
        "quest_offer",
        npc_key or "unknown_npc",
        caller=caller,
        target=npc,
        payload={"quests": quests},
    )
