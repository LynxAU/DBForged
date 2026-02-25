"""
================================================================================
INVENTORY & EQUIPMENT SYSTEM - DBForged Vertical Slice
================================================================================

This module provides a comprehensive inventory and equipment system for DBZ-themed
 gameplay. Players can carry items, equip gear, and use consumables.

INVENTORY SYSTEM:
-----------------
- Each character has an inventory (list of item keys)
- Maximum inventory slots: 20 (upgradeable)
- Items can be used, dropped, given, or traded

EQUIPMENT SYSTEM:
-----------------
Slots:
  - clothing: Weighted training clothing (increases XP gain)
  - accessory: Rings, watches, etc. (various bonuses)
  - pod: Capsule corp pod (allows instant recall)
  
Equipment bonuses:
  - Weighted Clothing: 1.1x - 2.0x XP gain during training
  - Accessory: Various (see ITEM_DEFINITIONS)
  - Pod: Instant return to saved location

CONSUMABLES:
------------
- Senzu Bean: Restores 100% HP and KI
- Super Senzu: Restores 100% HP/KI + cures all status effects
- Energy Drink: Restores 50% KI
- Protein Shake: Restores 50% HP
- Antidote: Cures all debuffs
- Elixir: Permanent +5% max HP or KI (rare)

CAPSULES:
---------
Capsules are collectible items that contain:
  - Weapons (not implemented in this version)
  - Vehicles (pods, cars)
  - Housing items
  - Rare materials

Capsule types:
  - Capsule S: Small (fits in pocket)
  - Capsule M: Medium
  - Capsule L: Large
  - Capsule XL: Very large

ITEM RARITY:
------------
- Common (white): 60% drop rate
- Uncommon (green): 25% drop rate
- Rare (blue): 10% drop rate
- Epic (purple): 4% drop rate
- Legendary (gold): 1% drop rate

CURRENCY:
---------
- Zeni: Primary currency (earned from combat, quests, selling items)
- Dragon Balls: Special currency (7 needed for Shenron wish)

EXAMPLE USAGE:
--------------
1. Using an item:
   use_item(player, "senzu_bean")

2. Equipping gear:
   equip_item(player, "weighted_clothing_heavy")

3. Checking inventory:
   get_inventory(player)

4. Selling items:
   sell_item(player, item_key, quantity)

INTEGRATION:
------------
- Training commands check for weighted clothing bonus
- Combat commands can drop items from enemies
- Quest rewards can include items
- Shops can buy/sell items
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ItemRarity(Enum):
    """Rarity levels for items."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ItemType(Enum):
    """Types of items."""
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    CAPSULE = "capsule"
    MATERIAL = "material"
    QUEST = "quest"
    CURRENCY = "currency"


class EquipmentSlot(Enum):
    """Equipment slot types."""
    CLOTHING = "clothing"
    ACCESSORY = "accessory"
    POD = "pod"


