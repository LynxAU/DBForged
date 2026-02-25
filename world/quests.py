"""
Minimal questline scaffolding for trainer/content unlocks.
"""

from __future__ import annotations

import time

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
        _quest("snake_way_endurance", "Snake Way Endurance", "king_kai", "Cross impossible endurance milestones and preserve ki control.", {"forms": ["kaioken"]}),
        _quest("kaioken_stability_trials", "Kaioken Stability Trials", "king_kai", "Hold Kaioken under movement and combo pressure.", {"forms": ["kaioken"]}),
        _quest("elder_kai_ritual", "Elder Kai Ritual", "supreme_kai", "A ritual awakening of latent power requiring patience and focus.", {"forms": ["potential_unleashed"]}),
        _quest("sacred_world_attunement", "Sacred World Attunement", "supreme_kai", "Attune to divine fields and sacred ki signatures.", {"forms": ["kai_unsealed"], "techniques": ["telekinesis_hold"]}),
        _quest("kai_guardian_vow", "Kai Guardian's Vow", "supreme_kai", "Bind your ki to a guardian role and refine divine discipline.", {"forms": ["godly_empowerment"]}),
        _quest("imperial_unsealing", "frieza", "Imperial Unsealing", "Unlock and maintain Frost Demon combat body states under ruthless standards.", {"forms": ["frost_demon_true_form"], "techniques": ["death_beam"]}),
        _quest("final_form_control", "frieza", "Final Form Control", "Sustain the final streamlined body without leaking power.", {"forms": ["frost_demon_final_form"]}),
        _quest("golden_refinement", "frieza", "Golden Refinement", "Refine golden power to reduce instability and improve precision.", {"forms": ["golden_frost"], "techniques": ["supernova", "death_ball"]}),
        _quest("emperor_precision_drills", "frieza", "Emperor Precision Drills", "Precision kill-shot and pressure routing exercises.", {"techniques": ["crusher_ball"]}),
        _quest("evolution_catalyst_alpha", "cell_shade", "Evolution Catalyst Alpha", "Simulated adaptation trials for biodroid stage evolution.", {"forms": ["biodroid_stage_two"], "techniques": ["spirit_breaking_fist"]}),
        _quest("evolution_catalyst_omega", "cell_shade", "Evolution Catalyst Omega", "Perfect-form stabilization under hostile combat conditions.", {"forms": ["biodroid_perfect"]}),
        _quest("zenkai_evolution_event", "cell_shade", "Zenkai Evolution Event", "Survive a critical simulation comeback to trigger a superior state.", {"forms": ["super_perfect_biodroid"], "techniques": ["omega_blaster"]}),
        _quest("broly_lineage_echoes", "broly", "Broly Lineage Echoes", "Confront Legendary lineage resonance without complete loss of control.", {"flags": ["legendary_seed"], "techniques": ["eraser_cannon"]}),
        _quest("legendary_control_protocol", "broly", "Legendary Control Protocol", "Stage-based LSSJ control drills with forced de-escalation practice.", {"lssj": {"unlock": True, "mastery_rank": 1}}),
        _quest("legendary_rage_forge", "broly", "Legendary Rage Forge", "Train escalation and containment under heavy combat stress.", {"lssj": {"mastery_rank": 2}}),
        _quest("capsule_lab_calibration", "cell_shade", "Capsule Lab Calibration", "Calibrate cybernetic throughput and overclock safety limits.", {"forms": ["android_overclock"]}),
        _quest("reactor_limiters_removed", "cell_shade", "Reactor Limiters Removed", "Sustain reactor output safely under repeated attack patterns.", {"forms": ["infinite_drive"]}),
        _quest("tuffle_mech_sync", "baby", "Tuffle Mech Sync", "Link with Tuffle machine support arrays and maintain signal integrity.", {"forms": ["truffle_machine_merge"], "techniques": ["gravity_bind"]}),
        _quest("parasite_protocols", "baby", "Parasite Protocols", "Learn suppressive battlefield control through parasite-network tactics.", {"forms": ["truffle_parasite_overdrive"], "techniques": ["gravity_bind"]}),
        _quest("tactical_probe_network", "baby", "Tactical Probe Network", "Deploy and route a probe web across multiple targets.", {"techniques": ["scatter_shot"]}),
        _quest("tournament_resolve", "jiren_echo", "Tournament Resolve", "Hold form under relentless pressure and break your limits deliberately.", {"forms": ["grey_limit_break"]}),
        _quest("grey_dominance_trials", "jiren_echo", "Grey Dominance Trials", "Pressure-focused control sparring against evasive opponents.", {"forms": ["meditative_limit"], "techniques": ["psychic_burst"]}),
        _quest("majin_body_discipline", "cell_shade", "Majin Body Discipline (Sim)", "Simulation drills for elastic-body timing and sustain control.", {"forms": ["super_majin"], "techniques": ["vanishing_ball"]}),
        _quest("kid_chaos_trial", "cell_shade", "Kid Chaos Trial (Sim)", "Survive chaotic movement and convert it into pressure windows.", {"forms": ["pure_majin"]}),
        _quest("hybrid_limit_break", "Hybrid Limit Break", "goku", "Unlock explosive hybrid potential through controlled emotional pressure.", {"forms": ["beast"]}),
        _quest("tail_training", "Tail Training", "vegeta", "Learn to control your tail and tap into Great Ape power.", {"forms": ["great_ape"], "race_any": ["saiyan", "half_breed"]}),
        _quest("golden_ape_mastery", "Golden Ape Mastery", "vegeta", "Combine Super Saiyan with Great Ape for devastating Golden Great Ape.", {"forms": ["golden_great_ape"]}),
        _quest("senzu_quest", "Senzu Bean Discovery", "baba", "Discover where to find legendary Senzu beans.", {"techniques": ["senzu_bean"]}),
        _quest("spirit_bomb_trial", "Spirit Bomb Mastery", "goku", "Learn the ultimate energy attack that gathers energy from all living things.", {"techniques": ["spirit_bomb"], "forms": ["super_saiyan"]}),
        _quest("shopping_trip", "Shopping Trip", "bulma", "Visit the Capsule Corp shop to buy equipment and items.", {"techniques": ["weighted_clothing", "scouter"]}),
        _quest("galick_gun_mastery", "Galick Gun Precision", "vegeta", "Master the Galick Gun with perfect charge control.", {"techniques": ["galick_gun"]}),
        _quest("special_beam_mastery", "Special Beam Cannon Focus", "piccolo", "Master the difficult Special Beam Cannon technique.", {"techniques": ["special_beam_cannon"]}),
        _quest("desert_wolf_rush", "Desert Wolf Rush", "yamcha", "Chain rush pressure with safe exits and anti-counter spacing.", {"techniques": ["wolf_fang_fist", "mach_punch_barrage"]}),
        _quest("practical_brawler_drills", "Practical Brawler Drills", "yamcha", "Build real-fight rhythm with feints, vanishes, and close pressure resets.", {"techniques": ["vanish_strike", "meteor_smash"]}),
        _quest("future_ruin_pressure", "Future Ruin Pressure", "future_trunks", "Fight through attrition scenarios while preserving beam efficiency.", {"techniques": ["buster_cannon", "burning_attack"]}),
        _quest("burning_hand_signs", "Burning Hand Signs", "future_trunks", "Master rapid-sign execution without sacrificing target acquisition.", {"techniques": ["burning_attack"]}),
        _quest("finish_buster_routing", "Finish Buster Routing", "future_trunks", "Route ki compression into stable finisher beams under movement.", {"techniques": ["finish_buster"]}),
        _quest("hybrid_composure_drills", "Hybrid Composure Drills", "gohan", "Maintain composure through surges and convert pressure into accurate offense.", {"techniques": ["consecutive_energy_blast", "wild_sense"]}),
        _quest("beast_edge_focus", "Beast Edge Focus", "gohan", "Walk the edge of overwhelming power without losing tactical judgment.", {"techniques": ["justice_rush"]}),
        _quest("ranger_barrier_protocols", "Ranger Barrier Protocols", "android_17", "Train barrier timing and repulsion angles under sustained pressure.", {"techniques": ["barrier", "explosive_wave"]}),
        _quest("arena_efficiency_loop", "Arena Efficiency Loop", "android_17", "Clear attrition gauntlets using efficient movement and pressure routing.", {"techniques": ["consecutive_energy_blast"]}),
        _quest("fusion_finisher_discipline", "Fusion Finisher Discipline", "gogeta", "Set up and release fusion-grade beam finishers without overcommitting early.", {"techniques": ["big_bang_kamehameha"]}),
        _quest("pride_trooper_formation", "Pride Trooper Formation", "toppo", "Drill disciplined team-pressure fundamentals and clean close-range punishes.", {"techniques": ["crusher_knee"]}),
        _quest("justice_combo_doctrine", "Justice Combo Doctrine", "toppo", "Train pressure strings that maintain advantage without reckless overextension.", {"techniques": ["justice_rush"]}),
        _quest("capsule_fundamentals_range", "Capsule Fundamentals Range", "vegeta", "Capsule Corp basics for rapid ki release, pressure chains, and guard discipline.", {"techniques": ["ki_blast", "guard", "finger_beam_burst"]}),
        _quest("turtle_advanced_beam_doctrine", "Turtle Advanced Beam Doctrine", "master_roshi", "Refine deeper Turtle School beam routing and scaling under load.", {"techniques": ["super_kamehameha"]}),
        _quest("lookout_shielding_practice", "Lookout Shielding Practice", "piccolo", "Practice defensive timings and controlled recovery windows.", {"techniques": ["regeneration_focus"]}),
        _quest("saiyan_heavy_finishers", "Saiyan Heavy Finishers", "vegeta", "Develop heavy strike and finisher discipline for pride-style combat pressure.", {"techniques": ["final_flash", "tail_sweep"], "forms": ["super_saiyan_grade3"]}),
        _quest("max_power_body_control", "Max Power Body Control", "master_roshi", "Control an overdriven physique without losing timing and breath.", {"forms": ["max_power"]}),
        _quest("ssj3_sustain_trial", "SSJ3 Sustain Trial", "goku", "Sustain SSJ3 output long enough to execute a clean finisher sequence.", {"forms": ["super_saiyan_3"]}),
        _quest("biodroid_carapace_protocol", "Biodroid Carapace Protocol", "cell_shade", "Stabilize bio-armor hardening under repeated incoming pressure.", {"forms": ["bioarmor_carapace"]}),
        _quest("capsule_arena_combo_path", "Capsule Arena Combo Path", "vegeta", "Refine close-range pressure strings and knee punishes around guard breaks.", {"techniques": ["crusher_knee"]}),
        _quest("spirit_control_basics", "Spirit Control Basics", "krillin", "Guide detached ki shots and maintain pressure on evasive targets.", {"techniques": ["spirit_shot"]}),
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


