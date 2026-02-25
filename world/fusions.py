"""
Fusion System - Handles Potara and Metamoran fusion mechanics.
"""

from __future__ import annotations
import time
from typing import Optional, Tuple


# Fusion state storage (in-memory for active fusions)
# Format: {character_id: {"partner": partner_id, "type": "potara"|"metamoran", "started": timestamp}}
ACTIVE_FUSIONS = {}

# Pending fusion requests
# Format: {character_id: {"from": requester_id, "type": "potara"|"metamoran", "timeout": timestamp}}
PENDING_FUSION_REQUESTS = {}


def get_fusion_data(character) -> Optional[dict]:
    """Get fusion data for a character."""
    char_id = character.id
    return ACTIVE_FUSIONS.get(char_id)


def is_fused(character) -> bool:
    """Check if a character is currently fused."""
    return character.id in ACTIVE_FUSIONS


def get_fusion_partner(character) -> Optional[str]:
    """Get the character ID of the fusion partner."""
    data = get_fusion_data(character)
    return data.get("partner") if data else None


def get_fusion_type(character) -> Optional[str]:
    """Get the type of fusion (potara or metamoran)."""
    data = get_fusion_data(character)
    return data.get("type") if data else None


def is_metamoran_fusion(character) -> bool:
    """Check if character is in a Metamoran fusion (time-limited)."""
    return get_fusion_type(character) == "metamoran"


def is_potara_fusion(character) -> bool:
    """Check if character is in a Potara fusion (permanent until unfused)."""
    return get_fusion_type(character) == "potara"


def get_fusion_time_remaining(character) -> Optional[int]:
    """Get remaining time in seconds for Metamoran fusion. Returns None for Potara."""
    data = get_fusion_data(character)
    if not data or data.get("type") != "metamoran":
        return None
    
    duration_minutes = data.get("duration_minutes", 30)
    started = data.get("started", 0)
    elapsed = time.time() - started
    remaining = (duration_minutes * 60) - elapsed
    
    if remaining <= 0:
        return 0
    return int(remaining)


def is_fusion_expired(character) -> bool:
    """Check if a Metamoran fusion has expired."""
    if not is_metamoran_fusion(character):
        return False
    return get_fusion_time_remaining(character) <= 0


def initiate_fusion(fuser1, fuser2, fusion_type: str, duration_minutes: int = None) -> Tuple[bool, str]:
    """
    Initiate a fusion between two characters.
    
    Args:
        fuser1: First character (the one initiating)
        fuser2: Second character (the partner)
        fusion_type: "potara" or "metamoran"
        duration_minutes: Duration for Metamoran fusion (optional)
    
    Returns:
        (success, message)
    """
    # Check if either is already fused
    if is_fused(fuser1):
        return False, "You are already in a fusion!"
    if is_fused(fuser2):
        return False, f"{fuser2.key} is already in a fusion!"
    
    # Check if they're in the same room
    if fuser1.location != fuser2.location:
        return False, "You must be in the same location to fuse!"
    
    # Check if either is in combat (optional - could allow or deny)
    if fuser1.db.in_combat or fuser2.db.in_combat:
        return False, "Cannot fuse while in combat!"
    
    # Store fusion data
    now = time.time()
    
    ACTIVE_FUSIONS[fuser1.id] = {
        "partner": fuser2.id,
        "type": fusion_type,
        "started": now,
        "duration_minutes": duration_minutes,
        "fuser1_name": fuser1.key,
        "fuser2_name": fuser2.key,
    }
    
    ACTIVE_FUSIONS[fuser2.id] = {
        "partner": fuser1.id,
        "type": fusion_type,
        "started": now,
        "duration_minutes": duration_minutes,
        "fuser1_name": fuser1.key,
        "fuser2_name": fuser2.key,
    }
    
    # Store reference on characters for easy access
    fuser1.db.fusion_partner = fuser2.key
    fuser1.db.fusion_type = fusion_type
    fuser1.db.is_fused = True
    
    fuser2.db.fusion_partner = fuser1.key
    fuser2.db.fusion_type = fusion_type
    fuser2.db.is_fused = True
    
    fusion_name = "Potara Fusion" if fusion_type == "potara" else "Metamoran Fusion"
    duration_text = "" if fusion_type == "potara" else f" ({duration_minutes} minutes)"
    
    return True, f"Successfully initiated {fusion_name}!{duration_text} You are now fused as one being."