# Item Definitions - all items in the game
ITEM_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # ==================== CONSUMABLES ====================
    "senzu_bean": {
        "name": "Senzu Bean",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.RARE,
        "description": "A mystical bean that fully restores HP and KI.",
        "use_effect": {"hp_restore": 100, "ki_restore": 100},
        "value": 500,
        "stackable": True,
        "max_stack": 10,
    },
    "super_senzu": {
        "name": "Super Senzu Bean",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.LEGENDARY,
        "description": "An ultra-rare bean that fully restores HP/KI and cures all status effects.",
        "use_effect": {"hp_restore": 100, "ki_restore": 100, "cure_all": True},
        "value": 2000,
        "stackable": True,
        "max_stack": 5,
    },
    "energy_drink": {
        "name": "Energy Drink",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.COMMON,
        "description": "Restores 50% KI.",
        "use_effect": {"ki_restore": 50},
        "value": 50,
        "stackable": True,
        "max_stack": 20,
    },
    "protein_shake": {
        "name": "Protein Shake",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.COMMON,
        "description": "Restores 50% HP.",
        "use_effect": {"hp_restore": 50},
        "value": 50,
        "stackable": True,
        "max_stack": 20,
    },
    "antidote": {
        "name": "Antidote",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.UNCOMMON,
        "description": "Cures all debuffs.",
        "use_effect": {"cure_debuffs": True},
        "value": 150,
        "stackable": True,
        "max_stack": 10,
    },
    "elixir_hp": {
        "name": "HP Elixir",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.EPIC,
        "description": "Permanently increases max HP by 5%. One-time use per character.",
        "use_effect": {"perm_max_hp": 5},
        "value": 5000,
        "stackable": False,
    },
    "elixir_ki": {
        "name": "KI Elixir",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.EPIC,
        "description": "Permanently increases max KI by 5%. One-time use per character.",
        "use_effect": {"perm_max_ki": 5},
        "value": 5000,
        "stackable": False,
    },
    "sensei_tea": {
        "name": "Sensei's Tea",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.RARE,
        "description": "Doubles XP gain for next training session.",
        "use_effect": {"xp_boost": 2.0, "duration": 3600},  # 1 hour
        "value": 300,
        "stackable": True,
        "max_stack": 5,
    },
    "gravity_charge": {
        "name": "Gravity Charge",
        "type": ItemType.CONSUMABLE,
        "rarity": ItemRarity.RARE,
        "description": "Allows 1 hour of gravity chamber training.",
        "use_effect": {"gravity_session": 3600},
        "value": 400,
        "stackable": True,
        "max_stack": 10,
    },

    # ==================== EQUIPMENT - CLOTHING ====================
    "weighted_clothing_light": {
        "name": "Light Weighted Clothing",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.CLOTHING,
        "rarity": ItemRarity.COMMON,
        "description": "Light training weights. +10% XP gain during training.",
        "equipment_bonus": {"xp_mod": 1.1},
        "value": 200,
        "stackable": False,
    },
    "weighted_clothing_medium": {
        "name": "Medium Weighted Clothing",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.CLOTHING,
        "rarity": ItemRarity.UNCOMMON,
        "description": "Medium training weights. +25% XP gain during training.",
        "equipment_bonus": {"xp_mod": 1.25},
        "value": 500,
        "stackable": False,
    },
    "weighted_clothing_heavy": {
        "name": "Heavy Weighted Clothing",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.CLOTHING,
        "rarity": ItemRarity.RARE,
        "description": "Heavy training weights. +50% XP gain during training.",
        "equipment_bonus": {"xp_mod": 1.5},
        "value": 1500,
        "stackable": False,
    },
    "weighted_clothing_elite": {
        "name": "Elite Weighted Gi",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.CLOTHING,
        "rarity": ItemRarity.EPIC,
        "description": "Master-level training gi. +100% XP gain during training.",
        "equipment_bonus": {"xp_mod": 2.0},
        "value": 5000,
        "stackable": False,
    },
    "tournament_gi": {
        "name": "Tournament Gi",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.CLOTHING,
        "rarity": ItemRarity.RARE,
        "description": "Worn by tournament champions. +15% combat stats in arena.",
        "equipment_bonus": {"arena_damage": 1.15},
        "value": 1000,
        "stackable": False,
    },

    # ==================== EQUIPMENT - ACCESSORIES ====================
    "scouter": {
        "name": "Scouter",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.ACCESSORY,
        "rarity": ItemRarity.UNCOMMON,
        "description": "Displays enemy power level when scanning.",
        "equipment_bonus": {"scan_bonus": True},
        "value": 300,
        "stackable": False,
    },
    "combat_watch": {
        "name": "Combat Watch",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.ACCESSORY,
        "rarity": ItemRarity.RARE,
        "description": "Shows enemy HP percentage during combat.",
        "equipment_bonus": {"show_hp_percent": True},
        "value": 800,
        "stackable": False,
    },
    "power bracelet": {
        "name": "Power Bracelet",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.ACCESSORY,
        "rarity": ItemRarity.RARE,
        "description": "+10% melee damage.",
        "equipment_bonus": {"melee_damage": 1.1},
        "value": 750,
        "stackable": False,
    },
    "ki_amplifier": {
        "name": "KI Amplifier",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.ACCESSORY,
        "rarity": ItemRarity.RARE,
        "description": "+10% ki damage.",
        "equipment_bonus": {"ki_damage": 1.1},
        "value": 750,
        "stackable": False,
    },
    "saiyan_armband": {
        "name": "Saiyan Armband",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.ACCESSORY,
        "rarity": ItemRarity.EPIC,
        "description": "+20% XP gain, +10% critical chance.",
        "equipment_bonus": {"xp_mod": 1.2, "crit_chance": 10},
        "value": 3000,
        "stackable": False,
    },

    # ==================== EQUIPMENT - PODS ====================
    "capsule_pod": {
        "name": "Capsule Corp Pod",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.POD,
        "rarity": ItemRarity.RARE,
        "description": "Store a location and instantly return to it once per day.",
        "equipment_bonus": {"recall": True},
        "value": 2000,
        "stackable": False,
    },
    "mega_pod": {
        "name": "Mega Capsule Pod",
        "type": ItemType.EQUIPMENT,
        "slot": EquipmentSlot.POD,
        "rarity": ItemRarity.EPIC,
        "description": "Store 3 locations, unlimited recalls (3 min cooldown).",
        "equipment_bonus": {"recall_slots": 3, "recall_cooldown": 180},
        "value": 8000,
        "stackable": False,
    },

    # ==================== CAPSULES ====================
    "capsule_s": {
        "name": "Capsule S",
        "type": ItemType.CAPSULE,
        "rarity": ItemRarity.COMMON,
        "description": "Small capsule. Contains basic supplies.",
        "capsule_contents": {"type": "supplies", "value_min": 50, "value_max": 200},
        "value": 100,
        "stackable": True,
        "max_stack": 50,
    },
    "capsule_m": {
        "name": "Capsule M",
        "type": ItemType.CAPSULE,
        "rarity": ItemRarity.UNCOMMON,
        "description": "Medium capsule. Contains moderate supplies.",
        "capsule_contents": {"type": "supplies", "value_min": 200, "value_max": 500},
        "value": 300,
        "stackable": True,
        "max_stack": 30,
    },
    "capsule_l": {
        "name": "Capsule L",
        "type": ItemType.CAPSULE,
        "rarity": ItemRarity.RARE,
        "description": "Large capsule. Contains valuable equipment.",
        "capsule_contents": {"type": "equipment", "rarity": "uncommon"},
        "value": 800,
        "stackable": True,
        "max_stack": 10,
    },
    "capsule_xl": {
        "name": "Capsule XL",
        "type": ItemType.CAPSULE,
        "rarity": ItemRarity.EPIC,
        "description": "Huge capsule. Contains rare equipment or items.",
        "capsule_contents": {"type": "equipment", "rarity": "rare"},
        "value": 2500,
        "stackable": True,
        "max_stack": 5,
    },

    # ==================== CURRENCY ====================
    "zeni": {
        "name": "Zeni",
        "type": ItemType.CURRENCY,
        "rarity": ItemRarity.COMMON,
        "description": "Standard currency of the universe.",
        "value": 1,
        "stackable": True,
        "max_stack": 999999,
    },
    "dragon_ball": {
        "name": "Dragon Ball",
        "type": ItemType.CURRENCY,
        "rarity": ItemRarity.LEGENDARY,
        "description": "One of seven balls that summon Shenron.",
        "value": 10000,
        "stackable": True,
        "max_stack": 7,
    },
    "earth_shard": {
        "name": "Earth Shard",
        "type": ItemType.MATERIAL,
        "rarity": ItemRarity.UNCOMMON,
        "description": "A shard of Earth's energy. Used for crafting.",
        "value": 150,
        "stackable": True,
        "max_stack": 100,
    },
    "namekian_crystal": {
        "name": "Namekian Crystal",
        "type": ItemType.MATERIAL,
        "rarity": ItemRarity.RARE,
        "description": "A crystal from Namek. Used for powerful equipment.",
        "value": 400,
        "stackable": True,
        "max_stack": 50,
    },
    "saiyan_ DNA": {
        "name": "Saiyan DNA",
        "type": ItemType.MATERIAL,
        "rarity": ItemRarity.EPIC,
        "description": "Pure Saiyan genetic material. Used for transformation research.",
        "value": 1000,
        "stackable": True,
        "max_stack": 20,
    },
}


