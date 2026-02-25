"""
Namekian Fusion System - DBForged Bible Implementation
=======================================================
Implements Namekian fusion on NPC kill with offer/accept mechanics.
"""

import random
import time


# Global storage for fusion offers
_fusion_offers = {}


def check_fusion_on_kill(killer, victim):
    """
    Check if a Namekian fusion should trigger when killing a Namekian NPC.
    0.03% chance (3 in 10,000).
    
    Returns:
        tuple: (triggered: bool, offer_data: dict or None)
    """
    # Check if victim is a Namekian NPC
    victim_race = getattr(victim.db, 'race', None)
    if victim_race != 'namekian':
        return False, None
        
    # Check if victim is an NPC
    if not getattr(victim.db, 'is_npc', False):
        return False, None
    
    # 0.03% chance
    if random.random() > 0.0003:
        return False, None
    
    # Check if killer is a Namekian
    killer_race = getattr(killer.db, 'race', None)
    if killer_race != 'namekian':
        return False, None
    
    # Check if already fused
    if getattr(killer.db, 'namek_fused', False):
        return False, None
    
    # Create fusion offer
    offer_id = f"{killer.id}_{int(time.time())}"
    offer_data = {
        'offer_id': offer_id,
        'killer_id': killer.id,
        'killer_name': killer.key,
        'victim_name': victim.key,
        'offer_time': time.time(),
        'expires': time.time() + 300,  # 5 minutes to accept
    }
    
    _fusion_offers[offer_id] = offer_data
    killer.db.pending_fusion_offer = offer_id
    
    return True, offer_data


def get_fusion_offer(offer_id):
    """Get a fusion offer by ID."""
    return _fusion_offers.get(offer_id)


def accept_fusion(character, offer_id):
    """
    Accept a fusion offer.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check if already fused
    if getattr(character.db, 'namek_fused', False):
        return False, "You are already fused!"
    
    # Get the offer
    offer = _fusion_offers.get(offer_id)
    if not offer:
        return False, "That fusion offer has expired."
    
    # Check if offer is for this character
    if offer['killer_id'] != character.id:
        return False, "That offer is not for you."
    
    # Check if offer has expired
    if time.time() > offer['expires']:
        del _fusion_offers[offer_id]
        character.db.pending_fusion_offer = None
        return False, "That fusion offer has expired."
    
    # Apply fusion bonuses
    character.db.namek_fused = True
    character.db.fusion_partner = offer['victim_name']
    character.db.fusion_time = time.time()
    
    # +50% max KI
    current_max_ki = character.db.ki_max or 100
    character.db.ki_max = int(current_max_ki * 1.5)
    character.db.ki_current = character.db.ki_max  # Full KI on fusion
    
    # Clear the offer
    del _fusion_offers[offer_id]
    character.db.pending_fusion_offer = None
    
    return True, f"You fuse with {offer['victim_name']}! Your max KI increases by 50%!"


def decline_fusion(character, offer_id):
    """
    Decline a fusion offer.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    offer = _fusion_offers.get(offer_id)
    if not offer:
        return False, "That fusion offer has expired or doesn't exist."
    
    if offer['killer_id'] != character.id:
        return False, "That offer is not for you."
    
    # Clear the offer
    del _fusion_offers[offer_id]
    character.db.pending_fusion_offer = None
    
    return True, "You decline the fusion offer."


def check_fusion_cooldown(character):
    """
    Check if character can receive fusion offers (cooldown between fusions).
    1 hour cooldown after a fusion ends.
    """
    last_fusion = getattr(character.db, 'last_fusion_time', None)
    if not last_fusion:
        return True
    
    # 1 hour cooldown
    if time.time() - last_fusion > 3600:
        return True
    return False


def get_fusion_status(character):
    """Get fusion status for the character."""
    if not getattr(character.db, 'namek_fused', False):
        return None
    
    return {
        'is_fused': True,
        'partner': character.db.fusion_partner,
        'fusion_time': character.db.fusion_time,
        'ki_bonus': '50%',
    }


def can_unfuse(character):
    """
    Check if character can unfuse (at will after some time).
    """
    if not getattr(character.db, 'namek_fused', False):
        return False
    
    fusion_time = getattr(character.db, 'fusion_time', None)
    if not fusion_time:
        return False
    
    # Can unfuse after 5 minutes
    if time.time() - fusion_time > 300:
        return True
    return False


def unfuse(character):
    """
    Allow character to unfuse (at will after 5 minutes).
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not getattr(character.db, 'namek_fused', False):
        return False, "You are not currently fused."
    
    if not can_unfuse(character):
        fusion_time = getattr(character.db, 'fusion_time', 0)
        remaining = 300 - (time.time() - fusion_time)
        return False, f"You must wait {remaining:.0f} more seconds before you can unfuse."
    
    # Store fusion time for cooldown
    character.db.last_fusion_time = time.time()
    
    # Clear fusion flags
    character.db.namek_fused = False
    character.db.fusion_partner = None
    character.db.fusion_time = None
    
    # KI returns to normal (already at boosted max, but that's fine)
    
    return True, "You separate from your fusion partner. You can now fuse again in 1 hour."
