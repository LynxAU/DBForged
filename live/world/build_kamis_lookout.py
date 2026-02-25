"""
Builder script to generate Kami's Lookout.
To execute:
    evennia run build_lookout
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_kamis_lookout():
    # Helper to create a room if it doesn't exist
    def make_room(key, desc, pl_min=0, pl_max=0):
        room = create_object(Room, key=key)
        room.db.desc = desc
        room.db.planet = "Kami's Lookout"
        room.db.climate = "otherworldly"
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

    print("Cleaning up old Kami's Lookout locations...")
    old_rooms = search_tag("Kami's Lookout", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Kami's Lookout...")

    # Main platform
    lookout_entrance = make_room("Kami's Lookout - Entrance",
        "You stand at the base of the immense cylindrical tower that houses Kami's Lookout. A simple door leads inside, but the true wonder is above - the lookout extends endlessly into the heavens. The air grows thin here, and you can see the curvature of Earth below.",
        pl_min=1000)

    main_platform = make_room("Kami's Lookout - Main Platform",
        "The primary gathering area of Kami's Lookout. The floor is polished white stone that seems to glow with inner light. A large fountain bubbles quietly in the center, its water somehow defying gravity as it flows upward before dissipating into mist. The sense of peace here is overwhelming.",
        pl_min=5000)

    # Interior rooms
    training_chamber = make_room("Training Chamber",
        "A dedicated space for martial arts training. The walls are reinforced with spiritual energy, capable of withstanding massive ki blasts. Training dummies line one wall, and a scoring system tracks progress. A young man with spiky hair seems to be pushing himself to the limit here.",
        pl_min=10000)

    sensory_room = make_room("Sensory Training Room",
        "A specialized chamber for developing sensory abilities. The walls are covered in ancient murals depicting the history of the Namekian race. The air hums with faint energy, enhancing concentration. This is where warriors learn to sense ki.",
        pl_min=5000)

    meditation_hall = make_room("Meditation Hall",
        "A serene space for mental and spiritual training. Cushions are arranged in precise rows, each imbued with calming energy. Incense burns softly, filling the air with a mystical fragrance. Through the windows, you can see the stars with impossible clarity.",
        pl_min=3000)

    # Tower areas
    upper_terrace = make_room("Upper Terrace",
        "A viewing platform higher up the lookout. The wind is stronger here, but the view is spectacular. You can see the entire planet spread out below, clouds swirling over oceans and continents. A lone figure meditates here, radiating calm power.",
        pl_min=10000)

    lookouts_top = make_room("Lookout - Summit",
        "The absolute top of Kami's Lookout. The platform extends into the stars themselves, as if you could reach out and touch the cosmos. A small shrine stands here, dedicated to the guardians of Earth. The sense of cosmic scale is humbling.",
        pl_min=50000)

    # Apply zone tags
    zone_rooms = [
        lookout_entrance, main_platform, training_chamber, 
        sensory_room, meditation_hall, upper_terrace, lookouts_top
    ]
    for r in zone_rooms:
        r.tags.add("Kami's Lookout", category="zone")

    # Connect rooms
    link_rooms(lookout_entrance, "up", main_platform, "down")
    link_rooms(main_platform, "north", training_chamber, "south")
    link_rooms(main_platform, "east", sensory_room, "west")
    link_rooms(main_platform, "west", meditation_hall, "east")
    link_rooms(main_platform, "up", upper_terrace, "down")
    link_rooms(upper_terrace, "up", lookouts_top, "down")

    print("- Successfully generated Kami's Lookout! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point: {lookout_entrance.dbref} ({lookout_entrance.key})")

if __name__ == "__main__":
    create_kamis_lookout()
