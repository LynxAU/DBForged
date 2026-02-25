"""
Transformation Unlock Mechanics - Enhanced prerequisite system.

This module adds advanced unlock requirements to transformations:
- Random roll system for first transformations
- Failure tracking with bonus rolls
- Death witness trigger (Goku watching Krillin die moment)
- Gravity training integration
- Race-specific transformation events
"""

from __future__ import annotations
import random
import time


# ============================================================================
# FLAVOR TEXT FOR FAILED TRANSFORMATIONS
# ============================================================================

NEAR_MISS_MESSAGES = {
    "saiyan": [
        "{YYour hair flashes golden for an instant! Your eyes glow blue as a blazing aura surrounds your body... but then it fades away.{x",
        "{YYou feel the power surging within you, your muscles bulge, your aura blazes bright... but you can't hold it. The transformation slips away.{x",
        "{YGolden energy erupts around you, your scream builds... but nothing happens. The power dissipates into the air.{x",
        "{YYour body trembles as legendary energy surges through your veins. For a moment you think you've done it... but the transformation fails.{x",
    ],
    "half_breed": [
        "{YYou feel power surge through your veins! Golden light emanates from your body... but it fades.{x",
        "{YYour body trembles with energy! For a brief moment you sense something more... but it slips away.{x",
    ],
    "human": [
        "{CYour focus intensifies! You feel latent power stir within you... but it remains dormant.{x",
        "{CYou concentrate deeply! Energy builds within... but you cannot quite harness it.{x",
    ],
    "namekian": [
        "{GYour body pulses with green energy! Your Dragon Clan powers surge... but cannot breakthrough.{x",
        "{GYou feel your Namekian潜力 awaken! The energy flows through you... but fades away.{x",
    ],
    "majin": [
        "{MYour body swells with power! Pink energy erupts around you... but then contracts.{x",
        "{MThe Majin chaos energy builds! You feel your form destabilize... but stabilize too soon.{x",
    ],
    "android": [
        "{CInternal processors surge! Power output increases... but core safety limits engage.{x",
        "{CYour reactor output spikes! Maximum efficiency reached... but fails to breakthrough.{x",
    ],
    "biodroid": [
        "{GGenetic potential activates! Cell-like energy surges... but the evolution stalls.{x",
        "{GYour biodroid genome activates! Perfect cells form... but cannot stabilize.{x",
    ],
    "frost_demon": [
        "{cYour true form struggles to emerge! Icy energy explodes outward... but crystallizes too soon.{x",
        "{cFrost Demon power builds! Your body shifts... but cannot complete the transformation.{x",
    ],
    "grey": [
        "{WYour psychic focus intensifies! Mental energy surges... but cannot manifest physically.{x",
        "{WThe grey power awakens! You feel your limits strain... but cannot break through.{x",
    ],
    "kai": [
        "{YDivine energy gathers! The cosmos responds to your power... but the connection fades.{x",
        "{YGlowing sacred light emanates from you! Your Kai potential stirs... but remains sealed.{x",
    ],
}

# Progressive failure messages based on fail count
PROGRESSIVE_FAILURE_MESSAGES = [
    None,  # 0-4 failures
    "{yYou've felt this before... the golden flash, the surging power... but once again, it wasn't enough.{x",  # 5+
    "{RThe power is there! You KNOW it's there! But your body won't listen to you!{x",  # 10+
    "{rTears of frustration stream down your face as the golden aura fades once more...{x",  # 20+
    "{rYOU ALMOST HAD IT! The power is RIGHT THERE!{x",  # 30+
    "{rYour soul screams for release... but the transformation refuses to come.{x",  # 50+
]

# Death witness transformation buildup sequence
DEATH_WITNESS_BUILDSUP_MESSAGES = [
    "{YA nearby player falls! Your heart stops...{x",
    "{YImages of your past battles flash before your eyes...{x",
    "{RYou scream out in anguish! Energy begins to crackle around you!{x",
    "{YGolden light emanates from your body! Your hair begins to shift!{x",
    "{YThe ground cracks beneath your feet as power erupts!{x",
    "{RYOUR EYES TURN EMERALD GREEN!{x",
    "{YGOLDEN ENERGY EXPLODES OUTWARD!{x",
    "{YYou have ascended to SUPER SAIYAN!{x",
]


# ============================================================================
# CHARACTER ATTRIBUTE HELPERS
# ============================================================================

def _get_attr(character, attr_name: str, default=None):
    """Get a character attribute safely."""
    return getattr(character.db, attr_name, default)