def unfuse(character) -> Tuple[bool, str]:
    """
    End a fusion between two characters.
    
    Args:
        character: One of the fused characters
    
    Returns:
        (success, message)
    """
    if not is_fused(character):
        return False, "You are not currently fused."
    
    data = get_fusion_data(character)
    partner_id = data.get("partner")
    fusion_type = data.get("type")
    
    # Find and unfuse the partner
    if partner_id:
        # Try to find partner in same room or elsewhere
        # We'll just clear their fusion data
        if partner_id in ACTIVE_FUSIONS:
            partner_data = ACTIVE_FUSIONS[partner_id]
            # Partner might be logged off, so we try to find them
            from typeclasses.characters import Character
            from evennia import search_object
            
            # Search for the partner object
            partner_objs = search_object(partner_id)
            if partner_objs:
                partner = partner_objs[0]
                if hasattr(partner, 'db'):
                    partner.db.fusion_partner = None
                    partner.db.fusion_type = None
                    partner.db.is_fused = False
            
            del ACTIVE_FUSIONS[partner_id]
    
    # Clear fusion data for the initiating character
    character.db.fusion_partner = None
    character.db.fusion_type = None
    character.db.is_fused = False
    
    del ACTIVE_FUSIONS[character.id]
    
    fusion_name = "Potara Fusion" if fusion_type == "potara" else "Metamoran Fusion"
    return True, f"You have ended the {fusion_name}. The two warriors separate."


def check_and_handle_fusion_expiry(character) -> Tuple[bool, str]:
    """
    Check if a fusion has expired and handle it.
    
    Returns:
        (was_expired, message) - was_expired is True if fusion just expired
    """
    if is_fusion_expired(character):
        partner_id = get_fusion_partner(character)
        fusion_type = get_fusion_type(character)
        
        # Clear fusion data
        if character.id in ACTIVE_FUSIONS:
            del ACTIVE_FUSIONS[character.id]
        
        character.db.fusion_partner = None
        character.db.fusion_type = None
        character.db.is_fused = False
        
        # Try to unfuse partner
        if partner_id and partner_id in ACTIVE_FUSIONS:
            from evennia import search_object
            partner_objs = search_object(partner_id)
            if partner_objs:
                partner = partner_objs[0]
                if hasattr(partner, 'db'):
                    partner.db.fusion_partner = None
                    partner.db.fusion_type = None
                    partner.db.is_fused = False
            del ACTIVE_FUSIONS[partner_id]
        
        return True, "Your Metamoran fusion has expired! The warriors separate."
    
    return False, ""


def get_combined_power_level(fuser1, fuser2) -> int:
    """
    Calculate the combined power level of two fused characters.
    
    The fusion multiplier is applied to the sum of both characters' PL.
    """
    from world.power import get_power_level
    
    pl1 = get_power_level(fuser1)
    pl2 = get_power_level(fuser2)
    
    # Base combined power
    combined = pl1 + pl2
    
    # Additional fusion multiplier is handled by the form's pl_factor
    # This returns the raw combined PL before form multipliers
    
    return combined


def can_fuse(character, target, fusion_type: str) -> Tuple[bool, str]:
    """
    Check if two characters can fuse.
    
    Args:
        character: The character initiating fusion
        target: The potential fusion partner
        fusion_type: "potara" or "metamoran"
    
    Returns:
        (can_fuse, reason)
    """
    # Check if already fused
    if is_fused(character):
        return False, "You are already in a fusion."
    if is_fused(target):
        return False, f"{target.key} is already in a fusion."
    
    # Check same location
    if character.location != target.location:
        return False, "You must be in the same location."
    
    # Check not in combat
    if character.db.in_combat or target.db.in_combat:
        return False, "Cannot fuse while in combat."
    
    # Check not the same character
    if character.id == target.id:
        return False, "You cannot fuse with yourself."
    
    # For Potara, check if they have the Potara earrings item
    if fusion_type == "potara":
        inventory = character.db.inventory or []
        if "potara_earrings" not in inventory:
            return False, "You need Potara earrings to perform this fusion."
    
    # For Metamoran, check if they've learned the dance
    if fusion_type == "metamoran":
        known = character.db.known_techniques or []
        if "metamoran_dance" not in known:
            return False, "You haven't learned the Metamoran dance."
    
    return True, "OK"


def format_fusion_status(character) -> str:
    """Format a nice status message about fusion state."""
    if not is_fused(character):
        return "You are not currently fused."
    
    data = get_fusion_data(character)
    fusion_type = data.get("type")
    partner_id = data.get("partner")
    fuser1_name = data.get("fuser1_name", "Unknown")
    fuser2_name = data.get("fuser2_name", "Unknown")
    
    from evennia import search_object
    partner_name = fuser2_name
    if partner_id:
        partner_objs = search_object(partner_id)
        if partner_objs:
            partner_name = partner_objs[0].key
    
    if fusion_type == "potara":
        return f"You are in Potara Fusion with {partner_name}. The fusion is permanent until you choose to unfuse."
    elif fusion_type == "metamoran":
        remaining = get_fusion_time_remaining(character)
        minutes = remaining // 60
        seconds = remaining % 60
        return f"You are in Metamoran Fusion with {partner_name}. Time remaining: {minutes}m {seconds}s."
    
    return "You are in an unknown fusion state."


