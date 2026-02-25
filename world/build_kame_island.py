"""
KAME ISLAND - Immersive New Player Experience
=============================================

A complete tutorial island featuring:
- Master Roshi's turtle training grounds
- Krillin, Android 18, and Marron on vacation
- Multiple exploration zones
- Interactive quests and dialogue
- Progressive difficulty training

"""

from evennia.objects.models import ObjectDB
from evennia.utils.create import create_object


def _get_room(key):
    return ObjectDB.objects.filter(db_key__iexact=key, db_typeclass_path="typeclasses.rooms.Room").first()


def _get_or_create_room(key, desc, zone=None, safe=False):
    room = _get_room(key)
    if room:
        room.db.desc = desc
        if zone:
            room.db.zone = zone
        if safe:
            room.db.safe_room = True
            room.tags.add("safe_room", category="zone")
        return room
    
    room = create_object("typeclasses.rooms.Room", key=key)
    room.db.desc = desc
    room.db.zone = zone or "Kame Island"
    if safe:
        room.db.safe_room = True
        room.tags.add("safe_room", category="zone")
    return room


def _create_exit(key, location, destination, aliases=None, desc=None):
    existing = ObjectDB.objects.filter(
        db_key__iexact=key, db_location=location, db_typeclass_path="typeclasses.exits.Exit"
    ).first()
    if existing:
        return existing
    
    exit_obj = create_object("typeclasses.exits.Exit", key=key, location=location, destination=destination)
    if aliases:
        for alias in aliases:
            exit_obj.aliases.add(alias)
    if desc:
        exit_obj.db.desc = desc
    return exit_obj


def _get_or_create_npc(key, typeclass, location, desc, attrs=None):
    npc = ObjectDB.objects.filter(db_key__iexact=key, db_typeclass_path=typeclass).first()
    if npc:
        npc.location = location
        npc.db.desc = desc
        if attrs:
            for attr_key, attr_value in attrs.items():
                setattr(npc.db, attr_key, attr_value)
        return npc
    
    npc = create_object(typeclass, key=key, location=location)
    npc.db.desc = desc
    if attrs:
        for attr_key, attr_value in attrs.items():
            setattr(npc.db, attr_key, attr_value)
    return npc