def _set_attr(character, attr_name: str, value):
    """Set a character attribute safely."""
    setattr(character.db, attr_name, value)


# ============================================================================
# FAILURE TRACKING
# ============================================================================

def get_transformation_fail_count(character, form_key: str = None) -> int:
    """
    Get the number of failed transformation attempts.
    If form_key is None, returns total failures across all forms.
    """
    fail_counts = _get_attr(character, "trans_fail_counts", {})
    if form_key is None:
        return sum(fail_counts.values())
    return fail_counts.get(form_key, 0)


def register_transformation_failure(character, form_key: str):
    """
    Register a failed transformation attempt.
    This increases the chance of success for future attempts.
    """
    fail_counts = _get_attr(character, "trans_fail_counts", {})
    fail_counts[form_key] = fail_counts.get(form_key, 0) + 1
    _set_attr(character, "trans_fail_counts", fail_counts)
    
    # Also track total failures for bonus calculation
    total_fails = _get_attr(character, "trans_total_fails", 0) + 1
    _set_attr(character, "trans_total_fails", total_fails)
    
    # Track last failure time
    _set_attr(character, "trans_last_fail_time", time.time())


def get_failure_bonus_chance(character, form_key: str = None) -> float:
    """
    Calculate bonus chance based on failed attempts.
    - After 10 failures: +1% chance
    - After 25 failures: +2% chance  
    - After 50 failures: +3% chance
    """
    fails = get_transformation_fail_count(character, form_key)
    
    if fails >= 50:
        return 0.03
    elif fails >= 25:
        return 0.02
    elif fails >= 10:
        return 0.01
    return 0.0


def get_near_miss_message(character, race: str) -> str:
    """
    Get a near-miss flavor message based on race and failure count.
    """
    fail_count = get_transformation_fail_count(character)
    race_key = race.lower().replace("-", "_").replace(" ", "_")
    
    # Get race-specific messages or fallback
    messages = NEAR_MISS_MESSAGES.get(race_key, NEAR_MISS_MESSAGES["saiyan"])
    
    # Check for progressive failure messages
    if fail_count >= 50 and PROGRESSIVE_FAILURE_MESSAGES[5]:
        return PROGRESSIVE_FAILURE_MESSAGES[5]
    elif fail_count >= 30 and PROGRESSIVE_FAILURE_MESSAGES[4]:
        return PROGRESSIVE_FAILURE_MESSAGES[4]
    elif fail_count >= 20 and PROGRESSIVE_FAILURE_MESSAGES[3]:
        return PROGRESSIVE_FAILURE_MESSAGES[3]
    elif fail_count >= 10 and PROGRESSIVE_FAILURE_MESSAGES[2]:
        return PROGRESSIVE_FAILURE_MESSAGES[2]
    elif fail_count >= 5 and PROGRESSIVE_FAILURE_MESSAGES[1]:
        return PROGRESSIVE_FAILURE_MESSAGES[1]
    
    # Return random message from race pool
    return random.choice(messages)


# ============================================================================
# RANDOM ROLL SYSTEM
# ============================================================================

def check_transformation_roll(character, form_key: str, form_data: dict, race: str) -> tuple:
    """
    Check if a random roll transformation succeeds.
    
    Returns:
        (success: bool, message: str)
        
    Prerequisites that trigger roll:
    - roll_chance: base chance (e.g., 0.03 for 3%)
    - roll_trigger: condition that must be met (rage, health_below, etc.)
    """
    req = form_data.get("prerequisites", {})
    
    # Check if this form uses the roll system
    roll_chance = req.get("roll_chance")
    if roll_chance is None:
        # No roll required, allow transformation
        return True, ""
    
    # Check trigger conditions
    roll_trigger = req.get("roll_trigger", {})
    
    # Check rage requirement
    if roll_trigger.get("rage_min"):
        current_rage = _get_attr(character, "rage", 0)
        if current_rage < roll_trigger["rage_min"]:
            return False, f"Need at least {roll_trigger['rage_min']} rage to attempt this transformation."
    
    # Check health requirement (must be below certain percentage)
    if roll_trigger.get("health_max_pct"):
        hp_current = _get_attr(character, "hp_current", 100)
        hp_max = _get_attr(character, "hp_max", 100)
        hp_pct = (hp_current / hp_max) * 100 if hp_max > 0 else 100
        if hp_pct > roll_trigger["health_max_pct"]:
            return False, f"You need to be below {roll_trigger['health_max_pct']}% health to attempt this transformation."
    
    # Check PL requirement
    if roll_trigger.get("pl_min"):
        current_pl = _get_attr(character, "power_level", 0)
        if current_pl < roll_trigger["pl_min"]:
            return False, f"Need at least {roll_trigger['pl_min']:,} power level to attempt this transformation."
    
    # Calculate final chance with failure bonus
    bonus_chance = get_failure_bonus_chance(character, form_key)
    final_chance = roll_chance + bonus_chance
    
    # Perform the roll
    roll = random.random()
    
    if roll < final_chance:
        # Success! Clear failure count for this form
        fail_counts = _get_attr(character, "trans_fail_counts", {})
        if form_key in fail_counts:
            fail_counts[form_key] = 0
            _set_attr(character, "trans_fail_counts", fail_counts)
        return True, ""
    
    # Failure - register it
    register_transformation_failure(character, form_key)
    return False, get_near_miss_message(character, race)