# Drop tables for different enemy tiers
DROP_TABLES: Dict[str, List[Dict[str, Any]]] = {
    "weak": [
        {"item": "zeni", "min": 10, "max": 50, "chance": 100},
        {"item": "protein_shake", "chance": 10},
        {"item": "energy_drink", "chance": 10},
        {"item": "capsule_s", "chance": 5},
    ],
    "normal": [
        {"item": "zeni", "min": 50, "max": 200, "chance": 100},
        {"item": "protein_shake", "chance": 20},
        {"item": "energy_drink", "chance": 20},
        {"item": "capsule_s", "chance": 15},
        {"item": "capsule_m", "chance": 5},
        {"item": "weighted_clothing_light", "chance": 3},
        {"item": "antidote", "chance": 10},
    ],
    "strong": [
        {"item": "zeni", "min": 200, "max": 500, "chance": 100},
        {"item": "senzu_bean", "chance": 10},
        {"item": "capsule_m", "chance": 20},
        {"item": "capsule_l", "chance": 5},
        {"item": "weighted_clothing_medium", "chance": 5},
        {"item": "scouter", "chance": 5},
        {"item": "sensei_tea", "chance": 10},
    ],
    "boss": [
        {"item": "zeni", "min": 1000, "max": 5000, "chance": 100},
        {"item": "senzu_bean", "chance": 30},
        {"item": "super_senzu", "chance": 5},
        {"item": "capsule_l", "chance": 30},
        {"item": "capsule_xl", "chance": 10},
        {"item": "weighted_clothing_heavy", "chance": 10},
        {"item": "power_bracelet", "chance": 10},
        {"item": "ki_amplifier", "chance": 10},
    ],
    "world_boss": [
        {"item": "zeni", "min": 10000, "max": 50000, "chance": 100},
        {"item": "super_senzu", "chance": 50},
        {"item": "capsule_xl", "chance": 50},
        {"item": "weighted_clothing_elite", "chance": 20},
        {"item": "saiyan_ DNA", "chance": 30},
        {"item": "elixir_hp", "chance": 10},
        {"item": "elixir_ki", "chance": 10},
    ],
}


