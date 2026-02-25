"""
Builder script to generate the Tournament Arena.
To execute:
    evennia run build_arena
from the live/ directory in shell, OR in-game as an admin user.
"""

from evennia import create_object, search_tag
from typeclasses.rooms import Room
from typeclasses.exits import Exit

def create_tournament_arena():
    # Helper to create a room if it doesn't exist
    def make_room(key, desc, pl_min=0, pl_max=0):
        room = create_object(Room, key=key)
        room.db.desc = desc
        room.db.planet = "Tournament Arena"
        room.db.climate = "controlled"
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

    print("Cleaning up old Tournament Arena locations...")
    old_rooms = search_tag("Tournament Arena", category="zone")
    for room in old_rooms:
        room.delete()

    print("Generating Tournament Arena...")

    # Entrance area
    arena_entrance = make_room("Tournament Arena - Entrance",
        "The grand entrance to the World Martial Arts Tournament venue. Ticket booths line the walls, and crowds of enthusiastic fans stream through the gates. Banners depicting past champions hang from the ceiling, inspiring new contenders.",
        pl_min=100)

    ticket_booth = make_room("Ticket Booth",
        "A small kiosk where fighters and spectators purchase entry passes. A bored-looking clerk sits behind the counter, stamping tickets with mechanical efficiency. Prices are posted: 50 zenies for preliminaries, 100 for the main event.",
        pl_min=100)

    waiting_area = make_room("Contestant Waiting Area",
        "A spacious green room where fighters prepare for their matches. Locker-style cubbies line the walls, each with a number. Coaches shout last-minute strategies, while nervous competitors stretch and warm up.",
        pl_min=1000)

    # Seating areas
    spectator_seats_lower = make_room("Arena - Lower Seating",
        "The cheaper seats offering a close view of the action. Fans pack tightly together, shouting encouragement and throwing debris when calls don't go their way. The energy is palpable, almost electric.",
        pl_min=100)

    spectator_seats_upper = make_room("Arena - Upper Seating",
        "Premium seating with an excellent bird's-eye view of the entire arena. Cushioned seats and decent sightlines justify the higher price. A concession stand nearby offers food and drinks.",
        pl_min=100)

    vip_box = make_room("VIP Box",
        "Exclusive boxes for wealthy spectators and special guests. Plush seating, complimentary refreshments, and perfect views of every corner of the arena. Bodyguards stand at attention by the entrance.",
        pl_min=10000)

    # The arena itself
    arena_floor = make_room("Tournament Arena - Fighting Floor",
        "The legendary fighting surface where countless battles have determined the fate of the world. The ring is a perfect circle, marked by white lines. Energy-absorbing material beneath the surface prevents serious injuries. The crowd roars as fighters step onto the sacred ground.",
        pl_min=1000)

    backstage = make_room("Backstage Area",
        "Behind the scenes of the tournament. Medical staff stand ready with recovery pods. Officials review match footage on holographic displays. Fighters who've been eliminated watch the remaining battles on monitors, analyzing their future opponents.",
        pl_min=1000)

    announcers_booth = make_room("Announcer's Booth",
        "High above the arena, this glass-walled room houses the broadcast team. Monitors display multiple camera angles. Microphones and equipment are arranged for the play-by-play commentary that fills the arena with hype.",
        pl_min=5000)

    # Apply zone tags
    zone_rooms = [
        arena_entrance, ticket_booth, waiting_area,
        spectator_seats_lower, spectator_seats_upper, vip_box,
        arena_floor, backstage, announcers_booth
    ]
    for r in zone_rooms:
        r.tags.add("Tournament Arena", category="zone")

    # Connect rooms
    link_rooms(arena_entrance, "north", arena_floor, "south")
    link_rooms(arena_entrance, "east", ticket_booth, "west")
    link_rooms(arena_entrance, "west", waiting_area, "east")
    link_rooms(arena_entrance, "up", spectator_seats_upper, "down")
    link_rooms(spectator_seats_lower, "up", spectator_seats_upper, "down")
    link_rooms(spectator_seats_upper, "east", vip_box, "west")
    link_rooms(arena_floor, "backstage", backstage, "arena")
    link_rooms(backstage, "up", announcers_booth, "down")

    print("- Successfully generated Tournament Arena! -")
    print(f"Created {len(zone_rooms)} rooms.")
    print(f"Starting point: {arena_entrance.dbref} ({arena_entrance.key})")

if __name__ == "__main__":
    create_tournament_arena()