def build_kame_island():
    """
    Build the complete Kame Island experience.
    """
    
    # ═══════════════════════════════════════════════════════════════════════
    # KAME ISLAND MAP
    # ═══════════════════════════════════════════════════════════════════════
    
    # Main beach area
    kame_beach = _get_or_create_room(
        "Kame Island: Beach Shore",
        """Golden sand stretches along crystal-clear turquoise water. 
        
The iconic Turtle School flag flutters in the breeze atop a hill 
to the north. Palm trees sway lazily, and the sound of waves 
is incredibly peaceful.

This is where legendary fighters first learned to train!"""
    )
    
    # Roshi's house exterior
    kame_house_exterior = _get_or_create_room(
        "Kame House - Exterior",
        """A modest hut perched on a cliff overlooking the ocean.
        
A worn sign reads "TURTLE SCHOOL" in faded paint. The house 
itself is humble - just a roof and walls, but inside holds 
the wisdom of decades of martial arts champions.

A large turtle sunbathes lazily near the entrance."""
    )
    
    # Training grounds
    training_grounds = _get_or_create_room(
        "Kame Island: Training Grounds",
        """The famous Turtle School training area!
        
Dented and cracked training dummies stand in rows. Heavy 
stone weights are stacked in corners. A ring of flattened 
grass marks the sparring area where countless champions 
first learned to fight.

The energy here is thick with history - Gohan's father 
trained here. So did Goku!"""
    )
    
    # Forest path
    forest_path = _get_or_create_room(
        "Kame Island: Forest Path",
        """A shaded trail through tropical vegetation.
        
Exotic birds call from the canopy. The path winds between 
ancient trees, occasionally opening to sunny clearings.
        
A small clearing to the east looks like a meditation spot."""
    )
    
    # Meditation clearing
    meditation_spot = _get_or_create_room(
        "Kame Island: Meditation Clearing",
        """A peaceful clearing surrounded by flowering plants.
        
The air here feels different - calmer, more focused. A 
flat rock in the center has been worn smooth from years 
of use by practitioners seeking inner peace.

The ocean is visible through the trees to the south."""
    )
    
    # Dock area
    kame_dock = _get_or_create_room(
        "Kame Island: Small Dock",
        """A weathered wooden dock extending into clear water.
        
Colorful fish swim in the crystal waters. A small boat 
is tied to the dock, used for trips to the mainland.

The beach is back to the south."""
    )
    
    # Roshi's interior (main room)
    roshi_interior = _get_or_create_room(
        "Kame House - Main Room",
        """The interior of Master Roshi's humble home.
        
Sparsely furnished but cozy. A worn futon sits in the corner.
Bookshelves line the walls, filled with ancient martial arts 
texts and... questionable magazines.

A small kitchen area occupies one corner."""
    )
    
    # Back garden
    roshi_garden = _get_or_create_room(
        "Kame House - Garden",
        """A small cultivation garden behind the house.
        
Vegetable plants grow in orderly rows. Roshi may be lazy, 
but he grows his own food. A turtle browses on lettuce."""
    )
    
    # Cave (hidden training area)
    secret_cave = _get_or_create_room(
        "Kame Island: Hidden Cave",
        """A secluded cave behind the waterfall!
        
Water cascades down the entrance, creating a natural curtain.
Inside, the air is cool and still - perfect for serious 
training away from distractions.

This is where Master Roshi sends students for advanced training."""
    )
    
    # Waterfall
    waterfall_area = _get_or_create_room(
        "Kame Island: Waterfall",
        """A beautiful waterfall feeds into a crystal pool!
        
The water sparkles in the sunlight, creating rainbows in 
the mist. According to legend, this is where Master Roshi 
meditates when he needs to think.

A hidden path leads into the rocks behind the falls."""
    )
    
    # Vacation cottage (for Krillin/18/Marron)
    vacation_cottage = _get_or_create_room(
        "Kame Island: Vacation Cottage",
        """A cozy cottage nestled in a private grove.
        
This private retreat was set up for Android 18 and her family 
to vacation in peace. Krillin insisted on the location - 
"best training grounds I've ever seen!"
        
A small playground has been set up for Marron."""
    )
    
    # Cottage exterior
    cottage_exterior = _get_or_create_room(
        "Kame Island: Cottage Grounds",
        """A peaceful grove with a beautiful cottage.
        
The cottage has a warm, homey feel. Fresh flowers frame 
the entrance. A hammock stretches between two palm trees.

Android 18 can often be found reading here while Marron plays."""
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONNECT THE MAP WITH EXITS
    # ═══════════════════════════════════════════════════════════════════════
    
    # Beach connections
    _create_exit("north", kame_beach, kame_house_exterior, ["n", "up"], "A path leads up to Roshi's house.")
    _create_exit("east", kame_beach, kame_dock, ["e", "dock"], "A dock extends into the ocean.")
    _create_exit("south", kame_beach, training_grounds, ["s", "training"], "The training grounds are south.")
    
    # House connections
    _create_exit("south", kame_house_exterior, kame_beach, ["s", "down", "beach"], "Back to the beach.")
    _create_exit("enter", kame_house_exterior, roshi_interior, ["in", "house"], "The Turtle School headquarters.")
    _create_exit("behind", kame_house_exterior, roshi_garden, ["back", "garden"], "A small garden behind the house.")
    
    # Training grounds
    _create_exit("north", training_grounds, kame_beach, ["n", "beach"], "Back to the beach.")
    _create_exit("west", training_grounds, forest_path, ["w", "forest"], "A forest path leads west.")
    _create_exit("inside", training_grounds, roshi_interior, ["inside", "house"], "The main house.")
    
    # Forest
    _create_exit("east", forest_path, training_grounds, ["e", "back", "training"], "Back to training grounds.")
    _create_exit("meditate", forest_path, meditation_spot, ["meditation", "clearing"], "A peaceful meditation spot.")
    
    # Meditation
    _create_exit("out", meditation_spot, forest_path, ["out", "forest"], "Back to the forest path.")
    
    # Dock
    _create_exit("west", kame_dock, kame_beach, ["w", "beach"], "Back to the main beach.")
    
    # House interior
    _create_exit("out", roshi_interior, kame_house_exterior, ["out", "exit"], "Back outside.")
    _create_exit("garden", roshi_interior, roshi_garden, ["garden", "back"], "The cultivation garden.")
    
    # Garden
    _create_exit("house", roshi_garden, roshi_interior, ["house", "front"], "Back to the main room.")
    _create_exit("north", roshi_garden, waterfall_area, ["n", "waterfall"], "A beautiful waterfall!")
    
    # Waterfall
    _create_exit("south", waterfall_area, roshi_garden, ["s", "garden"], "Back to the garden.")
    _create_exit("enter", waterfall_area, secret_cave, ["cave", "hidden", "inside"], "A hidden cave behind the falls!")
    
    # Cave
    _create_exit("out", secret_cave, waterfall_area, ["out", "waterfall"], "Back to the waterfall.")
    
    # Vacation cottage
    _create_exit("north", kame_beach, cottage_exterior, ["n", "cottage", "vacation"], "A cozy cottage in the grove.")
    _create_exit("south", cottage_exterior, kame_beach, ["s", "beach"], "Back to the beach.")
    _create_exit("enter", cottage_exterior, vacation_cottage, ["enter", "inside", "cottage"], "The vacation cottage.")
    
    # Cottage interior
    _create_exit("out", vacation_cottage, cottage_exterior, ["out", "exit"], "Back outside.")
    
    # ═══════════════════════════════════════════════════════════════════════
    # NPCs - THE CAST OF KAME ISLAND
    # ═══════════════════════════════════════════════════════════════════════
    
    # Master Roshi - The legendary Turtle Hermit
    _get_or_create_npc(
        "Master Roshi",
        "typeclasses.npcs.TrainingNPC",
        roshi_interior,
        """The legendary Master Roshi, the Turtle Hermit!
        
A elderly man with an impressive mustache and sunglasses.
Despite his age, his muscles are still defined - a testament 
to decades of training. He carries an aura of incredible 
power despite his small stature.

He pretends to be lazy, but his eyes miss nothing."""
        ,
        attrs={
            "race": "human",
            "base_power": 180,
            "sprite_id": "Kame Island/master_roshi",
            "strength": 16,
            "speed": 12,
            "balance": 15,
            "mastery": 25,
            "ki_control": 20,
            "npc_role": "trainer",
            "trainer_key": "master_roshi",
            "npc_content_key": "master_roshi",
            "dialogue_options": [
                {"keyword": "training", "response": "Training? Hah! You think you're ready for that? First you gotta prove you can handle the basics!"},
                {"keyword": "kamehameha", "response": "The Kamehameha? Now THAT'S a technique! I invented it 50 years ago. But you haven't EARNED it yet, kid!"},
                {"keyword": "errand", "response": "Errands? Sure, I've got plenty! Go ask about 'quests' and I'll give you something to do. Consider it... character building!"},
                {"keyword": "quest", "response": "Ah, you want work? Good! I got plenty. The beach needs cleaning, the turtles need finding, the... wait, why are you smiling? This is WORK, not a reward!"},
                {"keyword": "work", "response": "Work? What do you think this is, a charity? You wanna learn from me? Then EARN it! Go ask about quests, rookie!"},
                {"keyword": "history", "response": "This island... I've trained here for 80 years. Goku, Gohan, Piccolo... they all started exactly where you are now. Doing MY chores!"},
                {"keyword": "vacation", "response": "Oh, Krillin and 18? They're on vacation. Good people. 18 could destroy this island if she wanted, heh. Unlike SOME people who just want free training..."},
            ]
        }
    )
    
    # Turtle
    _get_or_create_npc(
        "Old Turtle",
        "typeclasses.npcs.TrainingNPC",
        kame_house_exterior,
        """An ancient giant turtle.
        
This turtle has been Roshi's companion for over a century! 
It moves slowly but possesses surprising wisdom. Its shell 
is worn smooth from decades of carrying students on its back."""
        ,
        attrs={
            "race": "humanoid",
            "base_power": 50,
            "sprite_id": "Kame Island/umigame",
            "strength": 20,
            "speed": 2,
            "balance": 15,
            "mastery": 10,
            "ki_control": 5,
            "npc_role": "friendly",
        }
    )
    
    # Krillin
    _get_or_create_npc(
        "Krillin",
        "typeclasses.npcs.TrainingNPC",
        cottage_exterior,
        """The mighty Krillin!
        
Short, bald, and one of the strongest fighters on Earth! 
His bald head gleams in the sunlight. Despite his tough 
appearance, he's a loving family man on vacation.

He was once Goku's greatest rival, but these days he 
prefers relaxation to constant training."""
        ,
        attrs={
            "race": "human",
            "base_power": 250,
            "sprite_id": "Kame Island/krillin",
            "strength": 18,
            "speed": 20,
            "balance": 17,
            "mastery": 22,
            "ki_control": 25,
            "npc_role": "trainer",
            "trainer_key": "krillin",
            "npc_content_key": "krillin",
            "dialogue_options": [
                {"keyword": "vacation", "response": "Ah man, this place is SO good! The training grounds are amazing. 18 needed a break from city life, you know?"},
                {"keyword": "training", "response": "Training? I'm on vacation! ...Well, maybe just a little sparring. You look like you can handle yourself!"},
                {"keyword": "18", "response": "18? She's the best, man. Seriously. Could destroy me with one finger. That's why I married her!"},
                {"keyword": "goku", "response": "Goku? Haven't seen him in forever! That guy never stops training. But honestly? I'm happy just taking it easy."},
            ]
        }
    )
    
    # Android 18
    _get_or_create_npc(
        "Android 18",
        "typeclasses.npcs.TrainingNPC",
        vacation_cottage,
        """Android 18, the beautiful and deadly!
        
Her blonde hair catches the light as she reads a book. 
Despite being an android created by Dr. Gero, she has 
a warm personality - especially around her daughter.

She's incredibly powerful but chooses peace."""
        ,
        attrs={
            "race": "android",
            "base_power": 350,
            "sprite_id": "Kame Island/android_18",
            "strength": 20,
            "speed": 22,
            "balance": 18,
            "mastery": 20,
            "ki_control": 30,
            "npc_role": "trainer",
            "trainer_key": "android_18",
            "npc_content_key": "android_18",
            "dialogue_options": [
                {"keyword": "vacation", "response": "This island is peaceful. It's rare to find somewhere Krillin won't drag me into training."},
                {"keyword": "daughter", "response": "Marron? She's playing somewhere nearby. Such a sweet girl. I just want her to have a normal life."},
                {"keyword": "training", "response": "I don't need to train. My power is already... sufficient. But Krillin never learns."},
                {"keyword": "power", "response": "My power? Let's just say I'm glad I'm on vacation. Androids don't need to prove ourselves."},
            ]
        }
    )
    
    # Marron
    _get_or_create_npc(
        "Marron",
        "typeclasses.npcs.TrainingNPC",
        cottage_exterior,
        """Marron, Krillin and Android 18's daughter!
        
A cheerful young girl with her mother's looks and her 
father's... enthusiasm. She's playing happily, completely 
oblivious to the incredible power her parents possess.

She represents the peaceful future her parents fought for."""
        ,
        attrs={
            "race": "human",
            "base_power": 10,
            "sprite_id": "Kame Island/marron",
            "strength": 5,
            "speed": 8,
            "balance": 6,
            "mastery": 1,
            "ki_control": 1,
            "npc_role": "friendly",
            "dialogue_options": [
                {"keyword": "play", "response": "Wanna play? Daddy says I'm gonna be a super strong fighter like him and Mommy!"},
                {"keyword": "mom", "response": "Mommy is the prettiest! And she can do ANYTHING!"},
                {"keyword": "dad", "response": "Daddy makes funny faces when he trains! He gets all sweaty!"},
            ]
        }
    )
    
    # Training Dummy (for practice)
    _get_or_create_npc(
        "Training Dummy MK-1",
        "typeclasses.npcs.HostileNPC",
        training_grounds,
        """A worn training dummy for beginners.
        
Covered in dents and scorch marks from generations of 
new fighters learning the basics. It's sturdy enough 
to take a beating but won't fight back - perfect for 
learning technique!"""
        ,
        attrs={
            "race": "android",
            "base_power": 45,
            "sprite_id": "npc_training_dummy",
            "strength": 6,
            "speed": 3,
            "balance": 5,
            "mastery": 0,
            "ki_control": 0,
            "npc_role": "sparring",
            "aggressive": False,
        }
    )
    
    # Stronger training dummy
    _get_or_create_npc(
        "Training Dummy MK-2",
        "typeclasses.npcs.HostileNPC",
        training_grounds,
        """An upgraded training dummy for intermediate fighters.
        
More damage than the MK-1, this dummy can actually put 
up a bit of a fight! Students who've mastered the basics 
use this for sparring practice."""
        ,
        attrs={
            "race": "android",
            "base_power": 95,
            "sprite_id": "npc_training_dummy_mk2",
            "strength": 12,
            "speed": 8,
            "balance": 10,
            "mastery": 5,
            "ki_control": 5,
            "npc_role": "sparring",
            "aggressive": False,
        }
    )
    
    # Wild animal - Monkey
    _get_or_create_npc(
        "Wild Monkey",
        "typeclasses.npcs.HostileNPC",
        forest_path,
        """A wild monkey from the island forest.
        
It looks aggressive! It's baring its teeth and seems 
territorial. Probably used to having this forest to itself."""
        ,
        attrs={
            "race": "humanoid",
            "base_power": 35,
            "sprite_id": "npc_monkey",
            "strength": 8,
            "speed": 12,
            "balance": 8,
            "mastery": 2,
            "ki_control": 1,
            "npc_role": "hostile",
            "aggressive": True,
        }
    )
    
    # Wild animal - Boar
    _get_or_create_npc(
        "Wild Boar",
        "typeclasses.npcs.HostileNPC",
        forest_path,
        """A wild boar with sharp tusks!
        
It's rooting through the undergrowth, tusks glinting 
in the filtered sunlight. Not as fast as the monkey, 
but packs a punch with those tusks!"""
        ,
        attrs={
            "race": "humanoid",
            "base_power": 55,
            "sprite_id": "npc_boar",
            "strength": 14,
            "speed": 6,
            "balance": 10,
            "mastery": 2,
            "ki_control": 1,
            "npc_role": "hostile",
            "aggressive": True,
        }
    )
    
    return {
        "beach": kame_beach,
        "training_grounds": training_grounds,
        "roshi": roshi_interior,
        "cottage": vacation_cottage,
    }


def get_kame_island_start():
    """Return the starting room for Kame Island."""
    rooms = build_kame_island()
    return rooms.get("beach")
