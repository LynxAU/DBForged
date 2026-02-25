"""
================================================================================
KI SENSE TRAINING - DBForged Vertical Slice
================================================================================

This module provides a Ki Sense Training minigame for players to train
their ki control and sensing abilities.

KI SENSE TRAINING:
------------------
A mini-game where players must detect and track ki signatures.

How it works:
1. A ki signature appears somewhere in the area
2. Player must use 'sense' to detect it
3. Track the signature by detecting multiple times
4. Pinpoint the exact location

Levels:
- Beginner: Detect 3 ki signatures
- Intermediate: Track moving signatures  
- Advanced: Detect hidden/blended signatures
- Master: Sense across the entire planet

Rewards:
- PL gains based on success
- Technique: Ki Sense (passive, sense others)
- Unlock: Can sense hidden enemies

Example Usage:
-------------
# Start training
sense training

# Try to sense ki
sense

# Check training status
sense status
"""

from __future__ import annotations

import random
import time
from typing import Dict, List, Optional, Any
from enum import Enum


class TrainingLevel(Enum):
    """Training difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


# Training configuration
TRAINING_CONFIG = {
    TrainingLevel.BEGINNER: {
        "signatures": 3,
        "move_chance": 0,
        "hidden_chance": 0,
        "pl_reward": 100,
        "sense_difficulty": 5,
    },
    TrainingLevel.INTERMEDIATE: {
        "signatures": 5,
        "move_chance": 30,
        "hidden_chance": 0,
        "pl_reward": 250,
        "sense_difficulty": 10,
    },
    TrainingLevel.ADVANCED: {
        "signatures": 7,
        "move_chance": 50,
        "hidden_chance": 30,
        "pl_reward": 500,
        "sense_difficulty": 15,
    },
    TrainingLevel.MASTER: {
        "signatures": 10,
        "move_chance": 70,
        "hidden_chance": 60,
        "pl_reward": 1000,
        "sense_difficulty": 20,
    },
}


# =============================================================================
# KI SENSE TRAINING FUNCTIONS
# =============================================================================


def start_training(character, level: TrainingLevel = None) -> tuple[bool, str]:
    """
    Start Ki Sense training.
    
    Args:
        character: The character training
        level: Training level (auto-selected if None)
    
    Returns:
        Tuple of (success, message)
    """
    pl = character.db.get('power_level', 0)
    
    # Auto-select level based on PL
    if level is None:
        if pl >= 50000:
            level = TrainingLevel.MASTER
        elif pl >= 25000:
            level = TrainingLevel.ADVANCED
        elif pl >= 10000:
            level = TrainingLevel.INTERMEDIATE
        else:
            level = TrainingLevel.BEGINNER
    
    config = TRAINING_CONFIG[level]
    
    # Check PL requirements
    pl_requirements = {
        TrainingLevel.BEGINNER: 0,
        TrainingLevel.INTERMEDIATE: 10000,
        TrainingLevel.ADVANCED: 25000,
        TrainingLevel.MASTER: 50000,
    }
    
    if pl < pl_requirements[level]:
        return False, f"You need {pl_requirements[level]:,} PL for {level.value} training."
    
    # Check if already training
    if character.db.get('ki_sense_training'):
        return False, "You're already in a training session! Use 'sense training' to check status."
    
    # Initialize training state
    training_data = {
        "level": level.value,
        "start_time": time.time(),
        "detected": [],
        "required": config["signatures"],
        "current_signature": None,
        "hint_x": random.randint(1, 10),
        "hint_y": random.randint(1, 10),
    }
    
    character.db.ki_sense_training = training_data
    character.db.ki_sense_active = True
    
    return True, f"""|y=== KI SENSE TRAINING STARTED ===|n

Level: {level.value.title()}
Goal: Detect {config['signatures']} ki signatures in the area.

|xTip: Use 'sense' repeatedly to detect ki signatures.
The signatures may move or hide, so be quick!

