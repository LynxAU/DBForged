"""
Iconic Dragon Ball NPC trainer/quest scaffolding definitions.
"""

from __future__ import annotations


NPC_DEFINITIONS = {
    "master_roshi": {
        "name": "Master Roshi",
        "role": "trainer",
        "bio": "The Turtle Hermit and founder of the Turtle School, Roshi trains fundamentals, discipline, and classic Earth techniques.",
        "location_hint": "Kame House / Turtle School grounds",
        "signature_moves": ["Kamehameha", "Max Power", "Evil Containment Wave", "Solar Flare (tournament-era use)"],
        "dialogue": [
            "Power without control is just noise. Breathe, then fire.",
            "A technique is more than a blast. It's timing, stance, and intent.",
        ],
        "questlines": ["turtle_school_fundamentals", "kami_sealing_trials"],
        "trainer_rewards": {
            "techniques": ["kame_wave", "super_kamehameha", "evil_containment_wave", "solar_flare", "max_power"],
            "forms": ["max_power"],
        },
    },
    "goku": {
        "name": "Son Goku",
        "role": "trainer",
        "bio": "Earth's Saiyan hero who teaches adaptable combat rhythm, instant movement, and breakthrough transformations.",
        "location_hint": "Capsule Corp training grounds / remote sparring instances",
        "signature_moves": ["Kamehameha", "Instant Transmission", "Dragon Fist", "Super Saiyan forms"],
        "dialogue": [
            "Don't copy me exactly. Find the version that works for your body.",
            "When the opening appears, move first and trust your training.",
        ],
        "questlines": ["ssj_breakpoint", "dragon_fist_trial", "instant_shift_attunement"],
        "trainer_rewards": {
            "techniques": ["instant_transmission", "dragon_fist", "super_kamehameha"],
            "forms": ["super_saiyan", "super_saiyan_2", "super_saiyan_3"],
        },
    },
    "vegeta": {
        "name": "Vegeta",
        "role": "trainer",
        "bio": "Prince of all Saiyans, Vegeta specializes in ruthless pressure, beam superiority, and pride-forged combat discipline.",
        "location_hint": "Capsule Corp gravity chamber",
        "signature_moves": ["Galick Gun", "Big Bang Attack", "Final Flash", "Super Saiyan Blue"],
        "dialogue": [
            "If your form wastes motion, your power means nothing.",
            "Dominate the exchange. Don't wait to be tested.",
        ],
        "questlines": ["gravity_chamber_proving", "storm_ascension", "whis_control_trials"],
        "trainer_rewards": {
            "techniques": ["galick_gun", "big_bang_attack", "final_flash", "tail_sweep"],
            "forms": ["super_saiyan_grade2", "super_saiyan_blue"],
        },
    },
    "piccolo": {
        "name": "Piccolo",
        "role": "trainer",
        "bio": "The Namekian master strategist teaches precision, discipline, and control-based offense.",
        "location_hint": "Wasteland plateau / Lookout sparring area",
        "signature_moves": ["Special Beam Cannon", "Masenko", "Makosen", "Giant Namekian"],
        "dialogue": [
            "Observe first. Attack second. Survive always.",
            "Precision beats panic. Control the line, control the fight.",
        ],
        "questlines": ["namekian_gianting", "precision_drill_spiral", "lookout_focus_trials"],
        "trainer_rewards": {
            "techniques": ["special_beam_cannon", "masenko", "makosen", "regeneration_focus"],
            "forms": ["giant_namekian", "dragon_clan_focus"],
        },
    },
    "krillin": {
        "name": "Krillin",
        "role": "trainer",
        "bio": "A veteran Earthling fighter who emphasizes cunning, survival, and timing over brute force.",
        "location_hint": "Kame House / tournament practice ring",
        "signature_moves": ["Destructo Disc", "Solar Flare", "Scatter Shot"],
        "dialogue": [
            "Winning isn't about looking flashy. It's about staying in the fight.",
            "Use movement and timing. Don't give stronger opponents clean reads.",
        ],
        "questlines": ["disc_control_drills", "survivor_instinct_course"],
        "trainer_rewards": {
            "techniques": ["destructo_disc", "kienzan_barrage", "scatter_shot"],
            "forms": [],
        },
    },
    "tien": {
        "name": "Tien Shinhan",
        "role": "trainer",
        "bio": "A disciplined martial artist who trains precision bursts, sacrifice techniques, and battlefield focus.",
        "location_hint": "Mountain dojo / isolated training grounds",
        "signature_moves": ["Tri-Beam", "Dodon Ray", "Solar Flare"],
        "dialogue": [
            "Technique should have purpose. Cost without payoff is weakness.",
            "Discipline is power you can still use when panic starts.",
        ],
        "questlines": ["crane_discipline_course", "tri_beam_endurance"],
        "trainer_rewards": {
            "techniques": ["tri_beam", "dodon_ray", "feint_step"],
            "forms": [],
        },
    },
    "king_kai": {
        "name": "King Kai",
        "role": "trainer",
        "bio": "North Kai teaches spiritual discipline, Kaioken strain management, and otherworld endurance.",
        "location_hint": "King Kai's Planet",
        "signature_moves": ["Kaioken", "Spirit Bomb (future content)"],
        "dialogue": [
            "Control your body before you multiply your power.",
            "Kaioken isn't a shortcut. It's a test of restraint.",
        ],
        "questlines": ["snake_way_endurance", "kaioken_stability_trials"],
        "trainer_rewards": {
            "techniques": [],
            "forms": ["kaioken"],
        },
    },
    "supreme_kai": {
        "name": "Supreme Kai",
        "role": "trainer",
        "bio": "A divine Kai who teaches sacred ki control, sealing, and latent potential rituals.",
        "location_hint": "Sacred World of the Kai",
        "signature_moves": ["Telekinesis", "Divine bindings", "Potential Unleashed (ritual guidance)"],
        "dialogue": [
            "Godly ki is not louder. It is cleaner.",
            "A sealed mind cannot master divine techniques.",
        ],
        "questlines": ["elder_kai_ritual", "sacred_world_attunement", "kai_guardian_vow"],
        "trainer_rewards": {
            "techniques": ["telekinesis_hold"],
            "forms": ["potential_unleashed", "kai_unsealed", "godly_empowerment"],
        },
    },
    "whis": {
        "name": "Whis",
        "role": "trainer",
        "bio": "Beerus's angel attendant, Whis trains divine movement, composure, and god-ki refinement.",
        "location_hint": "Beerus's World",
        "signature_moves": ["Ultra Instinct principles", "God ki refinement", "Staff techniques"],
        "dialogue": [
            "The body should move before the mind argues.",
            "Refinement beats excess. Again.",
        ],
        "questlines": ["god_ki_ritual", "whis_control_trials", "angelic_motion_basics"],
        "trainer_rewards": {
            "techniques": ["psychic_burst"],
            "forms": ["super_saiyan_god", "super_saiyan_blue"],
        },
    },
    "frieza": {
        "name": "Frieza",
        "role": "trainer",
        "bio": "The galactic tyrant is a ruthless source of Frost Demon technique and form mastery for those willing to survive the lesson.",
        "location_hint": "Frieza Force flagship / imperial training chamber",
        "signature_moves": ["Death Beam", "Death Ball", "Supernova", "Golden Form"],
        "dialogue": [
            "Efficiency is elegance. Waste is for soldiers.",
            "If you insist on power, at least make it precise.",
        ],
        "questlines": ["imperial_unsealing", "golden_refinement", "emperor_precision_drills"],
        "trainer_rewards": {
            "techniques": ["death_beam", "death_ball", "supernova", "crusher_ball"],
            "forms": ["frost_demon_true_form", "frost_demon_final_form", "golden_frost"],
        },
    },
    "cell_shade": {
        "name": "Cell (Simulation)",
        "role": "trainer",
        "bio": "A Capsule Corp combat simulation based on Cell's battle data, used to test adaptive biodroid evolution.",
        "location_hint": "Capsule Corp simulation chamber",
        "signature_moves": ["Adaptive genome combat", "Perfect form evolution", "Beam pressure"],
        "dialogue": [
            "Perfection is iterative. Survive, adapt, repeat.",
            "If you can be read, you can be dismantled.",
        ],
        "questlines": ["evolution_catalyst_alpha", "evolution_catalyst_omega", "zenkai_evolution_event"],
        "trainer_rewards": {
            "techniques": ["omega_blaster", "spirit_breaking_fist"],
            "forms": ["biodroid_stage_two", "biodroid_perfect", "super_perfect_biodroid", "bioarmor_carapace"],
        },
    },
    "broly": {
        "name": "Broly",
        "role": "trainer",
        "bio": "The Legendary Saiyan's training path is less about imitation and more about surviving escalating power safely.",
        "location_hint": "Remote wilderness / controlled combat arena",
        "signature_moves": ["Eraser Cannon", "Omega Blaster", "Legendary Super Saiyan"],
        "dialogue": [
            "Power comes fast. Control comes slower. Train both.",
            "If you lose yourself, the battle is already over.",
        ],
        "questlines": ["broly_lineage_echoes", "legendary_control_protocol", "legendary_rage_forge"],
        "trainer_rewards": {
            "techniques": ["eraser_cannon"],
            "forms": ["legendary_super_saiyan"],
        },
    },
    "baby": {
        "name": "Baby",
        "role": "trainer",
        "bio": "The Tuffle parasite survivor teaches Truffle/Tuffle tactical control, parasitic disruption, and machine-assisted warfare.",
        "location_hint": "Tuffle lab ruins / parasite command node",
        "signature_moves": ["Parasitic control", "machine merge", "probe warfare"],
        "dialogue": [
            "Win the battlefield before the punches start.",
            "Technology is power that doesn't tire.",
        ],
        "questlines": ["tuffle_mech_sync", "parasite_protocols", "tactical_probe_network"],
        "trainer_rewards": {
            "techniques": ["gravity_bind"],
            "forms": ["truffle_machine_merge", "truffle_parasite_overdrive"],
        },
    },
    "jiren_echo": {
        "name": "Jiren (Meditation Echo)",
        "role": "trainer",
        "bio": "A meditative projection modeled after Jiren's style, teaching resolve and overwhelming pressure control.",
        "location_hint": "Tournament of Power simulation chamber",
        "signature_moves": ["Psychic pressure", "meditative focus", "limit break resolve"],
        "dialogue": [
            "Power without resolve collapses under pressure.",
            "Stand. Breathe. Break your limit deliberately.",
        ],
        "questlines": ["tournament_resolve", "grey_dominance_trials"],
        "trainer_rewards": {
            "techniques": ["psychic_burst", "gravity_bind"],
            "forms": ["meditative_limit", "grey_limit_break"],
        },
    },
    "yamcha": {
        "name": "Yamcha",
        "role": "trainer",
        "bio": "A desert bandit turned veteran Z Fighter, Yamcha teaches practical rushdowns, movement feints, and pressure survival.",
        "location_hint": "Desert training field / tournament practice ring",
        "signature_moves": ["Wolf Fang Fist", "Spirit Ball (future content)", "Feint-heavy rush combat"],
        "dialogue": [
            "You don't need the biggest blast if your footwork wins the exchange.",
            "Rush clean, exit clean. Don't feed counters.",
        ],
        "questlines": ["desert_wolf_rush", "practical_brawler_drills"],
        "trainer_rewards": {
            "techniques": ["wolf_fang_fist", "mach_punch_barrage", "feint_step"],
            "forms": [],
        },
    },
    "future_trunks": {
        "name": "Future Trunks",
        "role": "trainer",
        "bio": "A hardened future warrior who teaches disciplined pressure beams and efficient finisher routing under real battlefield conditions.",
        "location_hint": "Capsule Corp simulation yard / future ruin simulation",
        "signature_moves": ["Burning Attack", "Finish Buster", "Buster Cannon"],
        "dialogue": [
            "Waste no motion. End the fight before the battlefield punishes you.",
            "Precision under pressure is what keeps everyone alive.",
        ],
        "questlines": ["future_ruin_pressure", "burning_hand_signs", "finish_buster_routing"],
        "trainer_rewards": {
            "techniques": ["burning_attack", "finish_buster", "buster_cannon"],
            "forms": [],
        },
    },
    "gohan": {
        "name": "Son Gohan",
        "role": "trainer",
        "bio": "A scholar-warrior who trains hybrid potential, controlled surges, and intelligent battlefield adaptation.",
        "location_hint": "Orange Star training annex / wilderness sparring field",
        "signature_moves": ["Masenko", "Potential Unleashed", "Beast (advanced)"],
        "dialogue": [
            "Power spikes are useless if your fundamentals collapse.",
            "Stay calm, read the field, then commit.",
        ],
        "questlines": ["hybrid_composure_drills", "beast_edge_focus"],
        "trainer_rewards": {
            "techniques": ["wild_sense", "consecutive_energy_blast", "justice_rush"],
            "forms": ["beast"],
        },
    },
    "android_17": {
        "name": "Android 17",
        "role": "trainer",
        "bio": "A ruthless efficiency fighter who teaches barrier timing, spacing, and sustained pressure with minimal waste.",
        "location_hint": "Wildlife preserve combat range / Tournament arena sim",
        "signature_moves": ["Barrier", "Explosive Wave", "Efficient sustained combat"],
        "dialogue": [
            "Win on efficiency. Let your opponent waste the extra energy.",
            "A barrier is timing, not panic.",
        ],
        "questlines": ["ranger_barrier_protocols", "arena_efficiency_loop"],
        "trainer_rewards": {
            "techniques": ["barrier", "explosive_wave", "consecutive_energy_blast"],
            "forms": [],
        },
    },
    "gogeta": {
        "name": "Gogeta",
        "role": "trainer",
        "bio": "A fusion warrior who represents the apex of decisive finisher routes and overwhelming beam conversion.",
        "location_hint": "Fusion training chamber / movie-era battle simulation",
        "signature_moves": ["Big Bang Kamehameha", "Soul Punisher (future content)"],
        "dialogue": [
            "Fusion power means nothing if your timing is sloppy.",
            "Build the opening, then finish cleanly.",
        ],
        "questlines": ["fusion_finisher_discipline"],
        "trainer_rewards": {
            "techniques": ["big_bang_kamehameha"],
            "forms": [],
        },
    },
    "toppo": {
        "name": "Toppo",
        "role": "trainer",
        "bio": "A Pride Trooper captain who teaches discipline, justice-themed pressure chains, and control under tournament rules.",
        "location_hint": "Pride Trooper simulation arena",
        "signature_moves": ["Justice Rush", "pressure grapples", "heroic suppression"],
        "dialogue": [
            "Justice is discipline under pressure, not loud speeches.",
            "Command the pace and your enemy will break first.",
        ],
        "questlines": ["pride_trooper_formation", "justice_combo_doctrine"],
        "trainer_rewards": {
            "techniques": ["justice_rush", "crusher_knee"],
            "forms": [],
        },
    },
}


def get_npc_definition(key):
    return NPC_DEFINITIONS.get(key)


def iter_npc_definitions():
    for key in sorted(NPC_DEFINITIONS.keys()):
        yield key, NPC_DEFINITIONS[key]
