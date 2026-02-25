"""
Builder script to generate Kame Island and Kame House.
To execute:
    evennia run build_kame
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_kame_island():
    # Helper to create a room if it doesn't exist by finding an existing one by key
    def make_room(key, desc):
        room = create_object(Room, key=key)
        room.db.desc = desc
        return room

    # Helper to link two rooms bidirectionally
    def link_rooms(room1, dir1, room2, dir2):
        if not room1 or not room2: return
        abbr = {"north": "n", "south": "s", "east": "e", "west": "w", "northeast": "ne", 
                "northwest": "nw", "southeast": "se", "southwest": "sw", "up": "u", "down": "d"}
        
        a1 = [abbr[dir1]] if dir1 in abbr else []
        a2 = [abbr[dir2]] if dir2 in abbr else []
        
        create_object(Exit, key=dir1, aliases=a1, location=room1, destination=room2)
        create_object(Exit, key=dir2, aliases=a2, location=room2, destination=room1)

    print("Cleaning up old Kame Island locations...")
    old_rooms = search_tag("Kame Island", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Kame Island...")

    # Create Interiors
    porch = make_room("Kame House - Front Porch", 
        "A brief wooden porch leading up to the iconic pink-walled, red-roofed Kame House. A comfortable deck chair rests here, often occupied by the Turtle Hermit. Sand lines the edges of the steps, giving way to the brilliant blue ocean just steps away.")
    
    living_room = make_room("Kame House - Living Room",
        "The cozy common area of Kame House. A soft couch sits in front of an old box television alongside a low wooden table. Fitness videos typically play on repeat. Shelves packed with eclectic knick-knacks and an absurd number of questionable magazines cover the walls. A small wooden staircase twists up to the bedroom.")

    kitchen = make_room("Kame House - Kitchen",
        "A surprisingly functional kitchen tucked into the back of Kame House. The small counter is perpetually messy, covered with instant ramen cups and milk bottles. A white refrigerator hums quietly in the corner, heavily stocked with frosty beer for the old man.")

    bathroom = make_room("Kame House - Bathroom",
        "A utilitarian cramped washroom containing a shower and toilet. It seems clean enough, though a suspicious pile of reading material sits precariously close to the commode.")

    bedroom = make_room("Kame House - Upstairs Bedroom",
        "The small, crowded sleeping quarters occupying the upper dome of Kame House. Several single beds are squeezed tightly together, offering rest for whichever martial arts students happen to be lingering. A rounded window offers a spectacular, unobstructed view of the seemingly endless ocean.")

    # Create Beach
    beach_south = make_room("KameIsland - Southern Beach",
        "The primary stretch of sandy shore at the front of the island. Hermit crabs scuttle across the golden sand, and gentle waves calmly break against the shoreline. Kame House stands boldly to the north.")

    beach_north = make_room("KameIsland - Rear Beach",
        "The secluded backside of Kame Island. The ocean breeze feels a bit cooler here, shaded by the mass of the house. A few pieces of driftwood litter the pristine white sand.")

    beach_east = make_room("KameIsland - Eastern Shore",
        "The right flank of the tiny island piece. A lone, curved palm tree provides a small patch of shade. It's a perfect spot to watch the sun rise over the endless sea.")

    beach_west = make_room("KameIsland - Western Shore",
        "The left side of the island. Seaweed washes up occasionally on the pristine sand here. You can see the curving walls of the pink house to your right.")

    # Create surrounding ocean
    ocean_n = make_room("The Endless Ocean", "You are treading water in the vast, shimmering blue southern sea. The water is pleasantly warm. Kame Island sits to the south.")
    ocean_s = make_room("The Endless Ocean", "You are treading water in the vast, shimmering blue southern sea. The water is pleasantly warm. Kame Island sits to the north.")
    ocean_e = make_room("The Endless Ocean", "You are treading water in the vast, shimmering blue southern sea. The water is pleasantly warm. Kame Island sits to the west.")
    ocean_w = make_room("The Endless Ocean", "You are treading water in the vast, shimmering blue southern sea. The water is pleasantly warm. Kame Island sits to the east.")

    # Apply some basic tags to identify the zone
    zone_rooms = [porch, living_room, kitchen, bathroom, bedroom, beach_south, beach_north, beach_east, beach_west, ocean_n, ocean_s, ocean_e, ocean_w]
    for r in zone_rooms:
        r.tags.add("Kame Island", category="zone")

    # Connect interiors
    link_rooms(porch, "north", living_room, "south")
    link_rooms(living_room, "north", kitchen, "south")
    link_rooms(living_room, "west", bathroom, "east")
    link_rooms(living_room, "up", bedroom, "down")

    # Connect house to beach
    link_rooms(beach_south, "north", porch, "south")
    
    # Connect beach rim
    link_rooms(beach_south, "east", beach_east, "southwest")
    link_rooms(beach_south, "west", beach_west, "southeast")
    link_rooms(beach_north, "east", beach_east, "northwest")
    link_rooms(beach_north, "west", beach_west, "northeast")

    # Connect beach to ocean
    link_rooms(beach_north, "north", ocean_n, "south")
    link_rooms(beach_south, "south", ocean_s, "north")
    link_rooms(beach_east, "east", ocean_e, "west")
    link_rooms(beach_west, "west", ocean_w, "east")

    print("- Successfully generated Kame Island layout! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point of island is: {beach_south.dbref} ({beach_south.key})")

if __name__ == "__main__":
    create_kame_island()