You feel a faint ki signature nearby... somewhere in the area.
|hUse 'sense' to detect it!|n
"""


def stop_training(character) -> tuple[bool, str]:
    """
    Stop Ki Sense training.
    
    Args:
        character: The character stopping training
    
    Returns:
        Tuple of (success, message)
    """
    if not character.db.get('ki_sense_training'):
        return False, "You're not currently training."
    
    # Calculate rewards
    training = character.db.ki_sense_training
    detected = len(training.get('detected', []))
    required = training.get('required', 0)
    
    level = TrainingLevel(training['level'])
    config = TRAINING_CONFIG[level]
    
    # Calculate PL reward (proportional to success)
    pl_reward = int(config['pl_reward'] * (detected / required)) if required > 0 else 0
    
    # Add PL
    if pl_reward > 0:
        current_pl = character.db.get('power_level', 0)
        character.db.power_level = current_pl + pl_reward
    
    # Clear training state
    character.db.ki_sense_training = None
    character.db.ki_sense_active = False
    
    return True, f"""|y=== TRAINING COMPLETE ===|n

Signatures Detected: {detected}/{required}
PL Gained: +{pl_reward}

Better luck next time!
"""


def sense_ki(character) -> tuple[bool, str]:
    """
    Attempt to sense ki signatures.
    
    Args:
        character: The sensing character
    
    Returns:
        Tuple of (success, message)
    """
    training = character.db.get('ki_sense_training')
    
    if not training:
        # Regular sense - just show nearby ki
        return sense_nearby_ki(character)
    
    # Training mode - try to detect signatures
    return detect_signature(character, training)


def detect_signature(character, training: Dict) -> tuple[bool, str]:
    """
    Detect a ki signature during training.
    
    Args:
        character: The detecting character
        training: Training state data
    
    Returns:
        Tuple of (success, message)
    """
    level = TrainingLevel(training['level'])
    config = TRAINING_CONFIG[level]
    
    pl = character.db.get('power_level', 0)
    
    # Calculate detection chance
    base_chance = 100 - config['sense_difficulty'] * 5
    
    # Bonus from PL
    pl_bonus = min(30, pl // 1000)
    
    # Random factor
    random_bonus = random.randint(-10, 10)
    
    total_chance = base_chance + pl_bonus + random_bonus
    
    # Check if hidden
    is_hidden = random.randint(1, 100) <= config['hidden_chance']
    if is_hidden:
        total_chance -= 30
    
    # Roll for detection
    if random.randint(1, 100) <= total_chance:
        # Success!
        detected_list = training.get('detected', [])
        
        # Generate a unique signature ID
        signature_id = len(detected_list) + 1
        
        # Move signature after detection (sometimes)
        if random.randint(1, 100) <= config['move_chance']:
            training['hint_x'] = random.randint(1, 10)
            training['hint_y'] = random.randint(1, 10)
        
        detected_list.append({
            "id": signature_id,
            "time": time.time(),
            "hidden": is_hidden,
        })
        training['detected'] = detected_list
        
        # Check if complete
        if len(detected_list) >= training['required']:
            return complete_training(character, training)
        
        # Continue training
        hint_msg = ""
        if random.random() < 0.3:  # 30% chance for hint
            x_dir = "north" if training['hint_x'] < 5 else "south"
            y_dir = "east" if training['hint_y'] < 5 else "west"
            hint_msg = f"\n|hThe signature feels {x_dir}-{y_dir}...|n"
        
        hidden_msg = " (hidden!)" if is_hidden else ""
        
        return True, f"""|g✓ Signature Detected!|n

You sensed a ki signature hidden={hidden_msg}

Progress: {len(detected_list)}/{training['required']}
{hint_msg}

|xUse 'sense' again to detect the next one!|n"""
    
    # Failed to detect
    return False, """|r✗ No ki detected...

The ki signature is moving around, making it hard to pin down.
Keep trying!|n"""


def complete_training(character, training: Dict) -> tuple[bool, str]:
    """
    Complete the training session.
    
    Args:
        character: The character completing training
        training: Training state data
    
    Returns:
        Tuple of (success, message)
    """
    level = TrainingLevel(training['level'])
    config = TRAINING_CONFIG[level]
    
    # Full reward
    pl_reward = config['pl_reward']
    
    # Add PL
    current_pl = character.db.get('power_level', 0)
    character.db.power_level = current_pl + pl_reward
    
    # Maybe unlock ki sense technique
    known_techniques = character.db.get('known_techniques', [])
    technique_unlocked = False
    
    if "ki_sense" not in known_techniques:
        known_techniques.append("ki_sense")
        character.db.known_techniques = known_techniques
        technique_unlocked = True
    
    # Clear training state
    character.db.ki_sense_training = None
    character.db.ki_sense_active = False
    
    tech_msg = "\n|yNew Technique Unlocked: Ki Sense!|n" if technique_unlocked else ""
    
    return True, f"""|c★ TRAINING COMPLETE ★|n