# ============================================================================
# PL THRESHOLD UNLOCK (Android Mark Upgrades)
# ============================================================================

def check_pl_threshold_requirement(character, form_data: dict) -> tuple:
    """
    Check if PL threshold requirements are met.
    
    Prerequisites:
    - unlock_type: "pl_threshold" or "auto"
    - pl_min: minimum power level required
    """
    req = form_data.get("prerequisites", {})
    
    unlock_type = req.get("unlock_type")
    
    # Handle PL threshold (Android Mark upgrades)
    if unlock_type == "pl_threshold":
        pl_min = req.get("pl_min")
        if pl_min:
            current_pl = _get_attr(character, "power_level", 0)
            if current_pl < pl_min:
                return False, f"Your power level must reach {pl_min:,} to unlock this form."
    
    # Handle auto-unlock (Frieza race - just get stronger at thresholds)
    # This is similar to pl_threshold but without the message
    if unlock_type == "auto":
        pl_min = req.get("pl_min")
        if pl_min:
            current_pl = _get_attr(character, "power_level", 0)
            if current_pl < pl_min:
                return False, f"Your power level must reach {pl_min:,} to unlock this form."
    
    return True, ""


def get_android_mark(character) -> str:
    """
    Get the current Android Mark based on power level.
    Mark I: PL 1-4999
    Mark II: PL 5000-14999
    Mark III: PL 15000+
    """
    pl = _get_attr(character, "power_level", 0)
    
    if pl >= 15000:
        return "Mark III"
    elif pl >= 5000:
        return "Mark II"
    else:
        return "Mark I"


# ============================================================================
# ABSORPTION UNLOCK (Bio-Android)
# ============================================================================

def get_absorption_count(character) -> int:
    """Get the number of NPCs absorbed by a Bio-Android."""
    return _get_attr(character, "absorption_count", 0)


def register_absorption(character):
    """Register an absorption by a Bio-Android."""
    count = _get_attr(character, "absorption_count", 0)
    _set_attr(character, "absorption_count", count + 1)


def check_absorption_requirement(character, form_data: dict) -> tuple:
    """
    Check if absorption requirements are met (Bio-Android).
    
    Prerequisites:
    - unlock_type: "absorption"
    - absorbs_min: minimum number of NPCs to absorb
    """
    req = form_data.get("prerequisites", {})
    
    if req.get("unlock_type") != "absorption":
        # Not an absorption form, skip this check
        return True, ""
    
    absorbs_min = req.get("absorbs_min")
    if absorbs_min:
        current_absorbs = get_absorption_count(character)
        if current_absorbs < absorbs_min:
            return False, f"You must absorb {absorbs_min} beings to evolve. You have absorbed {current_absorbs}."
    
    return True, ""


# ============================================================================
# GRAVITY TRAINING INTEGRATION
# ============================================================================

def get_gravity_training_count(character) -> int:
    """Get the number of completed gravity training sessions."""
    return _get_attr(character, "gravity_training_count", 0)


def register_gravity_training(character):
    """Register a completed gravity training session."""
    count = _get_attr(character, "gravity_training_count", 0)
    _set_attr(character, "gravity_training_count", count + 1)