# =============================================================================
# INVENTORY FUNCTIONS
# =============================================================================


def _ensure_inventory(character) -> Dict[str, int]:
    """Ensure character has inventory storage."""
    if not hasattr(character.db, 'inventory') or character.db.inventory is None:
        character.db.inventory = {}
    return character.db.inventory


def _ensure_equipment(character) -> Dict[str, Optional[str]]:
    """Ensure character has equipment storage."""
    if not hasattr(character.db, 'equipment') or character.db.equipment is None:
        character.db.equipment = {
            "clothing": None,
            "accessory": None,
            "pod": None,
        }
    return character.db.equipment


def get_inventory(character) -> List[tuple[str, int]]:
    """
    Get character's inventory as list of (item_key, quantity).
    
    Returns:
        List of tuples (item_key, quantity)
    """
    inv = _ensure_inventory(character)
    return [(key, qty) for key, qty in inv.items() if qty > 0]


def add_item(character, item_key: str, quantity: int = 1) -> bool:
    """
    Add an item to character's inventory.
    
    Args:
        character: The character to add the item to
        item_key: The item to add
        quantity: How many to add
    
    Returns:
        True if added successfully, False if failed
    """
    if item_key not in ITEM_DEFINITIONS:
        return False
    
    item_def = ITEM_DEFINITIONS[item_key]
    inv = _ensure_inventory(character)
    
    # Check stackability and max stack
    if item_def.get("stackable", False):
        max_stack = item_def.get("max_stack", 99)
        current = inv.get(item_key, 0)
        if current + quantity > max_stack:
            character.msg(f"|yYou can only hold {max_stack} {item_def['name']}s.|n")
            return False
        inv[item_key] = current + quantity
    else:
        # Non-stackable items
        if quantity > 1:
            quantity = 1  # Can only add 1 non-stackable
        if inv.get(item_key, 0) > 0:
            character.msg(f"|yYou already have a {item_def['name']}.|n")
            return False
        inv[item_key] = quantity
    
    return True


def remove_item(character, item_key: str, quantity: int = 1) -> bool:
    """
    Remove an item from character's inventory.
    
    Args:
        character: The character to remove from
        item_key: The item to remove
        quantity: How many to remove
    
    Returns:
        True if removed successfully, False if failed
    """
    inv = _ensure_inventory(character)
    current = inv.get(item_key, 0)
    
    if current < quantity:
        return False
    
    inv[item_key] = current - quantity
    if inv[item_key] <= 0:
        del inv[item_key]
    
    return True