Level: {level.value.title()}
Signatures Detected: {len(training['detected'])}/{training['required']}

|cPL Gained: +{pl_reward:,}|n{tech_msg}

Excellent work! Your ki sensing abilities have improved.
"""


def sense_nearby_ki(character) -> tuple[bool, str]:
    """
    Sense nearby ki signatures (non-training).
    
    Args:
        character: The sensing character
    
    Returns:
        Tuple of (success, message)
    """
    pl = character.db.get('power_level', 0)
    
    # Check if has ki sense
    known = character.db.get('known_techniques', [])
    has_ki_sense = "ki_sense" in known
    
    # Show nearby enemies would go here
    # For now, just show training option
    
    lines = ["|y=== KI SENSING ===|n\n"]
    
    lines.append(f"Your PL: {pl:,}\n")
    
    if character.db.get('ki_sense_training'):
        lines.append("|rYou are in a training session!|n\n")
        training = character.db.ki_sense_training
        level = training['level']
        config = TRAINING_CONFIG[TrainingLevel(level)]
        
        lines.append(f"Level: {training['level'].title()}\n")
        lines.append(f"Progress: {len(training['detected'])}/{training['required']}\n")
        lines.append("\nUse 'sense' to continue detecting signatures!\n")
    else:
        lines.append("|yCommands:|n\n")
        lines.append("  sense training - Start Ki Sense training\n")
        lines.append("  sense status   - View training status\n")
        lines.append("  sense           - Try to sense nearby ki\n")
        
        if has_ki_sense:
            lines.append("\n|g✓ You have Ki Sense ability!|n")
            lines.append("You can sense hidden enemies and track ki signatures.\n")
        else:
            lines.append("\nComplete Ki Sense training to unlock Ki Sense ability!\n")
    
    return "".join(lines)


def get_training_status(character) -> str:
    """
    Get training status.
    
    Args:
        character: The character
    
    Returns:
        Formatted status string
    """
    training = character.db.get('ki_sense_training')
    
    if not training:
        return sense_nearby_ki(character)[1]
    
    level = TrainingLevel(training['level'])
    config = TRAINING_CONFIG[level]
    
    lines = ["|y=== KI SENSE TRAINING STATUS ===|n\n"]
    
    lines.append(f"Level: {training['level'].title()}\n")
    lines.append(f"Progress: {len(training['detected'])}/{training['required']}\n")
    
    # Time elapsed
    elapsed = time.time() - training.get('start_time', time.time())
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    lines.append(f"Time: {minutes}m {seconds}s\n")
    
    lines.append("\n|yCommands:|n")
    lines.append("  sense        - Detect next signature\n")
    lines.append("  sense stop   - End training early\n")
    lines.append("  sense status - View this status\n")
    
    return "".join(lines)


# =============================================================================
# KI SENSE COMMANDS
# =============================================================================


class KiSenseCommand:
    """Ki Sense command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """Handle ki sense subcommands."""
        args = args.strip().lower() if args else ""
        
        if args == "":
            success, msg = sense_ki(caller)
            return msg if success else f"|r{msg}|n"
        
        if args == "training":
            success, msg = start_training(caller)
            return msg if success else f"|r{msg}|n"
        
        if args == "status":
            return get_training_status(caller)
        
        if args == "stop" or args == "end":
            success, msg = stop_training(caller)
            return msg if success else f"|r{msg}|n"
        
        if args == "help":
            return """|yKi Sense Commands:|n
  sense              - Try to sense ki
  sense training    - Start training
  sense status      - View training status
  sense stop        - Stop training

Training:
  Ki Sense training helps you develop your ability to
  detect and track ki signatures. Complete training
  to unlock the Ki Sense passive ability!
  
  Benefits of Ki Sense:
    - Detect hidden enemies
    - Track moving targets
    - Sense ki across greater distances
"""
        
        # Default to sensing
        success, msg = sense_ki(caller)
        return msg if success else f"|r{msg}|n"
