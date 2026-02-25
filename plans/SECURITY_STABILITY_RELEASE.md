# DBForged Security & Stability Release Plan

## Overview

This document outlines the implementation plan to address all critical and high-priority issues identified in the Technical Audit Report. This plan should be completed before any new feature development to ensure a stable, secure release-ready codebase.

---

## Priority 1: Critical Security Fixes

### 1.1 World Boss Damage Validation

**Issue**: Client can send arbitrary damage values - no server-side validation

**Location**: `world/tournaments.py:219-249`

**Fix Required**:
```python
def damage_world_boss(player_id: str, damage: int):
    # REMOVE: current = _world_boss_state["damage_dealt"].get(player_id, 0)
    # REMOVE: _world_boss_state["damage_dealt"][player_id] = current + damage
    
    # IMPLEMENT: Server calculates damage based on player's actual combat stats
    from world.power import compute_current_pl
    player = get_player_object(player_id)  # Need helper function
    if not player:
        return {"success": False, "reason": "Player not found"}
    
    # Calculate actual damage the player dealt this tick
    actual_damage = calculate_world_boss_damage(player)
    
    # Add to total
    current = _world_boss_state["damage_dealt"].get(player_id, 0)
    _world_boss_state["damage_dealt"][player_id] = current + actual_damage
```

**Status**: [ ] Not Started

---

### 1.2 Target Validation

**Issue**: Target ID can be set to any player globally, no room validation

**Location**: `commands/db_commands.py:419-438`, `typeclasses/characters.py:`

**Fix Required**:
```python
# In CmdTarget.func():
def func(self):
    caller = self.caller
    if not self.args:
        caller.msg("Usage: target <name>")
        return
        
    target = _search_target(caller, self.args.strip())
    if not target or target == caller:
        return
    
    # ADD: Validate target is in same room
    if target.location != caller.location:
        caller.msg("You can only target someone in your current location.")
        return
    
    # ADD: Validate target is a valid combatant
    if not hasattr(target, "db") or target.db.hp_current is None:
        caller.msg("You cannot attack that.")
        return
    
    caller.db.combat_target = target.id
    caller.msg(f"Target set to {target.key}.")
    if hasattr(target, "get_current_pl"):
        emit_entity_delta(target, recipients=[caller])
```

**Status**: [ ] Not Started

---

### 1.3 HP/KI Information Disclosure

**Issue**: Entity delta broadcasts exact HP/KI to all players in room - enables metagaming

**Location**: `world/events.py:106-142`

**Fix Required**:
```python
def emit_entity_delta(entity, recipients=None):
    stats = _safe_stats(entity)
    
    # MODIFY: Don't broadcast exact HP/KI to observers
    # Only send to self (for HUD)
    # For others, send only: name, position, form, visible status
    
    payload_self = {
        "entity": {
            "id": entity.id,
            "name": entity.key,
            "room": entity.location.id if entity.location else None,
            "position": {"x": coords[0], "y": coords[1], "layer": coords[2]},
            "sprite_id": entity.db.sprite_id or "sprite_humanoid_default",
            # FULL stats for self
            **stats
        }
    }
    
    payload_observer = {
        "entity": {
            "id": entity.id,
            "name": entity.key,
            "room": entity.location.id if entity.location else None,
            "position": {"x": coords[0], "y": coords[1], "layer": coords[2]},
            "sprite_id": entity.db.sprite_id or "sprite_humanoid_default",
            # LIMITED stats for observers - no HP/KI
            "active_form": stats.get("active_form"),
            "form_info": stats.get("form_info"),
            "displayed_pl": stats.get("displayed_pl"),  # Suppressed PL only
        }
    }
    
    # Send full to self
    emit_event(entity, "player_frame", payload_self)
    
    # Send limited to room
    if entity.location:
        emit_event_room(entity.location, "entity_delta", payload_observer, exclude=[entity])
```

**Status**: [ ] Not Started

---

### 1.4 Guild Open Join Bypass

**Issue**: Any player can join any guild without invitation

**Location**: `world/guilds.py:345-376`

**Fix Required**:
```python
def join_guild(guild: Guild, player_id: str, player_name: str) -> dict:
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    members = guild.db.members or {}
    
    if player_id in members:
        return {"success": False, "reason": "Already a member"}
    
    if len(members) >= MAX_GUILD_MEMBERS:
        return {"success": False, "reason": "Guild is full"}
    
    # REMOVE: The "open join" bypass
    # ADD: Check for invitation required
    invitations = guild.db.invitations or []
    if player_id not in invitations:
        return {"success": False, "reason": "You must be invited to join this guild"}
    
    # Add member
    members[player_id] = {
        "name": player_name,
        "role": GUILD_ROLE_MEMBER,
        "joined": time.time(),
    }
    guild.db.members = members
    
    # Remove invitation
    guild.remove_invitation(player_id)
    
    return {"success": True, "guild": guild.to_dict()}
```

**Status**: [ ] Not Started

---

### 1.5 Tournament Entry Cost

**Issue**: No entry fee for tournaments - can spam join

