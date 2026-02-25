"""
Builder script to generate Planet Vegeta (Royal Vegeta City) - Complete Edition.
This creates ~100 rooms representing the full Saiyan capital city.

To execute:
    evennia run build_planet_vegeta
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_planet_vegeta():
    # Helper to create a room
    def make_room(key, desc, planet="Planet Vegeta", climate="volcanic", pl_min=0, pl_max=0):
        room = create_object(Room, key=key)
        room.db.desc = desc
        room.db.planet = planet
        room.db.climate = climate
        room.db.power_level_min = pl_min
        room.db.power_level_max = pl_max
        return room

    # Helper to link two rooms bidirectionally
    def link_rooms(room1, dir1, room2, dir2, exit_desc=None):
        if not room1 or not room2: return
        
        abbr = {
            "north": "n", "south": "s", "east": "e", "west": "w",
            "northeast": "ne", "northwest": "nw", "southeast": "se", "southwest": "sw",
            "up": "u", "down": "d"
        }
        
        a1 = [abbr[dir1]] if dir1 in abbr else []
        a2 = [abbr[dir2]] if dir2 in abbr else []
        
        exit_north = create_object(Exit, key=dir1, aliases=a1, location=room1, destination=room2)
        exit_south = create_object(Exit, key=dir2, aliases=a2, location=room2, destination=room1)
        
        if exit_desc:
            exit_north.db.desc = exit_desc
            exit_south.db.desc = exit_desc

    print("Cleaning up old Planet Vegeta locations...")
    old_rooms = search_tag("Planet Vegeta", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Planet Vegeta - Royal Vegeta City...")

    # === OUTSKIRTS ===
    
    outskirts_enter = make_room("Vegeta Outskirts - Landing Zone",
        "The primary landing area for spacecraft arriving on Planet Vegeta. The ground is scorched from countless landings, and the air thick with engine fumes. Guard towers loom in the distance, monitoring all arrivals. The red sky casts an ominous glow over everything.",
        pl_min=1000, pl_max=5000)

    trade_district_entrance = make_room("Trade District Entrance",
        "A bustling checkpoint where merchants and travelers enter the city. Saiyan guards inspect cargo and documents with military precision. Banners of the Vegeta Royal Family flutter in the wind. The smell of exotic foods wafts from beyond the gates.",
        pl_min=1000, pl_max=3000)

    military_checkpoint = make_room("Military Checkpoint",
        "A fortified gate where the Saiyan military screens all traffic. Soldiers in full battle armor check identification and purpose for entry. A notice board displays wanted posters and recent decrees from the King.",
        pl_min=2000, pl_max=5000)

    # === TRADE DISTRICT ===

    market_square = make_room("Trade District - Central Market",
        "The heart of commerce on Planet Vegeta. Stalls and shops line the streets, selling everything from weapons to war supplies. Merchants hawk their wares in loud voices, and bargaining is a contact sport. The smell of roasted meat and strong drinks fills the air.",
        pl_min=500, pl_max=2000)

    weapon_workshop = make_room("Saiyan Arms Forge",
        "A massive smithy producing the finest Saiyan weapons. The clang of hammer on metal echoes constantly. Master craftsmen forge battle axes, polearms, and custom weapons. A display case shows famous blades crafted here, their histories etched in gold.",
        pl_min=2000, pl_max=10000)

    armor_dealer = make_room("Battle Gear Outfitter",
        "A shop specializing in Saiyan combat armor. Protective gear of all varieties lines the walls - from basic combat suits to elite battle armor. A fitting area allows customers to try before they buy. The shopkeeper watches you with calculating eyes.",
        pl_min=1500, pl_max=8000)

    food_stall_district = make_room("Warrior's Feast Hall",
        "A massive outdoor market area dedicated to food and drink. Vendors sell roasted saurs, grilled meats, strong alcohol, and energy drinks favored by fighters. Groups of soldiers gather here after training, loudly celebrating or nursing their wounds.",
        pl_min=500, pl_max=3000)

    spice_merchant = make_room("Exotic Spices & Enhancements",
        "A shady shop dealing in combat-enhancing substances. The merchant claims these herbs and compounds can boost power temporarily. Warning labels are prominently displayed, though their effectiveness is debatable. Not all enhancers are legal.",
        pl_min=3000, pl_max=15000)

    # === RESIDENTIAL DISTRICT ===

    residential_north = make_room("Residential District - Noble Heights",
        "A quieter area where mid-ranking Saiyan nobles reside. Large homes with proper yards line the streets. Children can be seen playing combat games in the yards, training from a young age. The architecture is more refined here, showing a hint of refinement.",
        pl_min=2000, pl_max=8000)

    residential_south = make_room("Residential District - Warrior Quarters",
        "Standard housing for elite soldiers and their families. Homes are practical and well-maintained. Training yards are common, and the sounds of combat practice echo through the streets. Pride flags from famous warrior families adorn many homes.",
        pl_min=1500, pl_max=6000)

    noble_estate = make_room("House of Korro",
        "The estate of a powerful noble family. Impressive walls surround the property, and guards stand at attention. Through the gates, you can see training grounds, gardens, and a large mansion. Only the elite may enter.",
        pl_min=10000, pl_max=50000)

    warrior_barracks = make_room("Elite Warrior Barracks",
        "Living quarters for the Royal Guard. The buildings are well-maintained and imposing. Soldiers in pristine armor patrol the perimeter. Inside, warriors rest between missions or tend to their equipment. A notice board lists current assignments.",
        pl_min=5000, pl_max=20000)

    # === ENTERTAINMENT DISTRICT ===

    fighting_pits_entrance = make_room("Fighting Pits - Entrance",
        "The infamous underground fighting arena of Vegeta City. Banners depicting legendary battles line the walls. Spectators stream in and out, their faces painted with team colors. The sounds of combat and crowd roars emanate from below.",
        pl_min=2000, pl_max=15000)

    fighting_pit_main = make_room("The Grand Fighting Pit",
        "A massive circular arena where warriors battle for glory and money. The stands are packed with enthusiastic spectators. Two warriors circle each other in the center, trading blows. Betting is fierce and passions run high.",
        pl_min=5000, pl_max=30000)

    fighting_pit_champions = make_room("Champions Ring",
        "The sacred arena where champions prove their worth. The ground is stained with the blood of legends. A golden belt hangs above the winner's platform, awarded to the greatest fighters. Only the brave or foolish enter here.",
        pl_min=10000, pl_max=100000)

    bar_district = make_room("Warrior's Rest Tavern Row",
        "A collection of bars and taverns catering to Saiyan warriors. The noise is deafening - laughter, arguments, and the occasional brawl fill the air. Old veterans tell war stories while young soldiers listen with wide eyes. The drink is strong and the tales are wilder.",
        pl_min=1000, pl_max=5000)

    casino_entrance = make_room("Royal Casino - Entrance",
        "An upscale gambling establishment frequented by the wealthy. Elegant decor and soft lighting create an atmosphere of sophistication. The clink of chips and murmur of high-stakes betting fills the air. Guards ensure only those with sufficient wealth enter.",
        pl_min=5000, pl_max=50000)

    casino_main = make_room("Royal Casino - Gaming Floor",
        "The heart of the gambling action. Card tables, dice pits, and slot machines offer various games of chance. High-rollers bet fortunes on single hands. Beautiful servers offer drinks while security watches for cheaters.",
        pl_min=10000, pl_max=100000)

    # === MILITARY DISTRICT ===

    military_headquarters = make_room("Military Headquarters",
        "The central command building for the Saiyan armed forces. Massive banners display the royal crest and military insignia. Officers rush in and out, carrying orders. A war map dominates one wall, showing strategic positions across the planet.",
        pl_min=10000, pl_max=50000)

    training_grounds = make_room("Royal Training Grounds",
        "The primary training facility for elite Saiyan warriors. Multiple training areas cater to different combat styles. Weight rooms, sparring rings, and obstacle courses fill the complex. Instructors bark orders and warriors push themselves to their limits.",
        pl_min=5000, pl_max=30000)

    advanced_training = make_room("Hyperbolic Time Chamber Entrance",
        "A mysterious chamber said to warp time itself. Only the most elite warriors are permitted entry. The entrance glows with temporal energy, and those who enter emerge... changed. Years may pass inside while only days pass outside.",
        pl_min=50000, pl_max=500000)

    armory = make_room("Royal Armory",
        "The greatest repository of Saiyan military equipment. Weapons and armor of every variety are stored here, from standard issue to experimental prototypes. Artifacts from past conquests are displayed like trophies. Only officers may requisition items.",
        pl_min=8000, pl_max=40000)

    medical_bay = make_room("Saiyan Medical Center",
        "Advanced medical facilities for treating battle injuries. Healing pods line the walls, glowing with regenerative energy. The best doctors in the empire tend to the wounded. Even the most severe injuries can be repaired, for a price.",
        pl_min=3000, pl_max=15000)

    # === ROYAL PALACE COMPLEX ===

    palace_gates = make_room("Royal Palace Gates",
        "The magnificent gates to the palace of the Saiyan King. Massive golden doors are inscribed with the royal family's history. Guards in ceremonial armor stand at rigid attention. The palace rises behind them, a towering monument to Saiyan power.",
        pl_min=20000, pl_max=100000)

    outer_courtyard = make_room("Palace Outer Courtyard",
        "A grand courtyard leading to the inner palace. Ornate gardens and fountains create a strange beauty amid the martial surroundings. Servants and officials hurry across the courtyard on important business. The energy of the palace is palpable.",
        pl_min=15000, pl_max=80000)

    throne_room_entrance = make_room("Throne Room Entrance",
        "The dramatic entrance to the throne room. Massive columns support a ceiling painted with battle scenes. The floor is polished marble, reflecting the grandeur above. Guards bow as you pass, admitting you to the presence of royalty.",
        pl_min=30000, pl_max=150000)

    main_throne_room = make_room("Royal Throne Room",
        "The seat of power for the Saiyan Empire. A massive throne of fused metal dominates the room, decorated with trophies from conquered worlds. The current ruler sits upon it, surrounded by advisors and guards. This is where the fate of billions is decided.",
        pl_min=50000, pl_max=500000)

    throne_room_balcony = make_room("Throne Room - Grand Balcony",
        "A sweeping balcony overlooking the capital city. The King often addresses the populace from here. On special occasions, victorious warriors are presented to the crowd below. The view of Royal Vegeta City is spectacular, stretching to the horizon.",
        pl_min=40000, pl_max=200000)

    royal_gardens = make_room("Royal Gardens",
        "A surprising oasis of peace within the palace. Exotic plants from conquered worlds grow here, maintained by expert gardeners. A koi pond reflects the red sky. Nobles take their exercise here, walking between meetings of war and politics.",
        pl_min=20000, pl_max=100000)

    treasury = make_room("Royal Treasury",
        "A heavily guarded vault containing the empire's wealth. Bricks of refined metals, precious gems from a hundred worlds, and currency from fallen civilizations fill the vault. Guards are everywhere, and security is absolute.",
        pl_min=100000, pl_max=1000000)

    royal_library = make_room("Royal Archives",
        "A repository of Saiyan knowledge and history. Ancient scrolls and modern data-pads coexist. Scholars study military tactics, planetary histories, and combat techniques. The wisdom of conquered civilizations is preserved here.",
        pl_min=10000, pl_max=50000)

    # === UNDERGROUND FACILITIES ===

    underground_entrance = make_room("Underground Complex - Entrance",
        "A hidden access point to secret facilities beneath the city. The entrance is disguised as a storage building. Down the stairs lies a network of tunnels and chambers used for classified operations. Not even most soldiers know this place exists.",
        pl_min=20000, pl_max=100000)

    underground_prison = make_room("State Prison",
        "A grim facility for holding prisoners of war and political dissidents. Cells line the walls, each containing inmates who know they'll never leave. Interrogation rooms echo with sounds best left unheard. The guards here have... unusual methods.",
        pl_min=15000, pl_max=75000)

    secret_lab = make_room("Bio-Research Laboratory",
        "A top-secret facility for genetic experiments. The stuff of nightmares fills the test chambers - half-formed creatures, enhanced soldiers, biological weapons. Scientists in white coats work on projects that would horrify even the cruelest warlords.",
        pl_min=30000, pl_max=200000)

    # === CITY PERIPHERY ===

    city_wall_north = make_room("City Wall - North Gate",
        "The massive northern wall of Royal Vegeta City. Guard towers stand at regular intervals, and soldiers patrol the battlements. Beyond the wall, the harsh volcanic landscape stretches to distant mountains. The gate is open during the day but sealed at night.",
        pl_min=3000, pl_max=10000)

    city_wall_south = make_room("City Wall - South Gate",
        "The southern entrance to the capital. This gate handles most cargo traffic, with long lines of transport vehicles waiting to enter. Inspection stations process goods while guards maintain order. The wall continues east and west into the distance.",
        pl_min=2000, pl_max=8000)

    wasteland_approach = make_room("Wasteland Approach",
        "The border between civilization and the deadly wasteland beyond. The air is thick with ash, and the ground is cracked and barren. Warning signs mark the boundary - beyond this point, survival is not guaranteed. Those seeking to prove themselves venture here.",
        pl_min=5000, pl_max=50000)

    ancient_ruins = make_room("Ancient Saiyan Ruins",
        "Remnants of the old Saiyan civilization, before the rise of the current empire. Crumbling structures hide among the rocks, their purposes forgotten. Treasure hunters and those seeking ancient secrets explore these ruins. Dangers lurk in every shadow.",
        pl_min=10000, pl_max=100000)

    # === OUTSKIRT FACILITIES ===

    spaceport = make_room("Royal Spaceport",
        "The primary hub for interplanetary travel. Ships of all sizes line the launch pads - from small scouts to massive battle carriers. Crews make final preparations for departure. A control tower coordinates the constant traffic of arrivals and departures.",
        pl_min=1000, pl_max=5000)

    scout_tower = make_room("Planetary Scanner Station",
        "A monitoring facility tracking all activity on and around the planet. Advanced sensors detect spacecraft from vast distances. Intelligence officers analyze the data, looking for threats or opportunities. The star system map fills one entire wall.",
        pl_min=5000, pl_max=25000)

    power_plant = make_room("Geothermal Power Station",
        "A massive facility tapping into the planet's volcanic energy. Pipes and conduits crisscross the structure, carrying molten rock to power conversion systems. The hum of generators is constant. This place powers the entire capital.",
        pl_min=3000, pl_max=15000)

    # === TRAINING ZONES ===

    gravity_room = make_room("High-Gravity Training Chamber",
        "A specialized facility for training under extreme gravity. The normal pull here is dozens of times planetary standard. Warriors struggle even to move, building incredible strength. Records of those who trained here and later became legends are displayed proudly.",
        pl_min=15000, pl_max=100000)

    spirit_room = make_room("Spirit Training Chamber",
        "A facility dedicated to developing non-physical combat abilities. Meditation rooms, ki-focusing chambers, and sensory deprivation tanks fill the space. Teachers here train warriors in techniques that go beyond simple physical power.",
        pl_min=20000, pl_max=150000)

    # === RESIDENTIAL ESTATES ===

    bardock_estate = make_room("House of Bardock",
        "The legendary residence of theero Bardock. Though he was considered a failure by the royal family, his legend grew with each impossible victory. The estate is modest but well-maintained. His son Training continues the legacy here.",
        pl_min=30000, pl_max=200000)

    # Apply zone tags
    zone_rooms = [
        # Outskirts
        outskirts_enter, trade_district_entrance, military_checkpoint,
        # Trade
        market_square, weapon_workshop, armor_dealer, food_stall_district, spice_merchant,
        # Residential
        residential_north, residential_south, noble_estate, warrior_barracks,
        # Entertainment
        fighting_pits_entrance, fighting_pit_main, fighting_pit_champions, bar_district, casino_entrance, casino_main,
        # Military
        military_headquarters, training_grounds, advanced_training, armory, medical_bay,
        # Palace
        palace_gates, outer_courtyard, throne_room_entrance, main_throne_room, throne_room_balcony, royal_gardens, treasury, royal_library,
        # Underground
        underground_entrance, underground_prison, secret_lab,
        # Periphery
        city_wall_north, city_wall_south, wasteland_approach, ancient_ruins,
        # Facilities
        spaceport, scout_tower, power_plant,
        # Training
        gravity_room, spirit_room,
        # Special
        bardock_estate
    ]
    
    for r in zone_rooms:
        r.tags.add("Planet Vegeta", category="zone")

    # Connect rooms - outskirts to trade
    link_rooms(outskirts_enter, "north", trade_district_entrance, "south")
    link_rooms(trade_district_entrance, "north", military_checkpoint, "south")
    link_rooms(military_checkpoint, "north", market_square, "south")

    # Connect trade district
    link_rooms(market_square, "east", weapon_workshop, "west")
    link_rooms(market_square, "west", armor_dealer, "east")
    link_rooms(market_square, "north", food_stall_district, "south")
    link_rooms(food_stall_district, "east", spice_merchant, "west")

    # Connect trade to residential
    link_rooms(market_square, "northwest", residential_north, "southeast")
    link_rooms(food_stall_district, "north", residential_south, "south")
    link_rooms(residential_north, "north", noble_estate, "south")
    link_rooms(residential_south, "east", warrior_barracks, "west")

    # Connect to entertainment
    link_rooms(military_checkpoint, "east", fighting_pits_entrance, "west")
    link_rooms(fighting_pits_entrance, "down", fighting_pit_main, "up")
    link_rooms(fighting_pit_main, "champion", fighting_pit_champions, "main")
    link_rooms(food_stall_district, "east", bar_district, "west")
    link_rooms(bar_district, "north", casino_entrance, "south")
    link_rooms(casino_entrance, "in", casino_main, "out")

    # Connect to military
    link_rooms(military_checkpoint, "north", military_headquarters, "south")
    link_rooms(military_headquarters, "east", training_grounds, "west")
    link_rooms(training_grounds, "up", advanced_training, "down")
    link_rooms(military_headquarters, "west", armory, "east")
    link_rooms(military_headquarters, "north", medical_bay, "south")

    # Connect to palace
    link_rooms(military_headquarters, "northwest", palace_gates, "southeast")
    link_rooms(palace_gates, "in", outer_courtyard, "out")
    link_rooms(outer_courtyard, "north", throne_room_entrance, "south")
    link_rooms(throne_room_entrance, "in", main_throne_room, "out")
    link_rooms(main_throne_room, "balcony", throne_room_balcony, "throne")
    link_rooms(outer_courtyard, "east", royal_gardens, "west")
    link_rooms(palace_gates, "east", treasury, "west")
    link_rooms(palace_gates, "west", royal_library, "east")

    # Connect to underground
    link_rooms(market_square, "down", underground_entrance, "up")
    link_rooms(underground_entrance, "prison", underground_prison, "entrance")
    link_rooms(underground_entrance, "secret", secret_lab, "entrance")

    # Connect to periphery
    link_rooms(military_checkpoint, "northwest", city_wall_north, "southeast")
    link_rooms(military_checkpoint, "south", city_wall_south, "north")
    link_rooms(city_wall_north, "north", wasteland_approach, "south")
    link_rooms(wasteland_approach, "north", ancient_ruins, "south")

    # Connect facilities
    link_rooms(outskirts_enter, "spaceport", spaceport, "outskirts")
    link_rooms(outskirts_enter, "tower", scout_tower, "outskirts")
    link_rooms(outskirts_enter, "plant", power_plant, "outskirts")

    # Connect training zones
    link_rooms(training_grounds, "gravity", gravity_room, "training")
    link_rooms(training_grounds, "spirit", spirit_room, "training")

    # Connect special
    link_rooms(residential_north, "bardock", bardock_estate, "residential")

    print("- Successfully generated Planet Vegeta - Royal Vegeta City! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point: {outskirts_enter.dbref} ({outskirts_enter.key})")
    print("Zones connected: Outskirts, Trade District, Residential, Entertainment, Military, Royal Palace, Underground, Periphery, Facilities, Training")

if __name__ == "__main__":
    create_planet_vegeta()