def check_gravity_training_requirement(character, form_data: dict) -> tuple:
    """
    Check if gravity training requirements are met.
    
    Prerequisites:
    - gravity_training_sessions: number of gravity sessions needed
    - brink_of_death_triggers: near-death experiences needed
    """
    req = form_data.get("prerequisites", {})
    
    if "gravity_training_sessions" in req:
        needed = req["gravity_training_sessions"]
        current = get_gravity_training_count(character)
        if current < needed:
            return False, f"Need {needed} gravity training sessions. You have completed {current}."
    
    if "brink_of_death_triggers" in req:
        needed = req["brink_of_death_triggers"]
        current = _get_attr(character, "brink_of_death_count", 0)
        if current < needed:
            return False, f"Need {needed} near-death experiences. You have {current}."
    
    # Check if fusion is required (for Namekians)
    if req.get("requires_fusion"):
        if not _get_attr(character, "namek_fused", False):
            return False, "You must fuse with a Namekian to unlock this form. Use 'fuse' when offered."
    
    return True, ""


# ============================================================================
# DEATH WITNESS TRIGGER
# ============================================================================

def get_witness_death_count(character) -> int:
    """Get the number of death witnesses that triggered transformation."""
    return _get_attr(character, "witness_death_transforms", 0)


def register_witness_death(character):
    """Register that character witnessed a death and transformed."""
    count = _get_attr(character, "witness_death_transforms", 0)
    _set_attr(character, "witness_death_transforms", count + 1)
    # Also set a timestamp
    _set_attr(character, "witness_death_recent_time", time.time())


def check_death_witness_trigger(character, form_data: dict) -> tuple:
    """
    Check if death witness trigger conditions are met.
    
    Prerequisites:
    - witness_death_trigger: True to enable
    - witness_chance: chance when witnessing death (default 20%)
    - pl_min: minimum PL needed
    - rage_min: minimum rage needed
    """
    req = form_data.get("prerequisites", {})
    
    if not req.get("witness_death_trigger"):
        return True, ""
    
    # Check if recently witnessed a death
    last_witness = _get_attr(character, "witness_death_recent_time", 0)
    if last_witness > 0:
        # Check if within valid window (e.g., 5 seconds)
        if time.time() - last_witness < 5:
            # Check other requirements
            if req.get("pl_min"):
                current_pl = _get_attr(character, "power_level", 0)
                if current_pl < req["pl_min"]:
                    return False, f"Need {req['pl_min']:,} PL to transform from witnessing death."
            
            if req.get("rage_min"):
                current_rage = _get_attr(character, "rage", 0)
                if current_rage < req["rage_min"]:
                    return False, f"Need {req['rage_min']} rage to transform from witnessing death."
            
            # Success - consume the trigger
            _set_attr(character, "witness_death_recent_time", 0)
            register_witness_death(character)
            return True, ""
    
    return True, ""


def trigger_death_witness_transform(character) -> bool:
    """
    Called when a player dies nearby. Check if this character
    should trigger a transformation.
    
    Returns True if transformation was triggered.
    """
    # Check if character has any forms that can use death witness
    from world.forms import FORMS, list_forms_for_race
    
    race = _get_attr(character, "race", "human")
    available_forms = list_forms_for_race(race)
    
    for form_key, form_data in available_forms:
        req = form_data.get("prerequisites", {})
        if not req.get("witness_death_trigger"):
            continue
        
        # Check PL and rage requirements
        current_pl = _get_attr(character, "power_level", 0)
        current_rage = _get_attr(character, "rage", 0)
        
        pl_min = req.get("pl_min", 1000)
        rage_min = req.get("rage_min", 20)
        
        if current_pl < pl_min or current_rage < rage_min:
            continue
        
        # Roll for transformation
        chance = req.get("witness_chance", 0.20)
        
        # Add failure bonus
        bonus = get_failure_bonus_chance(character, form_key)
        final_chance = chance + bonus
        
        if random.random() < final_chance:
            # Success! Set the witness trigger
            _set_attr(character, "witness_death_recent_time", time.time())
            _set_attr(character, "pending_witness_transform", form_key)
            return True
    
    return False


# ============================================================================
# RACE-SPECIFIC TRANSFORMATION EVENTS
# ============================================================================

def get_race_first_forms() -> dict:
    """
    Define the 'first transformation' for each race.
    These are the forms that use the random roll system.
    """
    return {
        "saiyan": "super_saiyan",
        "half_breed": "super_saiyan",
        "human": "max_power",
        "namekian": "giant_namekian",
        "majin": "super_majin",
        "android": "android_overclock",
        "biodroid": "biodroid_stage_two",
        "frost_demon": "frost_demon_true_form",
        "grey": "meditative_limit",
        "kai": "kai_unsealed",
        "truffle": "truffle_machine_merge",
    }