def _ensure_character_progress_fields(character):
    character.db.known_techniques = list(character.db.known_techniques or [])
    character.db.unlocked_forms = list(character.db.unlocked_forms or [])
    character.db.lssj_state = dict(character.db.lssj_state or {})


def get_quest_status(character, quest_key):
    state = ensure_player_quest_state(character)
    entry = dict(state.get(quest_key, {}))
    entry.setdefault("accepted", False)
    entry.setdefault("turn_in_ready", False)
    entry.setdefault("completed", False)
    entry.setdefault("reward_claimed", False)
    return entry


def accept_quest(character, quest_key):
    quest = get_quest_definition(quest_key)
    if not quest:
        return False, "Unknown quest.", None
    state = ensure_player_quest_state(character)
    entry = get_quest_status(character, quest_key)
    if entry.get("completed"):
        return False, "Quest already completed.", entry
    if entry.get("accepted"):
        return False, "Quest already accepted.", entry
    entry["accepted"] = True
    entry["accepted_at"] = time.time()
    entry["giver"] = quest.get("giver")
    entry["title"] = quest.get("title")
    state[quest_key] = entry
    character.db.quest_state = state
    return True, f"Accepted quest: {quest['title']}.", entry


def mark_quest_turn_in_ready(character, quest_key):
    quest = get_quest_definition(quest_key)
    if not quest:
        return False, "Unknown quest.", None
    state = ensure_player_quest_state(character)
    entry = get_quest_status(character, quest_key)
    if not entry.get("accepted"):
        return False, "Accept the quest first.", entry
    if entry.get("completed"):
        return False, "Quest already completed.", entry
    entry["turn_in_ready"] = True
    entry["turn_in_ready_at"] = time.time()
    state[quest_key] = entry
    character.db.quest_state = state
    return True, f"{quest['title']} is ready to turn in.", entry


