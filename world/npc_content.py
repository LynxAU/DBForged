"""
Iconic Dragon Ball NPC trainer/quest scaffolding definitions.
"""

from __future__ import annotations


NPC_DEFINITIONS = {
    "master_rokan": {
        "name": "Master Rokan",
        "role": "trainer",
        "bio": "A fundamental martial arts master who teaches basic techniques to new fighters.",
        "location_hint": "Earth: Plains - Safe Camp",
        "signature_moves": ["Basic Ki Blast", "Training Fundamentals"],
        "dialogue": [
            "Focus your ki and strike true.",
            "Every master was once a beginner.",
        ],
        "questlines": ["basic_fundamentals"],
        "trainer_rewards": {
            "techniques": ["ki_blast", "kame_wave", "solar_flare", "guard", "afterimage_dash", "vanish_strike"],
            "forms": [],
        },
    },
    "master_roshi": {
        "name": "Master Roshi",
        "role": "trainer",
        "bio": "The legendary Turtle Hermit! He's trained Goku, Gohan, Piccolo and countless others. Despite being lazy, his wisdom is unmatched.",
        "location_hint": "Kame House / Turtle School grounds",
        "signature_moves": ["Kamehameha", "Max Power", "Evil Containment Wave", "Solar Flare"],
        "dialogue": [
            "Hah! You want to train? I've been training for 80 years!",
            "Power without control is just noise. Breathe, then fire.",
            "The Kamehameha? I invented it 50 years ago!",
            "Goku trained here. So did Gohan. And Piccolo!",
        ],
        "dialogue_options": [
            {"keyword": "training", "response": "Training? Hah! You think you're ready for that? First you gotta prove you can handle the basics!"},
            {"keyword": "kamehameha", "response": "The Kamehameha? Now THAT'S a technique! I invented it 50 years ago. But you haven't EARNED it yet, kid!"},
            {"keyword": "quest", "response": "Ah, you want work? Good! I've got plenty. The beach needs cleaning, the turtles need finding, the... wait, why are you smiling? This is WORK, not a reward!"},
            {"keyword": "errand", "response": "Errands? Sure, I've got plenty! Go ask about 'quests' and I'll give you something to do. Consider it... character building!"},
            {"keyword": "work", "response": "Work? What do you think this is, a charity? You wanna learn from me? Then EARN it!"},
            {"keyword": "history", "response": "This island... I've trained here for 80 years. Goku, Gohan, Piccolo... they all started exactly where you are now. Doing MY chores!"},
            {"keyword": "vacation", "response": "Oh, Krillin and 18? They're on vacation. Good people. 18 could destroy this island if she wanted, heh. Unlike SOME people who just want free training..."},
        ],
        "questlines": [
            "turtle_school_fundamentals", 
            "kami_sealing_trials", 
            "kame_island_arrival", 
            "roshi_errand_hermit_crabs",
            "roshi_errand_debris",
            "roshi_errand_turtle",
            "roshi_meditation_training",
            "roshi_sparring_test",
            "roshi_kamehameha_trial",
            "turtle_advanced_beam_doctrine",
            "max_power_body_control",
            "island_explorer"
        ],
        "trainer_rewards": {
            "techniques": ["kame_wave", "super_kamehameha", "evil_containment_wave", "solar_flare"],
            "forms": ["max_power"],
        },
    },
    "krillin": {
        "name": "Krillin",
        "role": "trainer",
        "bio": "The mighty Krillin! Short, bald, and one of Earth's strongest fighters. He's on vacation with his family.",
        "location_hint": "Kame Island - Cottage Grounds",
        "signature_moves": ["Kienzan", "Solar Flare", "Scatter Shot", "Tri-Beam"],
        "dialogue": [
            "This island is the PERFECT training spot!",
            "Man, vacation is great. 18 wanted some peace and quiet.",
        ],
        "dialogue_options": [
            {"keyword": "vacation", "response": "Ah man, this place is SO good! The training grounds are amazing. 18 needed a break from city life, you know?"},
            {"keyword": "training", "response": "Training? I'm on vacation! ...Well, maybe just a little sparring. You look like you can handle yourself!"},
            {"keyword": "18", "response": "18? She's the best, man. Seriously. Could destroy me with one finger. That's why I married her!"},
            {"keyword": "goku", "response": "Goku? Haven't seen him in forever! That guy never stops training. But honestly? I'm happy just taking it easy."},
        ],
        "questlines": ["meet_the_family"],
        "trainer_rewards": {
            "techniques": ["kienzan", "scatter_shot", "tri_beam"],
            "forms": [],
        },
    },
    "android_18": {
        "name": "Android 18",
        "role": "trainer",
        "bio": "Android 18! Created by Dr. Gero but chose peace. She's incredibly powerful but prefers a quiet life with her family.",
        "location_hint": "Kame Island - Vacation Cottage",
        "signature_moves": ["Energy Barrier", "Power Sealing", "Destructo Disc (taught Krillin)"],
        "dialogue": [
            "This island is... peaceful. I like it.",
            "Don't tell Krillin I said this, but he's a good fighter.",
        ],
        "dialogue_options": [
            {"keyword": "vacation", "response": "This island is peaceful. It's rare to find somewhere Krillin won't drag me into training."},
            {"keyword": "daughter", "response": "Marron? She's playing somewhere nearby. Such a sweet girl. I just want her to have a normal life."},
            {"keyword": "training", "response": "I don't need to train. My power is already... sufficient. But Krillin never learns."},
            {"keyword": "power", "response": "My power? Let's just say I'm glad I'm on vacation. Androids don't need to prove ourselves."},
        ],
        "questlines": ["meet_the_family"],
        "trainer_rewards": {
            "techniques": ["barrier", "destructo_disc"],
            "forms": [],
        },
    },
    "marron": {
        "name": "Marron",
        "role": "friendly",
        "bio": "Krillin and Android 18's daughter! A cheerful little girl who represents the peaceful future her parents fought for.",
        "location_hint": "Kame Island - Cottage Grounds",
        "signature_moves": ["Giggle", "Pout", "Super Cute Attack"],
        "dialogue": [
            "Wanna play?",
            "I'm gonna be SUPER strong like Mommy and Daddy!",
        ],
        "dialogue_options": [
            {"keyword": "play", "response": "Wanna play? Daddy says I'm gonna be a super strong fighter like him and Mommy!"},
            {"keyword": "mom", "response": "Mommy is the prettiest! And she can do ANYTHING!"},
            {"keyword": "dad", "response": "Daddy makes funny faces when he trains! He gets all sweaty!"},
        ],
        "questlines": ["meet_the_family"],
    },
    "goku": {
        "name": "Son Goku",
        "role": "trainer",
        "bio": "Earth's Saiyan hero who teaches adaptable combat rhythm, instant movement, and breakthrough transformations.",
        "location_hint": "Mount Paozu",
        "signature_moves": ["Kamehameha", "Instant Transmission", "Dragon Fist", "Super Saiyan forms", "Spirit Bomb"],
        "dialogue": [
            "Don't copy me exactly. Find the version that works for your body.",
            "When the opening appears, move first and trust your training.",
            "The Spirit Bomb gathers energy from all living things - it's not just ki, it's life itself!",
        ],
        "questlines": ["ssj_breakpoint", "dragon_fist_trial", "instant_shift_attunement", "spirit_bomb_trial"],
        "trainer_rewards": {
            "techniques": ["instant_transmission", "dragon_fist", "super_kamehameha", "spirit_bomb"],
            "forms": ["super_saiyan", "super_saiyan_2", "super_saiyan_3"],
        },
    },
    "vegeta": {
        "name": "Prince Vegeta",
        "role": "trainer",
        "bio": "The proud Saiyan prince who teaches aggressive pressure tactics and Great Ape control.",
        "location_hint": "Capsule Corp training grounds",
        "signature_moves": ["Galick Gun", "Final Flash", "Big Bang Attack", "Great Ape"],
        "dialogue": [
            "You think you can surpass me? Pathetic!",
            "A Saiyan must always push beyond their limits.",
            "Focus on your tail control - it's the key to Great Ape power.",
        ],
        "questlines": ["tail_training", "galick_gun_mastery", "royal_pride"],
        "trainer_rewards": {
            "techniques": ["galick_gun", "final_flash", "big_bang_attack"],
            "forms": ["super_saiyan", "great_ape"],
        },
    },
    "piccolo": {
        "name": "Piccolo",
        "role": "trainer",
        "bio": "The Namekian warrior who teaches defensive tactics, special beam cannon, and regeneration.",
        "location_hint": "Sacred Namekian Forest / Capsule Corp",
        "signature_moves": ["Special Beam Cannon", "Multi-Form", "Regeneration", "Hellzone Grenade"],
        "dialogue": [
            "Defense wins battles. Attack is just the finishing move.",
            "A warrior must know pain to understand victory.",
            "Your regeneration is tied to your spirit. Focus!",
        ],
        "questlines": ["namekian_fusion_understanding", "special_beam_mastery", "regen_mastery"],
        "trainer_rewards": {
            "techniques": ["special_beam_cannon", "multi_form", "hellzone_grenade"],
            "forms": ["namekian_fusion"],
        },
    },
    "trunks": {
        "name": "Future Trunks",
        "role": "trainer",
        "bio": "The time-traveling warrior from a dark future who teaches sword techniques and sword_Beam.",
        "location_hint": "Capsule Corp / Earth unspecified",
        "signature_moves": ["Sword Beam", "Finish Buster", "Burning Attack", "Super Saiyan forms"],
        "dialogue": [
            "You must protect your timeline at all costs.",
            "A sword is an extension of the soul. Train with blade and ki together.",
            "Hope... it's what gives us strength to fight.",
        ],
        "questlines": ["sword_attunement", "time_displacement_insight", "future_warrior_prep"],
        "trainer_rewards": {
            "techniques": ["sword_beam", "finish_buster", "burning_attack"],
            "forms": ["super_saiyan", "super_saiyan_2"],
        },
    },
    "king_kai": {
        "name": "King Kai",
        "role": "trainer",
        "bio": "The North Kai of the afterlife. Teaches Kaioken and trains dead warriors.",
        "location_hint": "King Kai's Planet (afterlife)",
        "signature_moves": ["Kaioken", "Kaoha", "Ray", "Pass"],
        "dialogue": [
            "Welcome to my planet! But... you're not dead yet? Fascinating.",
            "Kaioken multiplies your power, but strains your body. Balance is key!",
            "Hey! Don't forget my catchphrase! HAAAI!",
        ],
        "questlines": ["kaioken_attunement", "kaioken_x3_trial", "kaioken_x10_trial"],
        "trainer_rewards": {
            "techniques": ["kaioken", "kaioken_x3", "kaioken_x10", "kaioken_x20"],
            "forms": [],
        },
    },
    "whis": {
        "name": "Whis",
        "role": "trainer",
        "bio": "The Angelic attendant of Beerus. Teaches Ultra Instinct to worthy warriors.",
        "location_hint": "Beerus's Planet / Divine Realm",
        "signature_moves": ["Angel's Rhythm", "Ultra Instinct", "Divine Slash"],
        "dialogue": [
            "Ultra Instinct is not about power... it's about moving without thought.",
            "The body moves faster than the mind. That is the key.",
            "My training is strict, but the results speak for themselves.",
        ],
        "questlines": ["ultra_instinct_intro", "ultra_instinct_sign", "ultra_instinct_mastered", "ultra_instinct_breached"],
        "trainer_rewards": {
            "techniques": ["ultra_instinct_dodge"],
            "forms": ["ultra_instinct_sign", "ultra_instinct_mastered", "ultra_instinct_breached"],
        },
    },
    "baba": {
        "name": "Fortuneteller Baba",
        "role": "trainer",
        "bio": "A mysterious fortuneteller who knows the secrets of legendary healing items like the Senzu bean.",
        "location_hint": "Baba's Palace / Crystal Cave",
        "signature_moves": ["Spirit Fist", "Senzu Bean knowledge"],
        "dialogue": [
            "I see... you seek the Senzu bean's power.",
            "Very rare, very valuable. But I know where one grows.",
            "Would you like to know?",
        ],
        "questlines": ["senzu_quest"],
        "trainer_rewards": {
            "techniques": ["senzu_bean"],
            "forms": [],
        },
    },
    "baba": {
        "name": "Fortuneteller Baba",
        "role": "trainer",
        "bio": "A mysterious fortuneteller who knows the secrets of legendary healing items like the Senzu bean.",
        "location_hint": "Baba's Palace / Crystal Cave",
        "signature_moves": ["Spirit Fist", "Senzu Bean knowledge"],
        "dialogue": [
            "I see... you seek the Senzu bean's power.",
            "Very rare, very valuable. But I know where one grows.",
            "Would you like to know?",
        ],
        "questlines": ["senzu_quest"],
        "trainer_rewards": {
            "techniques": ["senzu_bean"],
            "forms": [],
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
        "questlines": ["elder_kai_ritual", "sacred_world_attunement", "kai_guardian_vow", "potara_fusion_rites", "potara_ultimate_arts"],
        "trainer_rewards": {
            "techniques": ["telekinesis_hold", "potara_earrings", "soul_buster"],
            "forms": ["potential_unleashed", "kai_unsealed", "godly_empowerment", "potara_fusion"],
        },
    },
    "metamoran_master": {
        "name": "Metamoran Master",
        "role": "trainer",
        "bio": "A mysterious martial artist who teaches the legendary Metamoran dance fusion technique. Only those with perfect rhythm and synchronization can learn this art.",
        "location_hint": "Metamoran Training Grounds / Hidden Mountain Sanctuary",
        "signature_moves": ["Metamoran Dance", "Stardust Fall", "Fusion Kamehameha"],
        "dialogue": [
            "Dance is the ultimate expression of combat harmony.",
            "Two bodies, one mind. That is the fusion way.",
            "Your rhythm must be perfect, or the dance fails.",
        ],
        "questlines": ["metamoran_dance_teaching", "metamoran_barrage_training", "fusion_beam_mastery"],
        "trainer_rewards": {
            "techniques": ["metamoran_dance", "stardust_fall", "fusion_kamehameha", "double_galick_cannon"],
            "forms": ["metamoran_fusion"],
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
    "king_kai": {
        "name": "King Kai",
        "role": "trainer",
        "bio": "The North Kai of the Afterlife teaches the powerful Kaioken technique. His training is demanding but essential for those seeking explosive power. Kaioken can be charged mid-battle to increase its multiplier - x3 at 3s, x10 at 6s, x20 at 10s.",
        "location_hint": "King Kai's Planet (Afterlife)",
        "signature_moves": ["Kaioken (hold to charge)", "Spirit Bomb"],
        "dialogue": [
            "Kaioken multiplies your power, but at a price. Train your body to handle the strain!",
            "Hold Kaioken to charge it - the longer you hold, the more power you get. But be careful - strain builds up fast!",
            "Focus ki in your limbs, not just your spirit. Control is everything.",
        ],
        "questlines": ["snake_way_endurance", "kaioken_stability_trials"],
        "trainer_rewards": {
            "techniques": ["kaioken", "spirit_bomb"],
            "forms": ["kaioken"],
        },
    },
    "whis": {
        "name": "Whis",
        "role": "trainer",
        "bio": "The Angel attendant to Beerus teaches Ultra Instinct - the ultimate combat technique. His gentle demeanor hides an incredibly demanding training regime.",
        "location_hint": "Beerus's Planet / Angel Temple",
        "signature_moves": ["Ultra Instinct Sign", "Mastered Ultra Instinct", "Angel Strike"],
        "dialogue": [
            "Ultra Instinct is not about power. It's about moving without thinking.",
            "Your body must learn to act before your mind decides. That's the key.",
            "Relaxation and tension - balance them, and you'll understand.",
        ],
        "questlines": ["ultra_instinct_awakening", "ultra_instinct_mastery", "ui_overwhelm_event", "whis_control_trials"],
        "trainer_rewards": {
            "techniques": ["angel_strike", "ultra_instinct_dodge"],
            "forms": ["ultra_instinct_sign", "ultra_instinct", "ultra_instinct_breached"],
        },
    },
    "bulma": {
        "name": "Bulma",
        "role": "shopkeeper",
        "bio": "The brilliant scientist of Capsule Corp. She runs the shop and sells various equipment and items to fighters.",
        "location_hint": "Capsule Corp - Main Shop",
        "signature_moves": [],
        "dialogue": [
            "Welcome to Capsule Corp! Take a look at my inventory.",
            "We've got the best gear in the world!",
            "Need a scouter? We've got plenty!",
            "Senzu beans are rare, but I have a few in stock.",
        ],
        "questlines": ["shopping_trip"],
        "shop_items": {
            "weighted_clothing": {"price": 500, "description": "Training gear that increases power gain by 10%"},
            "scouter": {"price": 1000, "description": "Device to scan enemy power levels"},
            "senzu_bean": {"price": 2000, "description": "Legendary healing bean that fully restores health"},
            "potara_earrings": {"price": 10000, "description": "Sacred earrings enabling Potara fusion - requires two pairs"},
        },
    },
}


def get_npc_definition(key):
    return NPC_DEFINITIONS.get(key)


def iter_npc_definitions():
    for key in sorted(NPC_DEFINITIONS.keys()):
        yield key, NPC_DEFINITIONS[key]
