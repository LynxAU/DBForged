"""
Planet Cracker & Training Systems - DBForged Bible Implementation
===============================================================
"""

import random
import time


# =============================================================================
# PLANET CRACKER TECHNIQUE
# =============================================================================


def can_use_planet_cracker(character):
    """
    Check if character can use Planet Cracker.
    Requires 1M+ PL and 10% learn chance.
    """
    pl = character.db.power_level or 0
    if pl < 1000000:
        return False, "You need at least 1,000,000 PL to use Planet Cracker."
    
    # Check once-per-day limit
    last_use = getattr(character.db, 'planet_cracker_last_use', None)
    if last_use:
        import time
        if time.time() - last_use < 86400:  # 24 hours
            return False, "You can only use Planet Cracker once per day."
    
    return True, None


def use_planet_cracker(character, target_room=None):
    """
    Use Planet Cracker technique.
    10% learn chance - if miss, 1 hour exhaustion penalty.
    """
    can_use, error = can_use_planet_cracker(character)
    if not can_use:
        return False, error
    
    # 10% chance to successfully use
    if random.random() < 0.10:
        # Success!
        import time
        character.db.planet_cracker_last_use = time.time()
        
        # Calculate damage (based on PL)
        pl = character.db.power_level or 100
        damage = int(pl * 2)  # Massive damage
        
        return True, {
            'success': True,
            'damage': damage,
            'room': target_room,
            'message': f"You unleash PLANET CRACKER! A massive energy beam destroys everything in the area for {damage} damage!"
        }
    else:
        # Miss - exhaustion penalty
        import time
        character.db.planet_cracker_last_use = time.time()
        character.db.exhausted_until = time.time() + 3600  # 1 hour
        
        return True, {
            'success': False,
            'damage': 0,
            'room': None,
            'message': "You fail to properly channel Planet Cracker! Your body is exhausted for 1 hour."
        }


# =============================================================================
# TRAINER SYSTEM
# =============================================================================


# Trainer definitions
TRAINERS = {
    "roshi": {
        "name": "Master Roshi",
        "location": "Kame House",
        "xp_bonus": 1.5,
        "specialty": "Basic combat training",
        "prereq_pl": 0,
    },
    "kingkai": {
        "name": "King Kai",
        "location": "King Kai's Planet",
        "xp_bonus": 2.0,
        "specialty": "Spirit training & kaio ken",
        "prereq_pl": 50000,
    },
    "guru": {
        "name": "Guru",
        "location": "Namek",
        "xp_bonus": 1.8,
        "specialty": "Potential unlocking",
        "prereq_pl": 10000,
    },
    "whis": {
        "name": "Whis",
        "location": "Beerus's Planet",
        "xp_bonus": 3.0,
        "specialty": "Ultra instinct training",
        "prereq_pl": 500000,
    },
    "frieza": {
        "name": "Lord Frieza",
        "location": "Frieza's Ship",
        "xp_bonus": 2.5,
        "specialty": "Ruthless combat",
        "prereq_pl": 100000,
    },
}


def train_with_npc(character, trainer_id):
    """
    Train with a specific NPC trainer.
    Returns XP bonus and starts training session.
    """
    trainer = TRAINERS.get(trainer_id.lower())
    if not trainer:
        return False, "Unknown trainer. Available: Roshi, King Kai, Guru, Whis, Frieza"
    
    pl = character.db.power_level or 0
    if pl < trainer['prereq_pl']:
        return False, f"You need at least {trainer['prereq_pl']:,} PL to train with {trainer['name']}."
    
    # Calculate training bonus
    xp_bonus = trainer['xp_bonus']
    
    # Generate training XP based on PL
    base_xp = int(pl * 0.1)
    bonus_xp = int(base_xp * (xp_bonus - 1))
    
    # Apply XP
    current_xp = getattr(character.db, 'xp', 0)
    character.db.xp = current_xp + base_xp + bonus_xp
    
    return True, f"You train with {trainer['name']}! +{base_xp + bonus_xp} XP ({xp_bonus}x bonus)."


def get_available_trainers(character):
    """Get list of trainers available to the character."""
    pl = character.db.power_level or 0
    available = []
    
    for trainer_id, trainer in TRAINERS.items():
        if pl >= trainer['prereq_pl']:
            available.append({
                'id': trainer_id,
                'name': trainer['name'],
                'location': trainer['location'],
                'bonus': trainer['xp_bonus'],
                'specialty': trainer['specialty'],
            })
    
    return available


def learn_technique_from_trainer(character, trainer_id, technique_name):
    """
    Learn a specific technique from a trainer.
    """
    trainer = TRAINERS.get(trainer_id.lower())
    if not trainer:
        return False, "Unknown trainer."
    
    # Check PL requirement
    pl = character.db.power_level or 0
    if pl < trainer['prereq_pl']:
        return False, f"You need more PL to learn from {trainer['name']}."
    
    # Check if character has the technique
    known_techs = getattr(character.db, 'techniques_known', [])
    if technique_name in known_techs:
        return False, f"You already know {technique_name}."
    
    # Add technique
    known_techs.append(technique_name)
    character.db.techniques_known = known_techs
    
    return True, f"You learned {technique_name} from {trainer['name']}!"