def _grant_reward_techniques(character, keys):
    _ensure_character_progress_fields(character)
    known = set(character.db.known_techniques or [])
    newly = []
    for key in keys or []:
        if key not in known:
            known.add(key)
            newly.append(key)
    character.db.known_techniques = sorted(known)
    return newly


def _grant_reward_forms(character, keys):
    _ensure_character_progress_fields(character)
    unlocked = set(character.db.unlocked_forms or [])
    newly = []
    for key in keys or []:
        if key not in unlocked:
            unlocked.add(key)
            newly.append(key)
    character.db.unlocked_forms = sorted(unlocked)
    return newly


def _grant_reward_lssj(character, payload):
    if not payload:
        return False
    _ensure_character_progress_fields(character)
    state = dict(character.db.lssj_state or {})
    changed = False
    if payload.get("unlock"):
        if not state.get("unlocked"):
            state["unlocked"] = True
            changed = True
    if payload.get("mastery_rank") is not None:
        rank = int(payload.get("mastery_rank") or 0)
        if rank > int(state.get("mastery_rank", 0) or 0):
            state["mastery_rank"] = rank
            changed = True
    if changed:
        character.db.lssj_state = state
    return changed


def grant_quest_rewards(character, quest_key):
    quest = get_quest_definition(quest_key)
    if not quest:
        return False, "Unknown quest.", {}
    rewards = dict(quest.get("rewards", {}))
    granted = {
        "techniques": _grant_reward_techniques(character, rewards.get("techniques", [])),
        "forms": _grant_reward_forms(character, rewards.get("forms", [])),
        "flags": list(rewards.get("flags", [])),
        "lssj_changed": _grant_reward_lssj(character, rewards.get("lssj")),
    }
    if granted["flags"]:
        flags = set(character.db.story_flags or [])
        flags.update(granted["flags"])
        character.db.story_flags = sorted(flags)
    return True, "Rewards granted.", granted


def turn_in_quest(character, quest_key, *, npc_key=None):
    quest = get_quest_definition(quest_key)
    if not quest:
        return False, "Unknown quest.", None
    if npc_key and quest.get("giver") != npc_key:
        return False, "That trainer cannot accept this turn-in.", None

    state = ensure_player_quest_state(character)
    entry = get_quest_status(character, quest_key)
    if entry.get("completed"):
        return False, "Quest already completed.", entry
    if not entry.get("accepted"):
        return False, "Accept the quest first.", entry
    if not entry.get("turn_in_ready"):
        return False, "Quest objectives are not marked complete yet.", entry

    _ok, _msg, granted = grant_quest_rewards(character, quest_key)
    entry["completed"] = True
    entry["reward_claimed"] = True
    entry["completed_at"] = time.time()
    entry["giver"] = quest.get("giver")
    state[quest_key] = entry
    character.db.quest_state = state
    return True, f"Completed quest: {quest['title']}.", {"state": entry, "granted": granted, "quest": quest}


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