def send_fusion_request(requester, target, fusion_type: str) -> Tuple[bool, str]:
    """
    Send a fusion request to another player.
    
    Args:
        requester: The character initiating the request
        target: The target to receive the request
        fusion_type: "potara" or "metamoran"
    
    Returns:
        (success, message)
    """
    # Check if either is already fused
    if is_fused(requester):
        return False, "You are already in a fusion!"
    if is_fused(target):
        return False, f"{target.key} is already in a fusion!"
    
    # Check if target already has a pending request
    if target.id in PENDING_FUSION_REQUESTS:
        return False, f"{target.key} already has a pending fusion request."
    
    # Check same location
    if requester.location != target.location:
        return False, "You must be in the same location."
    
    # Check not in combat
    if requester.db.in_combat or target.db.in_combat:
        return False, "Cannot fuse while in combat!"
    
    # Create pending request
    PENDING_FUSION_REQUESTS[target.id] = {
        "from": requester.id,
        "from_name": requester.key,
        "type": fusion_type,
        "timeout": time.time() + 60,  # 60 second timeout
    }
    
    # Notify requester
    requester.msg(f"|yYou sent a {fusion_type.title()} fusion request to {target.key}.|n")
    requester.msg("Waiting for their response... (request expires in 60 seconds)")
    
    # Notify target
    fusion_name = "Potara" if fusion_type == "potara" else "Metamoran"
    target.msg(f"|y{requester.key} wants to perform {fusion_name} fusion with you!|n")
    target.msg(f"Type 'accept fusion' to accept or 'decline fusion' to refuse.")
    
    return True, f"Fusion request sent to {target.key}."


def accept_fusion(character) -> Tuple[bool, str]:
    """
    Accept a pending fusion request.
    
    Args:
        character: The character accepting the request
    
    Returns:
        (success, message)
    """
    if character.id not in PENDING_FUSION_REQUESTS:
        return False, "You don't have any pending fusion requests."
    
    request_data = PENDING_FUSION_REQUESTS[character.id]
    requester_id = request_data["from"]
    fusion_type = request_data["type"]
    from_name = request_data["from_name"]
    
    # Check timeout
    if time.time() > request_data["timeout"]:
        del PENDING_FUSION_REQUESTS[character.id]
        return False, "The fusion request has expired."
    
    # Find the requester
    from evennia import search_object
    requester_objs = search_object(requester_id)
    if not requester_objs:
        del PENDING_FUSION_REQUESTS[character.id]
        return False, "The requester is no longer available."
    
    requester = requester_objs[0]
    
    # Check they're still in the same location
    if requester.location != character.location:
        del PENDING_FUSION_REQUESTS[character.id]
        return False, "You are no longer in the same location."
    
    # Check requirements again
    ok, reason = can_fuse(requester, character, fusion_type)
    if not ok:
        del PENDING_FUSION_REQUESTS[character.id]
        return False, reason
    
    ok, reason = can_fuse(character, requester, fusion_type)
    if not ok:
        del PENDING_FUSION_REQUESTS[character.id]
        return False, reason
    
    # Duration for metamoran
    duration = 30 if fusion_type == "metamoran" else None
    
    # Initiate fusion
    ok, msg = initiate_fusion(requester, character, fusion_type, duration)
    
    # Clean up request
    del PENDING_FUSION_REQUESTS[character.id]
    
    if ok:
        requester.msg(f"|g{character.key} accepted your fusion request! {msg}|n")
        character.msg(f"|gYou accepted the fusion! {msg}|n")
        requester.location.msg_contents(
            f"{requester.key} and {character.key} begin the fusion!",
            exclude=[requester, character]
        )
    
    return ok, msg


def decline_fusion(character) -> Tuple[bool, str]:
    """
    Decline a pending fusion request.
    
    Args:
        character: The character declining the request
    
    Returns:
        (success, message)
    """
    if character.id not in PENDING_FUSION_REQUESTS:
        return False, "You don't have any pending fusion requests."
    
    request_data = PENDING_FUSION_REQUESTS[character.id]
    requester_id = request_data["from"]
    from_name = request_data["from_name"]
    
    del PENDING_FUSION_REQUESTS[character.id]
    
    # Notify requester
    from evennia import search_object
    requester_objs = search_object(requester_id)
    if requester_objs:
        requester_objs[0].msg(f"|r{character.key} declined your fusion request.|n")
    
    return True, f"You declined the fusion request from {from_name}."


def has_pending_request(character) -> bool:
    """Check if character has a pending fusion request."""
    return character.id in PENDING_FUSION_REQUESTS