def has_item(character, item_key: str) -> bool:
    """Check if character has an item."""
    inv = _ensure_inventory(character)
    return item_key in inv and inv[item_key] > 0


def get_item_count(character, item_key: str) -> int:
    """Get quantity of an item in inventory."""
    inv = _ensure_inventory(character)
    return inv.get(item_key, 0)


# =============================================================================
# EQUIPMENT FUNCTIONS
# =============================================================================


def equip_item(character, item_key: str) -> tuple[bool, str]:
    """
    Equip an item to a slot.
    
    Args:
        character: The character equipping the item
        item_key: The item to equip
    
    Returns:
        Tuple of (success, message)
    """
    if item_key not in ITEM_DEFINITIONS:
        return False, "Unknown item."
    
    item_def = ITEM_DEFINITIONS[item_key]
    
    if item_def.get("type") != ItemType.EQUIPMENT:
        return False, "That item cannot be equipped."
    
    # Check if character has the item
    if not has_item(character, item_key):
        return False, "You don't have that item."
    
    # Determine slot
    slot = item_def.get("slot")
    if not slot:
        return False, "This item has no equipment slot."
    
    equip = _ensure_equipment(character)
    
    # Check if something is already equipped
    current = equip.get(slot.value)
    if current:
        # Unequip current item first
        unequip_item(character, slot.value)
    
    # Equip new item
    remove_item(character, item_key)
    equip[slot.value] = item_key
    
    return True, f"You equip {item_def['name']}."


def unequip_item(character, slot: str) -> tuple[bool, str]:
    """
    Unequip an item from a slot.
    
    Args:
        character: The character unequipping
        slot: The slot to unequip (clothing, accessory, pod)
    
    Returns:
        Tuple of (success, message)
    """
    equip = _ensure_equipment(character)
    current = equip.get(slot)
    
    if not current:
        return False, "Nothing equipped in that slot."
    
    item_def = ITEM_DEFINITIONS.get(current)
    if not item_def:
        return False, "Error: equipped item not found."
    
    # Add back to inventory
    add_item(character, current)
    
    # Clear slot
    equip[slot] = None
    
    return True, f"You unequip {item_def['name']}."


def get_equipped(character, slot: str) -> Optional[str]:
    """Get the item equipped in a slot."""
    equip = _ensure_equipment(character)
    return equip.get(slot)


def get_equipment_bonus(character, bonus_type: str) -> float:
    """
    Get a cumulative bonus from all equipped items.
    
    Args:
        character: The character
        bonus_type: The bonus type (xp_mod, melee_damage, ki_damage, etc.)
    
    Returns:
        Multiplier (1.0 = no bonus)
    """
    equip = _ensure_equipment(character)
    multiplier = 1.0
    
    for slot_item in equip.values():
        if not slot_item:
            continue
        item_def = ITEM_DEFINITIONS.get(slot_item)
        if not item_def:
            continue
        
        bonuses = item_def.get("equipment_bonus", {})
        if bonus_type in bonuses:
            multiplier *= bonuses[bonus_type]
    
    return multiplier


# =============================================================================
# ITEM USAGE FUNCTIONS
# =============================================================================


