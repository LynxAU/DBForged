# DB Arena 2 - System Enhancement Plan

## Executive Summary

This document outlines the identified issues and proposed enhancements for DB Arena 2, a Dragon Ball Z themed MUD built on the ROM 2.4 codebase. The analysis revealed multiple areas requiring attention, from security concerns to system enhancements.

---

## Issue 1: Input Sanitization (Security Priority)

### Current Problem
- **Location**: [`src/act_info.c:2464`](src/act_info.c:2464)
- **FIXME Comment**: "Need to come up with a centralized user input sanitization scheme"
- **Problem**: Player titles and string inputs lack proper length checking before use
- **Risk**: Potential buffer overflow or injection vulnerabilities

### Proposed Fix
Create a centralized input sanitization module with the following functions:

```c
// In a new file: src/sanitize.c
char *sanitize_string(const char *input, int max_length);
char *strip_color_codes(const char *input);
bool validate_input_length(const char *input, int min_len, int max_len);
char *sanitize_filename(const char *input);
```

**Implementation Approach**:
1. Create `sanitize.h` with function prototypes
2. Implement `sanitize.c` with:
   - String truncation to max length
   - Color code stripping (`{x`, `{r`, etc.)
   - Special character escaping
   - Newline/control character removal
3. Update all input-handling functions to use these sanitizers
4. Focus initially on `do_title()` and `do_description()` commands

---

## Issue 2: Debug System Expansion

### Current Problem
- **Location**: [`src/debug.c`](src/debug.c:1)
- **Current State**: Nearly empty - only contains `varlimit` command
- **Problem**: Limited tooling to debug runtime issues
- **Context**: 300+ bug log points in codebase, but no way to inspect game state

### Proposed Enhancement

Expand [`src/debug.c`](src/debug.c:1) with the following commands:

#### 2.1 Memory Debugging Commands
```
memstat          - Show memory allocation summary
memlist          - List all allocated structures
memcheck         - Run memory integrity check
```

#### 2.2 Entity Tracking
```
debug chars      - Show all active characters
debug mobs       - Show all mobs in game
debug objects    - Show object counts by type
debug players    - Show connected players with details
```

#### 2.3 Runtime State Inspection
```
debug rooms      - Show room statistics
debug areas      - Show area loading status
debug fighting   - Show all combat instances
debug updates    - Show pending update queue
```

#### 2.4 Performance Profiling
```
debug timers     - Show function execution times
debug network    - Show socket/connection stats
```

**Proposed Architecture**:
```c
// src/debug.c structure
void memstat(CHAR_DATA *ch, char *argument);
void debug_chars(CHAR_DATA *ch, char *argument);
void debug_mobs(CHAR_DATA *ch, char *argument);
// ... etc

// Use existing log infrastructure
// Add debug levels: DEBUG_BRIEF, DEBUG_NORMAL, DEBUG_VERBOSE
```

---

## Issue 3: Combat System Review

### Current Problems

#### 3.1 Damage Cap Issue
- **Location**: [`src/fight.c:688`](src/fight.c:688)
- **Issue**: Damage capped at 2500 with bug log
- **Impact**: Limits high-level combat effectiveness
- **Fix**: Remove arbitrary cap, implement proper scaling

#### 3.2 Group Gain Calculation
- **Location**: [`src/fight.c:1782`](src/fight.c:1782)
- **Issue**: Logged when members == 0, defaults to 1
- **Fix**: Proper null-check handling

#### 3.3 Damage Message Cleanup
- **Location**: [`src/fight.c:2064`](src/fight.c:2064)
- **Issue**: Bad dt (damage type) triggers bug log
- **Fix**: Add default case handling

### Proposed Enhancement: Combat Analytics

Add a combat logging and statistics system:

```c
// In fight.c or new combat_stats.c
typedef struct CombatStats {
    int total_damage_dealt;
    int total_damage_received;
    int kills;
    int deaths;
    int hits_landed;
    int hits_missed;
    time_t combat_start;
} COMBAT_STATS;

// Commands:
// combatlog    - Show recent combat events
// combatstats  - Show personal/room/global stats
// damage       - Debug damage calculations
```

---

## Issue 4: Save/Load System Edge Cases

### Current Problems

#### 4.1 Character Invalidation
- **Location**: [`src/save.c:119`](src/save.c:119)
- **Issue**: Attempting to save invalidated character
- **Fix**: Add validation check at save entry point

#### 4.2 Unknown Skill Handling
- **Location**: [`src/save.c:825`](src/save.c:825), [`src/save.c:1075`](src/save.c:1075)
- **Issue**: Unknown skills trigger bug logs
- **Fix**: Graceful fallback with player notification

#### 4.3 Object Nesting
- **Location**: [`src/save.c:1508`](src/save.c:1508)
- **Issue**: Bad nest levels logged
- **Fix**: Validate nesting on load, cap at MAX_NEST

### Proposed Enhancement: Save System Robustness

Add save validation and recovery:

```c
// New functions in save.c
bool validate_pfile(CHAR_DATA *ch);
bool recover_corrupted_pfile(CHAR_DATA *ch, FILE *fp);
void backup_pfile(const char *name);

// Auto-backup before save
// Checksum validation
// Version migration support
```

---

## Issue 5: Random/Procedural Generation

### Current State
- **Location**: [`src/rand.c`](src/rand.c:1)
- **Features**: Map generation, random weapon/armor creation
- **Potential**: Could be expanded for more content

### Proposed Enhancement

Expand [`src/rand.c`](src/rand.c:1) capabilities:

#### 5.1 Quest Generation
- Random quest generation system
- Dynamic objectives based on player level
- Rewards scaling

#### 5.2 Event System
- Random world events (tournaments, rare spawns)
- Seasonal events framework

---

## Implementation Priority Matrix

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Input Sanitization | Medium | Security |
| 2 | Debug System | High | Development |
| 3 | Combat Cleanup | Low | Stability |
| 4 | Save System | Medium | Stability |
| 5 | Random Gen | High | Content |

---

## Notes

- All changes should maintain backward compatibility with existing player files
- Test thoroughly after each modification
- Consider adding #ifdef DEBUG sections for development-only code
- Document any new commands in help files

---

*Generated for DB Arena 2 Enhancement Project*
