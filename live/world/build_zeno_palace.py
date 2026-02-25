"""
Builder script to generate Zeno's Palace (The Omni-King's Realm).
To execute:
    evennia run build_zeno
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_zeno_palace():
    # Helper to create a room if it doesn't exist
    def make_room(key, desc, pl_min=0, pl_max=0):
        room = create_object(Room, key=key)
        room.db.desc = desc
        room.db.planet = "Zeno's Palace"
        room.db.climate = "celestial"
        if pl_min:
            room.db.power_level_min = pl_min
        if pl_max:
            room.db.power_level_max = pl_max
        return room

    # Helper to link two rooms bidirectionally
    def link_rooms(room1, dir1, room2, dir2):
        if not room1 or not room2: return
        abbr = {"north": "n", "south": "s", "east": "e", "west": "w", 
                "northeast": "ne", "northwest": "nw", "southeast": "se", 
                "southwest": "sw", "up": "u", "down": "d"}
        
        a1 = [abbr[dir1]] if dir1 in abbr else []
        a2 = [abbr[dir2]] if dir2 in abbr else []
        
        create_object(Exit, key=dir1, aliases=a1, location=room1, destination=room2)
        create_object(Exit, key=dir2, aliases=a2, location=room2, destination=room1)

    print("Cleaning up old Zeno's Palace locations...")
    old_rooms = search_tag("Zeno's Palace", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Zeno's Palace...")

    # The void before palace
    entrance_void = make_room("The Grand Zeno's Arena - Approach",
        "You float in an infinite void of pure white. Before you stretches an impossible structure - Zeno's Palace, the seat of the Omni-King. The very fabric of reality seems to bend around it. Even the greatest gods approach with trepidation.",
        pl_min=1000000000)

    palace_gates = make_room("Palace Gates",
        "Massive gates made of crystallized time stand before you. They pulse with a soft golden light, and looking at them too long makes your mind reel. Guards from all twelve universes stand watch, but even they look nervous.",
        pl_min=500000000)

    # The palace
    grand_foyer = make_room("Zeno's Palace - Grand Foyer",
        "The entrance to the Omni-King's home. The architecture defies physics - rooms exist in more dimensions than three. Soft music plays from nowhere and everywhere. Attendants in pristine white bow as you enter.",
        pl_min=1000000000)

    throne_ante = make_room("Antechamber",
        "A waiting room fit for gods. Comfortable seats made of compressed starlight are arranged casually. Other deities wait here - some nervously, some with practiced calm. A large monitor shows various universes.",
        pl_min=500000000)

    # The throne room
    zeno_throne = make_room("Zeno's Throne Room",
        "The most important room in all of existence. A massive chamber of pure white gold, with floating platforms at various heights. In the center sits a simple but elegant throne, and upon it... the Omni-Kind himself. Small, pink, and radiating absolute power. The Future Zeno stands nearby.",
        pl_min=1000000000)

    # Gardens (impossible gardens)
    garden_of_time = make_room("Garden of Time",
        "A serene garden where flowers bloom in the past, present, and future simultaneously. Some trees show autumn leaves while others display spring buds. Time flows differently here - you could spend centuries here and return to find only moments have passed.",
        pl_min=500000000)

    garden_of_space = make_room("Garden of Space",
        "An endless meadow that folds in on itself. Walking forward might take you to another universe entirely. Constellations float at knee height, and you can reach out and touch distant galaxies. The boundaries between spaces are merely suggestions.",
        pl_min=500000000)

    # Entertainment areas
    playroom = make_room("Zeno's Playroom",
        "A vast chamber filled with toys and games from across the multiverse. A massive ball pit contains balls from different dimensions. Video game consoles from a thousand worlds line one wall. This is where Zeno comes to relax.",
        pl_min=500000000)

    observation_deck = make_room("Observation Deck",
        "A chamber with windows that look out on all of existence. You can see every universe, every timeline, every possibility. Gods and angels use this room to check on their domains. The scale is both beautiful and terrifying.",
        pl_min=500000000)

    # Guest quarters
    divine_suite = make_room("Divine Guest Suite",
        "Luxury accommodations for visiting deities. The room reshapes itself based on your preferences - what feels comfortable to a god of destruction would be incomprehensible to a mortal. Fine foods and drinks materialize on command.",
        pl_min=100000000)

    # Apply zone tags
    zone_rooms = [
        entrance_void, palace_gates, grand_foyer, throne_ante, zeno_throne,
        garden_of_time, garden_of_space, playroom, observation_deck, divine_suite
    ]
    for r in zone_rooms:
        r.tags.add("Zeno's Palace", category="zone")

    # Connect rooms
    link_rooms(entrance_void, "forward", palace_gates, "back")
    link_rooms(palace_gates, "north", grand_foyer, "south")
    link_rooms(grand_foyer, "east", garden_of_space, "west")
    link_rooms(grand_foyer, "west", garden_of_time, "east")
    link_rooms(grand_foyer, "north", throne_ante, "south")
    link_rooms(throne_ante, "forward", zeno_throne, "back")
    link_rooms(grand_foyer, "up", observation_deck, "down")
    link_rooms(grand_foyer, "playroom", playroom, "grand_foyer")
    link_rooms(grand_foyer, "guest_suite", divine_suite, "grand_foyer")

    print("- Successfully generated Zeno's Palace! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point: {entrance_void.dbref} ({entrance_void.key})")

if __name__ == "__main__":
    create_zeno_palace()