def is_first_transformation(character, form_key: str) -> bool:
    """Check if this is the first transformation for the character's race."""
    race = _get_attr(character, "race", "human")
    first_forms = get_race_first_forms()
    return first_forms.get(race) == form_key


def get_form_unlock_requirements(form_key: str) -> dict:
    """
    Get enhanced unlock requirements for a form.
    These complement the basic prerequisites in forms.py.
    """
    # Define roll-based transformations with their triggers
    roll_requirements = {
        "super_saiyan": {
            "roll_chance": 0.03,  # 3% base chance
            "roll_trigger": {
                "pl_min": 1000,
                "rage_min": 25,
                "health_max_pct": 50,  # Must be struggling
            },
        },
        "super_saiyan_grade2": {
            # Also uses roll but less strict
            "roll_chance": 0.05,
            "roll_trigger": {
                "rage_min": 30,
            },
        },
        "potential_unleashed": {
            # Human potential - requires focus, not rage
            "roll_chance": 0.10,
            "roll_trigger": {
                "health_max_pct": 30,  # Must be pushed
            },
        },
        "giant_namekian": {
            # Namekian giant form - needs battle pressure
            "roll_chance": 0.08,
            "roll_trigger": {
                "health_max_pct": 40,
            },
        },
        "super_majin": {
            # Majin transformation - anger-based
            "roll_chance": 0.05,
            "roll_trigger": {
                "rage_min": 30,
            },
        },
    }
    return roll_requirements.get(form_key, {})


# ============================================================================
# MASTERIES AND BONUSES
# ============================================================================

def calculate_form_mastery_bonus(character, form_key: str) -> dict:
    """
    Calculate various bonuses based on character history.
    
    Returns dict with:
    - roll_bonus: bonus to roll chance
    - duration_bonus: bonus to transformation duration
    - drain_reduction: reduction to ki drain
    """
    fail_count = get_transformation_fail_count(character, form_key)
    gravity_count = get_gravity_training_count(character)
    witness_count = get_witness_death_count(character)
    
    # Failure-based roll bonus
    roll_bonus = get_failure_bonus_chance(character, form_key)
    
    # Gravity training bonus (+2 seconds per session, max 60)
    duration_bonus = min(60, gravity_count * 2)
    
    # Witness death bonus (permanent +5% duration)
    if witness_count > 0:
        duration_bonus += 5
    
    # Drain reduction from gravity training (max 20%)
    drain_reduction = min(0.20, gravity_count * 0.02)
    
    return {
        "roll_bonus": roll_bonus,
        "duration_bonus": duration_bonus,
        "drain_reduction": drain_reduction,
    }


# ============================================================================
# COMBAT INTEGRATION HOOKS
# ============================================================================

def on_character_damaged(character, damage: int):
    """
    Called when character takes damage.
    Check for brink-of-death transformation trigger.
    """
    hp_current = _get_attr(character, "hp_current", 100)
    hp_max = _get_attr(character, "hp_max", 100)
    
    # Check if this damage brings them to brink of death
    if hp_current <= hp_max * 0.10:  # Below 10% HP
        # Register brink of death experience
        count = _get_attr(character, "brink_of_death_count", 0)
        _set_attr(character, "brink_of_death_count", count + 1)


def on_character_killed(character, victim):
    """
    Called when character kills something.
    Check if this triggers transformation for nearby witnesses.
    """
    from evennia import Object
    
    # Get all characters in the same location
    location = character.location
    if not location:
        return
    
    for obj in location.contents:
        if obj == character:
            continue
        if not hasattr(obj, "db"):
            continue
        
        # Check if it's a character (has power_level)
        if not hasattr(obj, "power_level"):
            continue
        
        # Trigger death witness for this character
        trigger_death_witness_transform(obj)


def on_rage_changed(character, old_rage: int, new_rage: int):
    """
    Called when character's rage changes.
    Can trigger transformation attempts at high rage.
    """
    # If rage spikes high, check for transformation roll
    if new_rage >= 50:  # Very high rage
        race = _get_attr(character, "race", "human")
        first_forms = get_race_first_forms()
        first_form = first_forms.get(race)
        
        if first_form:
            # Check if they meet PL requirements for first form
            pl = _get_attr(character, "power_level", 0)
            if pl >= 1000:  # SSJ PL requirement
                # Could auto-trigger roll here or just set a flag
                _set_attr(character, "rage_transformation_ready", first_form)