def use_item(character, item_key: str) -> tuple[bool, str]:
    """
    Use an item from inventory.
    
    Args:
        character: The character using the item
        item_key: The item to use
    
    Returns:
        Tuple of (success, message)
    """
    if item_key not in ITEM_DEFINITIONS:
        return False, "Unknown item."
    
    item_def = ITEM_DEFINITIONS[item_key]
    
    if not has_item(character, item_key):
        return False, "You don't have that item."
    
    # Check item type
    if item_def.get("type") != ItemType.CONSUMABLE:
        return False, "That item cannot be used directly."
    
    effect = item_def.get("use_effect", {})
    
    # Apply effects
    messages = []
    
    # HP restore
    if "hp_restore" in effect:
        current_hp = getattr(character, 'db', {}).get('hp', 100)
        max_hp = getattr(character, 'db', {}).get('max_hp', 100)
        restore = (effect["hp_restore"] / 100.0) * max_hp
        new_hp = min(current_hp + restore, max_hp)
        character.db.hp = new_hp
        messages.append(f"|gRestored {restore:.0f} HP!|n")
    
    # KI restore
    if "ki_restore" in effect:
        current_ki = getattr(character, 'db', {}).get('ki', 100)
        max_ki = getattr(character, 'db', {}).get('max_ki', 100)
        restore = (effect["ki_restore"] / 100.0) * max_ki
        new_ki = min(current_ki + restore, max_ki)
        character.db.ki = new_ki
        messages.append(f"|gRestored {restore:.0f} KI!|n")
    
    # Cure all status effects
    if effect.get("cure_all"):
        from world.status_effects import remove_all_debuffs, remove_all_buffs
        remove_all_debuffs(character)
        remove_all_buffs(character)
        messages.append("|gCured all status effects!|n")
    
    # Cure debuffs only
    if effect.get("cure_debuffs"):
        from world.status_effects import remove_all_debuffs
        remove_all_debuffs(character)
        messages.append("|gCured all debuffs!|n")
    
    # Permanent HP increase
    if "perm_max_hp" in effect:
        current_max = character.db.get('max_hp', 100)
        increase = (effect["perm_max_hp"] / 100.0) * current_max
        character.db.max_hp = current_max + increase
        character.db.hp = character.db.max_hp  # Full heal
        messages.append(f"|gPermanently increased max HP by {effect['perm_max_hp']}%!|n")
    
    # Permanent KI increase
    if "perm_max_ki" in effect:
        current_max = character.db.get('max_ki', 100)
        increase = (effect["perm_max_ki"] / 100.0) * current_max
        character.db.max_ki = current_max + increase
        character.db.ki = character.db.max_ki  # Full refill
        messages.append(f"|gPermanently increased max KI by {effect['perm_max_ki']}%!|n")
    
    # XP boost (store as temporary flag)
    if "xp_boost" in effect:
        character.db.xp_boost_multiplier = effect["xp_boost"]
        character.db.xp_boost_expires = effect.get("duration", 3600)
        messages.append(f"|gXP gain doubled for {effect.get('duration', 3600)//60} minutes!|n")
    
    # Gravity session
    if "gravity_session" in effect:
        character.db.gravity_session = effect["gravity_session"]
        messages.append("|gGravity chamber session activated!|n")
    
    # Remove used item
    remove_item(character, item_key)
    
    return True, " ".join(messages)


# =============================================================================
# DROP & REWARD FUNCTIONS
# =============================================================================


def roll_drops(character, drop_table: str) -> List[tuple[str, int]]:
    """
    Roll for random drops based on enemy tier.
    
    Args:
        character: The character receiving drops (for Zeni)
        drop_table: The enemy tier (weak, normal, strong, boss, world_boss)
    
    Returns:
        List of (item_key, quantity) drops
    """
    drops = []
    table = DROP_TABLES.get(drop_table, [])
    
    for entry in table:
        chance = entry.get("chance", 0)
        if random.randint(1, 100) > chance:
            continue
        
        item = entry.get("item")
        if item == "zeni":
            # Handle Zeni specially
            if random.randint(1, 100) <= chance:
                min_z = entry.get("min", 1)
                max_z = entry.get("max", 100)
                zeni = random.randint(min_z, max_z)
                # Apply any Zeni bonuses
                zeni_bonus = get_equipment_bonus(character, "zeni_bonus")
                zeni = int(zeni * zeni_bonus)
                drops.append(("zeni", zeni))
        else:
            # Regular item drop
            drops.append((item, 1))
    
    return drops


def give_drops(character, drops: List[tuple[str, int]]) -> str:
    """
    Give drops to a character and return a message.
    
    Args:
        character: The character receiving drops
        drops: List of (item_key, quantity)
    
    Returns:
        Message describing what was received
    """
    messages = []
    
    for item_key, quantity in drops:
        # Handle Zeni specially
        if item_key == "zeni":
            current_zeni = character.db.get('zeni', 0)
            character.db.zeni = current_zeni + quantity
            messages.append(f"+{quantity} Zeni")
            continue
        
        if item_key in ITEM_DEFINITIONS:
            add_item(character, item_key, quantity)
            item_def = ITEM_DEFINITIONS[item_key]
            if quantity > 1:
                messages.append(f"{item_def['name']} x{quantity}")
            else:
                messages.append(item_def['name'])
    
    if messages:
        return f"|gYou received: {', '.join(messages)}!|n"
    return ""