**Location**: `world/tournaments.py:130-140`

**Fix Required**:
```python
TOURNAMENT_ENTRY_COST = 500  #zeni

def join_tournament(player) -> dict:
    """Add a player to the tournament."""
    if not _tournament_state["signup_open"]:
        return {"success": False, "reason": "Signups are closed"}
    
    player_id = player.id
    if player_id in _tournament_state["participants"]:
        return {"success": False, "reason": "Already signed up"}
    
    # ADD: Check player has enough zeni
    player_zeni = getattr(player.db, 'zeni', 0) or 0
    if player_zeni < TOURNAMENT_ENTRY_COST:
        return {"success": False, "reason": f"Need {TOURNAMENT_ENTRY_COST} zeni to enter"}
    
    # Deduct entry fee
    player.db.zeni = player_zeni - TOURNAMENT_ENTRY_COST
    
    # Add to prize pool
    _tournament_state["prize_pool"] = _tournament_state.get("prize_pool", 0) + TOURNAMENT_ENTRY_COST
    
    _tournament_state["participants"].append(player_id)
    return {"success": True, "participants": len(_tournament_state["participants"])}
```

**Status**: [ ] Not Started

---

### 1.6 Zenkai/Regen Farm Prevention

**Issue**: Players can intentionally die repeatedly to farm Zenkai boosts and regeneration

**Location**: `typeclasses/characters.py:406-444`

**Fix Required**:
```python
def handle_defeat(self, source=None, kind="attack"):
    from world.combat import disengage, stop_charging

    stop_charging(self, interrupted=True)
    disengage(self)
    self.db.active_form = None
    
    # ADD: Track defeat count per time window
    now = time.time()
    defeat_history = list(self.db.defeat_history or [])
    # Remove defeats older than 1 hour
    defeat_history = [t for t in defeat_history if now - t < 3600]
    
    # ADD: If more than 3 defeats in 1 hour, reduce rewards
    recent_defeat_count = len(defeat_history)
    defeat_history.append(now)
    self.db.defeat_history = defeat_history
    
    # Reduced rewards if farming
    reward_reduction = 1.0
    if recent_defeat_count >= 3:
        reward_reduction = 0.5  # 50% reduction
    if recent_defeat_count >= 5:
        reward_reduction = 0.25  # 75% reduction
    if recent_defeat_count >= 10:
        reward_reduction = 0.0  # No rewards
    
    # Apply reduced rewards
    self.db.hp_current = max(1, int(self.db.hp_max * 0.55 * reward_reduction))
    self.db.ki_current = max(1, int(self.db.ki_max * 0.40 * reward_reduction))
    
    # Zenkai Boost - reduced/f disabled if farming
    race = (self.db.race or "").lower()
    if race in {"saiyan", "half_breed"} and reward_reduction > 0:
        zenkai_count = getattr(self.db, 'zenkai_count', 0) or 0
        self.db.zenkai_count = zenkai_count + 1
        
        zenkai_bonus = min(0.15, 0.04 + (zenkai_count * 0.01)) * reward_reduction
        if zenkai_bonus > 0:
            self.add_status("zenkai_boost", 600, pl_bonus=1.0 + zenkai_bonus)
            self.msg(f"|g>>> ZENKAI BOOST! <<<|n (+{zenkai_bonus*100:.0f}% PL for 10 min)")
    
    # Regeneration - reduced if farming
    if race in {"namekian", "majin", "biodroid"} and reward_reduction > 0:
        regen_bonus = getattr(self.db, 'regen_level', 0) or 0
        regen_heal = int(self.db.hp_max * (0.08 + regen_bonus * 0.02) * reward_reduction)
        self.db.hp_current = min(self.db.hp_max, self.db.hp_current + regen_heal)
        self.db.regen_level = regen_bonus + 1
    
    # ... rest of method
```

**Status**: [ ] Not Started

---

## Priority 2: Architecture Improvements

### 2.1 Tournament/World Boss Persistence

**Issue**: Tournament and world boss state lost on server restart

**Location**: `world/tournaments.py:23-50`

**Fix Required**:
- Create Evennia Script or GlobalScript to persist state
- OR store state in Django database via Evennia's Attribute system
- Implement save/load functions

**Implementation**:
```python
# New file: world/tournament_persistence.py

from evennia import DefaultScript

class TournamentStateScript(DefaultScript):
    """Persists tournament and world boss state"""
    
    def at_script_creation(self):
        self.key = "tournament_state"
        self.persistent = True
        
    def get_tournament_state(self):
        return self.db.tournament_state or copy.deepcopy(_default_tournament_state)
    
    def set_tournament_state(self, state):
        self.db.tournament_state = state
        
    def get_world_boss_state(self):
        return self.db.world_boss_state or copy.deepcopy(_default_world_boss_state)
    
    def set_world_boss_state(self, state):
        self.db.world_boss_state = state
```

**Status**: [ ] Not Started

---

### 2.2 Split commands/db_commands.py

**Issue**: 3000 lines in single file - unmaintainable

