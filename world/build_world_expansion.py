"""
Builder script to generate additional world areas:
- Capsule Corp (West City)
- King Kai's Planet
- Mount Paozu
- Red Ribbon Army HQ

To execute:
    evennia run build_world_expansion
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit


def make_room(key, desc, zone=None):
    """Helper to create a room."""
    room = create_object(Room, key=key)
    room.db.desc = desc
    if zone:
        room.tags.add(zone, category="zone")
    return room


def link_rooms(room1, dir1, room2, dir2):
    """Helper to link two rooms bidirectionally."""
    if not room1 or not room2:
        return
    abbr = {"north": "n", "south": "s", "east": "e", "west": "w", 
            "northeast": "ne", "northwest": "nw", "southeast": "se", 
            "southwest": "sw", "up": "u", "down": "d"}
    
    a1 = [abbr[dir1]] if dir1 in abbr else []
    a2 = [abbr[dir2]] if dir2 in abbr else []
    
    create_object(Exit, key=dir1, aliases=a1, location=room1, destination=room2)
    create_object(Exit, key=dir2, aliases=a2, location=room2, destination=room1)


def create_capsule_corp():
    """Build Capsule Corp in West City."""
    print("Generating Capsule Corp...")
    
    # Main building
    entrance = make_room(
        "Capsule Corp - Main Entrance",
        "The grand entrance of Capsule Corporation. The lobby features sleek modern design with chrome accents. A reception desk sits near the entrance with a holographic display showing company news. The famous Capsule Corp logo glows softly above the doors.",
        zone="Capsule Corp"
    )
    
    lab = make_room(
        "Capsule Corp - Research Lab",
        "A high-tech laboratory filled with holographic displays and prototype capsules. Workbenches line the walls covered in schematics for various inventions. ATime Machine blueprint can be faintly seen on one of the screens.",
        zone="Capsule Corp"
    )
    
    training_hall = make_room(
        "Capsule Corp - Training Hall",
        "A massive underground training facility. The walls are reinforced and covered in impact padding. Gravity training machines line one wall, capable of adjusting up to 100x gravity. Sparring drones float in standby mode.",
        zone="Capsule Corp"
    )
    
    roof = make_room(
        "Capsule Corp - Rooftop",
        "A helipad and observation deck on top of the main building. The city of West City spreads out below. A few capsule cars zoom past on the streets far below. The sunset reflects off the glass towers.",
        zone="Capsule Corp"
    )
    
    # Link rooms
    link_rooms(entrance, "north", lab, "south")
    link_rooms(entrance, "east", training_hall, "west")
    link_rooms(entrance, "up", roof, "down")
    
    return entrance


def create_king_kai_planet():
    """Build King Kai's Planet (North Kai)."""
    print("Generating King Kai's Planet...")
    
    # The planet is tiny - just a small floating platform
    main = make_room(
        "King Kai's Planet",
        "A tiny rectangular planet in the afterlife. The grass is vibrant green and the sky is a cheerful blue despite being in the afterlife. A modest pagoda sits nearby where King Kai trains souls. A small house with the Neko Cafe sign is here too! Bubbles the dog lounges nearby.",
        zone="North Kai"
    )
    
    training_grounds = make_room(
        "King Kai's Training Grounds",
        "A simple dirt field where fighters train in the afterlife. Training dummies made of hay stand in a row. A large boulder with \"Push\" carved into it sits nearby - tests of strength for aspiring warriors.",
        zone="North Kai"
    )
    
    link_rooms(main, "north", training_grounds, "south")
    
    return main