# =============================================================================
# INVENTORY DISPLAY
# =============================================================================


def get_inventory_display(character) -> str:
    """
    Get a formatted display of character's inventory.
    
    Returns:
        Formatted string showing inventory
    """
    inv = get_inventory(character)
    equip = _ensure_equipment(character)
    
    lines = ["|y=== INVENTORY ===|n"]
    
    # Show equipment
    lines.append("\n|yEQUIPPED:|n")
    for slot in ["clothing", "accessory", "pod"]:
        item = equip.get(slot)
        if item:
            item_def = ITEM_DEFINITIONS.get(item, {})
            lines.append(f"  {slot.title()}: |c{item_def.get('name', item)}|n")
        else:
            lines.append(f"  {slot.title()}: |x(nothing)|n")
    
    # Show inventory
    lines.append("\n|yITEMS:|n")
    if not inv:
        lines.append("  |x(EMPTY)|n")
    else:
        for item_key, qty in sorted(inv):
            item_def = ITEM_DEFINITIONS.get(item_key, {})
            name = item_def.get("name", item_key)
            rarity = item_def.get("rarity", ItemRarity.COMMON)
            
            # Color by rarity
            if rarity == ItemRarity.LEGENDARY:
                color = "|y"
            elif rarity == ItemRarity.EPIC:
                color = "|m"
            elif rarity == ItemRarity.RARE:
                color = "|b"
            elif rarity == ItemRarity.UNCOMMON:
                color = "|g"
            else:
                color = "|w"
            
            if qty > 1:
                lines.append(f"  {color}{name}|n x{qty}")
            else:
                lines.append(f"  {color}{name}|n")
    
    # Show Zeni
    zeni = character.db.get('zeni', 0)
    lines.append(f"\n|yZENI:|n  |y{zeni:,}|n")
    
    return "".join(lines)


def get_item_info(item_key: str) -> str:
    """Get detailed info about an item."""
    if item_key not in ITEM_DEFINITIONS:
        return "Unknown item."
    
    item = ITEM_DEFINITIONS[item_key]
    lines = []
    
    # Name and rarity
    rarity = item.get("rarity", ItemRarity.COMMON)
    if rarity == ItemRarity.LEGENDARY:
        lines.append(f"|y{item['name']}|n (Legendary)")
    elif rarity == ItemRarity.EPIC:
        lines.append(f"|m{item['name']}|n (Epic)")
    elif rarity == ItemRarity.RARE:
        lines.append(f"|b{item['name']}|n (Rare)")
    elif rarity == ItemRarity.UNCOMMON:
        lines.append(f"|g{item['name']}|n (Uncommon)")
    else:
        lines.append(f"|w{item['name']}|n (Common)")
    
    lines.append(f"\n{item['description']}")
    
    # Value
    lines.append(f"\nValue: {item['value']} Zeni")
    
    # Type-specific info
    if item.get("type") == ItemType.CONSUMABLE:
        effect = item.get("use_effect", {})
        effects = []
        if "hp_restore" in effect:
            effects.append(f"Restores {effect['hp_restore']}% HP")
        if "ki_restore" in effect:
            effects.append(f"Restores {effect['ki_restore']}% KI")
        if effect.get("cure_all"):
            effects.append("Cures all effects")
        if effect.get("cure_debuffs"):
            effects.append("Cures debuffs")
        if effects:
            lines.append(f"Effect: {', '.join(effects)}")
    
    elif item.get("type") == ItemType.EQUIPMENT:
        slot = item.get("slot")
        if slot:
            lines.append(f"Slot: {slot.value}")
        bonuses = item.get("equipment_bonus", {})
        if bonuses:
            lines.append("Bonuses:")
            for bonus, value in bonuses.items():
                if isinstance(value, float):
                    lines.append(f"  {bonus}: +{int((value-1)*100)}%")
                else:
                    lines.append(f"  {bonus}: {value}")
    
    return "".join(lines)