**Solution**: Split into logical modules

**Implementation**:
```
commands/
├── __init__.py
├── command.py
├── commandset.py
├── default_cmdsets.py
├── db_commands.py          # Keep base/shared functions only
├── combat_cmds.py          # NEW: attack, flee, charge, guard, counter
├── character_cmds.py       # NEW: stats, profile, transform
├── social_cmds.py          # NEW: guild, talk, quests
├── movement_cmds.py        # NEW: fly, teleport, grid movement
├── admin_cmds.py           # NEW: spawn, teleport ( Builders)
└── utility_cmds.py        # NEW: help, hud, scan, sense
```

**Status**: [ ] Not Started

---

### 2.3 Fix Guild Leader Lookup Import Error

**Issue**: `_get_leader_name()` catches wrong exception

**Location**: `world/guilds.py:244-255`

**Fix Required**:
```python
def _get_leader_name(self) -> str:
    """Get the leader's name."""
    from evennia.objects.models import ObjectDB
    from django.core.exceptions import ObjectDoesNotExist  # ADD THIS
    
    leader_id = self.db.leader
    if leader_id:
        try:
            account = ObjectDB.objects.get(id=int(leader_id))
            if account:
                return account.key
        except (ValueError, ObjectDoesNotExist):  # FIX: Use correct exception
            pass
    return "Unknown"
```

**Status**: [ ] Not Started

---

### 2.4 Combat Handler Object Lookup Safety

**Issue**: Potential AttributeError when objects deleted during iteration

**Location**: `world/combat.py:130-139`

**Fix Required**:
```python
def _iter_ids(self, idset):
    stale = set()
    for obj_id in set(idset):
        try:
            obj = _obj(obj_id)
            if obj and hasattr(obj, 'location') and obj.location:  # ADD: safer checks
                yield obj
            else:
                stale.add(obj_id)
        except Exception as e:  # ADD: catch any errors
            logger.log_warning(f"Error iterating combatant {obj_id}: {e}")
            stale.add(obj_id)
    
    for obj_id in stale:
        idset.discard(obj_id)
```

**Status**: [ ] Not Started

---

### 2.5 Input Validation Improvements

**Issue**: Command arguments have minimal validation

**Implementation Plan**:
- Add validation wrapper for all command arguments
- Sanitize Evennia markup from user input
- Add length limits to all string inputs

**Status**: [ ] Not Started

---

## Priority 3: Code Quality

### 3.1 Remove Dead Code

**Issue**: Empty classes and unused modules

**Items**:
- [ ] Remove `typeclasses/objects.py` ObjectParent empty class (or add actual code)
- [ ] Remove `world/content_validation.py` or integrate into startup
- [ ] Remove commented-out code in `commands/command.py`

**Status**: [ ] Not Started

---

### 3.2 Move Static Data to JSON

**Issue**: Form/technique/quest definitions in Python code

**Implementation**:
```
world/
├── data/
│   ├── forms.json
│   ├── techniques.json
│   ├── racials.json
│   └── quests.json
├── forms.py    # Load from JSON
├── techniques.py
├── racials.py
└── quests.py
```

**Status**: [ ] Not Started

---

### 3.3 Add Startup Validation

**Issue**: Content validation module exists but not used

**Fix**: Call `validate_all_content()` at server startup

**Location**: `server/conf/at_server_startstop.py`

**Status**: [ ] Not Started

---

## Implementation Checklist

### Security Fixes (Must Complete Before Release)
- [x] 1.1 World Boss Damage Validation
- [x] 1.2 Target Validation
- [x] 1.3 HP/KI Information Disclosure
- [x] 1.4 Guild Open Join Fix
- [x] 1.5 Tournament Entry Cost
- [x] 1.6 Zenkai/Regen Farm Prevention

### Architecture (Should Complete Before Release)
- [x] 2.1 Tournament/World Boss Persistence
- [ ] 2.2 Split db_commands.py (Deferred - low priority, technical debt)
- [x] 2.3 Fix Guild Import Error
- [x] 2.4 Combat Handler Safety
- [ ] 2.5 Input Validation (Deferred - can be done incrementally)

### Code Quality (Nice to Have)
- [ ] 3.1 Remove Dead Code (Deferred - low impact)
- [ ] 3.2 Move Static Data to JSON (Deferred - refactor task)
- [x] 3.3 Add Startup Validation

---

## Timeline Recommendation

| Week | Focus |
|------|-------|
| Week 1 | Security fixes (1.1 - 1.6) |
| Week 2 | Architecture (2.1 - 2.4) |
| Week 3 | Architecture (2.5) + Code Quality |
| Week 4 | Testing and polish |

---

## Dependencies

- Security fixes (1.1-1.6) are independent and can be parallelized
- Architecture improvements build upon security fixes
- Code quality items are lowest priority

---

## Success Criteria

- [ ] No CRITICAL or HIGH severity vulnerabilities
- [ ] Tournament state persists across restarts
- [ ] All commands properly validate input
- [ ] Commands split into maintainable modules
- [ ] Code passes basic lint checks