def create_mount_paozu():
    """Build Mount Paozu - Goku's childhood home."""
    print("Generating Mount Paozu...")
    
    # Mountain base
    forest_path = make_room(
        "Mount Paozu - Forest Path",
        "A winding dirt path through the dense forest of Mount Paozu. Tall trees block much of the sunlight. The air is fresh and clean. You can hear birds singing in the distance. A small stream crosses the path.",
        zone="Mount Paozu"
    )
    
    # The mountain itself
    base_camp = make_room(
        "Mount Paozu - Base Camp",
        "A small clearing at the base of the mountain. Old training equipment is scattered around - log benches, rope swings, and stone weights. This is where Goku trained as a child. A steep trail leads up the mountain.",
        zone="Mount Paozu"
    )
    
    # Goku's house
    house_exterior = make_room(
        "Goku's House - Exterior",
        "A modest wooden house nestled in the mountains. The classic Kame House symbol is painted on the side, though this is clearly a different structure. A vegetable garden grows beside the house. Mount Paozu towers above.",
        zone="Mount Paozu"
    )
    
    house_interior = make_room(
        "Goku's House - Interior",
        "A simple but comfortable living space. A worn couch sits in front of a small TV. The kitchen area has basic supplies. Stairs lead up to the bedroom. Family photos line the walls - Goku, Chi-Chi, and their children.",
        zone="Mount Paozu"
    )
    
    # Spirit Bomb training spot
    cliff_edge = make_room(
        "Mount Paozu - Spirit Bomb Cliff",
        "A dramatic cliff overlooking a vast valley. This is where Goku learned the Spirit Bomb technique. The energy is different here - raw and wild. On clear days you can see the entire valley below.",
        zone="Mount Paozu"
    )
    
    # Link rooms
    link_rooms(forest_path, "north", base_camp, "south")
    link_rooms(base_camp, "east", house_exterior, "west")
    link_rooms(house_exterior, "in", house_interior, "out")
    link_rooms(base_camp, "up", cliff_edge, "down")
    
    return forest_path


def create_red_ribbon_army():
    """Build Red Ribbon Army HQ."""
    print("Generating Red Ribbon Army HQ...")
    
    # Entrance
    gate = make_room(
        "Red Ribbon Army - Main Gate",
        "The imposing front gate of the Red Ribbon Army headquarters. Red banners with the army's emblem flutter in the wind. Armed soldiers stand guard at the entrance. The building looms ahead, a stark contrast to the surrounding landscape.",
        zone="Red Ribbon Army"
    )
    
    lobby = make_room(
        "Red Ribbon Army - Main Lobby",
        "A militaristic lobby with red and black decor. Maps of conquered territories line the walls. Soldiers march briskly through the halls. An elevator and stairs lead deeper into the complex.",
        zone="Red Ribbon Army"
    )
    
    # Army storage
    armory = make_room(
        "Red Ribbon Army - Armory",
        "Racks of weapons line the walls - blasters, grenades, and more exotic experimental weapons. A prototype Super Mega Death Ball sits in a secure container. The shelves are well-organized despite the chaotic nature of the army.",
        zone="Red Ribbon Army"
    )
    
    # Secret lab (Android creation)
    lab = make_room(
        "Red Ribbon Army - Secret Laboratory",
        "A hidden laboratory deep in the facility. Bio- pods contain incomplete Android prototypes. The smell of ozone and machinery fills the air. Tubes and wires create a maze of technology. This is where Dr. Gero conducted his experiments.",
        zone="Red Ribbon Army"
    )
    
    # Commander's office
    office = make_room(
        "Red Ribbon Army - Commander's Office",
        "A luxurious office for the army's commander. A large desk dominates the room. Holographic displays show troop movements and strategic maps. A portrait of the army's founder hangs on the wall.",
        zone="Red Ribbon Army"
    )
    
    # Linking
    link_rooms(gate, "north", lobby, "south")
    link_rooms(lobby, "east", armory, "west")
    link_rooms(lobby, "down", lab, "up")
    link_rooms(lobby, "north", office, "south")
    
    return gate


def create_all_areas():
    """Generate all new world areas."""
    print("=== Building World Expansion ===")
    
    capsule_corp = create_capsule_corp()
    king_kai = create_king_kai_planet()
    mount_paozu = create_mount_paozu()
    red_ribbon = create_red_ribbon_army()
    
    print("\n=== World Expansion Complete! ===")
    print(f"Capsule Corp: {capsule_corp}")
    print(f"King Kai's Planet: {king_kai}")
    print(f"Mount Paozu: {mount_paozu}")
    print(f"Red Ribbon Army: {red_ribbon}")


if __name__ == "__main__":
    create_all_areas()
