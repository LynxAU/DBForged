"""
Builder script to generate Beerus's Planet (Planet 703).
To execute:
    evennia run build_beerus
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_beerus_planet():
    # Helper to create a room if it doesn't exist
    def make_room(key, desc, pl_min=0, pl_max=0):
        room = create_object(Room, key=key)
        room.db.desc = desc
        room.db.planet = "Beerus's Planet"
        room.db.climate = "varied"
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

    print("Cleaning up old Beerus's Planet locations...")
    old_rooms = search_tag("Beerus's Planet", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Beerus's Planet...")

    # Main palace area
    palace_entrance = make_room("Beerus's Palace - Grand Entrance",
        "The breathtaking entrance to the God of Destruction's residence. Crystalline pillars stretch toward an impossibly high ceiling, glowing with soft divine energy. The floor is polished marble that reflects the ethereal light. Massive doors loom to the north, leading deeper into the palace.",
        pl_min=50000000)

    grand_hall = make_room("Beerus's Palace - Grand Hall",
        "A magnificent hall worthy of a God of Destruction. Velvet cushions are arranged around a low table, perfect for lounging. Golden ornaments adorn the walls, and the ceiling features a mural depicting the宇宙's creation and destruction. A soft hum of cosmic energy fills the air.",
        pl_min=50000000)

    throne_room = make_room("Beerus's Palace - Throne Room",
        "The private throne room of Lord Beerus. A raised platform holds an elegant throne made from condensed starlight. The walls are adorned with memorabilia from across the universe - proof of Beerus's title as Destroyer. Whis stands quietly in the corner, awaiting orders.",
        pl_min=100000000)

    # Sleeping quarters
    beerus_bedroom = make_room("Beerus's Private Quarters",
        "The personal chambers of the God of Destruction. A massive, cushioned bed dominates the room - perfect for a cat deity's naps. Scratching posts stand in the corner, and dish bowls are filled with the finest fish. Moonlight streams through the window.",
        pl_min=50000000)

    guest_quarters = make_room("Guest Accommodations",
        "Luxurious quarters for honored guests. The room features adaptive lighting and temperature controls. A replicator provides any food or drink desired. The bed is impossibly comfortable, conforming to the sleeper's exact preferences.",
        pl_min=1000000)

    # Dining area
    dining_hall = make_room("Palace Dining Hall",
        "A grand dining area capable of hosting cosmic-level banquets. The table can extend to accommodate many guests. Fresh supplies are magically replenished daily. The finest cuisines from across the universe are available.",
        pl_min=50000000)

    # Training areas
    training_chamber = make_room("Divine Training Chamber",
        "A specially constructed area for combat training. The walls are reinforced with destruction energy, capable of withstanding attacks that could shatter planets. Training dummies made of condensed starlight stand ready. Warning signs in cosmic script line the walls.",
        pl_min=100000000)

    meditation_garden = make_room("Cosmic Meditation Garden",
        "A serene garden where the laws of physics bend to create impossible beauty. Floating koi ponds, upside-down waterfalls, and plants from extinct planets create an atmosphere of profound peace. A stone bench offers a perfect spot for contemplation.",
        pl_min=50000000)

    # Outdoor areas
    palace_terrace = make_room("Palace Terrace",
        "A sweeping terrace offering views of the planet's unique landscape. The ground is soft, cloud-like material that absorbs impact. In the distance, destruction craters serve as reminders of Beerus's power. The sky shifts through impossible colors.",
        pl_min=50000000)

    planetary_edge = make_room("Edge of Existence",
        "The literal edge of Beerus's planet, where reality becomes thin. Looking over the edge, you see the vast cosmic void. Stars glitter in the eternal darkness. The ground feels unstable here, resonating with destructive energy.",
        pl_min=200000000)

    # Apply zone tags
    zone_rooms = [
        palace_entrance, grand_hall, throne_room, beerus_bedroom, 
        guest_quarters, dining_hall, training_chamber, meditation_garden,
        palace_terrace, planetary_edge
    ]
    for r in zone_rooms:
        r.tags.add("Beerus's Planet", category="zone")

    # Connect rooms
    link_rooms(palace_entrance, "north", grand_hall, "south")
    link_rooms(grand_hall, "north", throne_room, "south")
    link_rooms(grand_hall, "east", dining_hall, "west")
    link_rooms(grand_hall, "west", guest_quarters, "east")
    link_rooms(grand_hall, "up", beerus_bedroom, "down")
    link_rooms(throne_room, "east", training_chamber, "west")
    link_rooms(throne_room, "west", meditation_garden, "east")
    link_rooms(palace_entrance, "out", palace_terrace, "in")
    link_rooms(palace_terrace, "forward", planetary_edge, "back")

    print("- Successfully generated Beerus's Planet! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point: {palace_entrance.dbref} ({palace_entrance.key})")

if __name__ == "__main__":
    create_beerus_planet()
