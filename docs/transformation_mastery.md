# Transformation Mastery System - Technical Design

## Overview
Transformations should require mastery - the more you use them, the longer you can hold them. At max mastery, you can hold transformations indefinitely.

---

## How It Works

### 1. Mastery Levels (0-100)
- Starts at 0 for each transformation tier
- Increases by 1 for every 10 seconds spent transformed
- Max mastery = 100 (can hold transformation indefinitely)

### 2. Transformation Duration Formula
```
Base duration = 60 seconds (1 minute)
Bonus from mastery = (mastery / 100) * 240 seconds (4 minutes)
Max duration = 300 seconds (5 minutes) at 0 mastery
            = 300 seconds (5 minutes) at 100 mastery (indefinite)
```

Actually, simpler formula:
- At 0 mastery: 60 seconds
- Each mastery point adds 2.4 seconds- At 100 mastery: 300 seconds (indefinite with refresh)

### 3. Mastery Increase
- While transformed, gain +1 mastery per 10 seconds
- Only counts while actively transformed (not reverted)
- Different mastery tracking for SSJ1, SSJ2, SSJ3, SSJ4, SSJ5

### 4. Flavor Text at Low Power
When PL drops near the limit:
- At 80%: "Your golden aura flickers..."
- At 90%: "You feel your transformation slipping!"
- At 100%: Transform reverts automatically

---

## Data Structures

### In CHAR_DATA (not PC_DATA - it's temporary):
```c
int trans_timer[5];          // How long each transformation can be held (seconds)
int trans_elapsed[5];        // How long currently transformed (seconds)
bool trans_active[5];        // Which transformation is currently active
```

Actually, we already have trans_count which is used for different things. Let's use a simpler approach:

### Simpler Approach - Use trans_mastery directly:
```c
int trans_mastery[5];        // Mastery level 0-100 for SSJ1-5
```

### Add trans_start_time to track when transform began:
```c
int trans_start_time;        // When current transformation started
int trans_current;           // Which transformation is active (-1 = none)
```

---

## Implementation

### 1. When transforming (do_ssj1, do_ssj2, etc.):
```c
// Record start time
ch->trans_start_time = current_time;
ch->trans_current = TRANS_SSJ1;

// Show mastery info
if (ch->trans_mastery[0] > 0) {
    printf_to_char(ch, "Your SSJ1 mastery is %d%%. You can hold this form for %d seconds.\n\r",
        ch->trans_mastery[0], 60 + ch->trans_mastery[0] * 2);
}
```

### 2. In update.c - check transformation timeout:
```c
void update_transformations() {
    for each player {
        if (ch->trans_current != -1) {
            int elapsed = current_time - ch->trans_start_time;
            int max_time = 60 + ch->trans_mastery[ch->trans_current] * 2;
            
            // Check for low power warnings
            if (elapsed > max_time * 0.8 && elapsed < max_time * 0.8 + 1) {
                sendch("Your golden aura flickers...\n\r", ch);
            }
            else if (elapsed > max_time * 0.9 && elapsed < max_time * 0.9 + 1) {
                sendch("You feel your transformation slipping!\n\r", ch);
            }
            
            // Time's up!
            if (elapsed >= max_time) {
                // Revert transformation
                do_revert(ch, "");
                sendch("Your transformation fades away...\n\r", ch);
            }
            // Still transformed - gain mastery
            else if (elapsed > 0 && elapsed % 10 == 0) {
                ch->trans_mastery[ch->trans_current]++;
                if (ch->trans_mastery[ch->trans_current] > 100)
                    ch->trans_mastery[ch->trans_current] = 100;
            }
        }
    }
}
```

---

## Commands

### New Command: `mastery` or `trans mastery`
```
mastery           - Show mastery for all forms
mastery ssj1    - Show SSJ1 mastery details
```

---

## Display

### Score/Status Display:
```
Transformations:
  SSJ1: Mastery 45% (can hold 168 seconds)
  SSJ2: Mastery 20% (can hold 108 seconds)
  SSJ3: Mastery 0%  (can hold 60 seconds)
```

---

## Files to Modify

- merc.h - Add trans_mastery[], trans_start_time, trans_current
- act_move.c - Modify do_ssj1-5 to record start time
- update.c - Add transformation timeout checking
- act_info.c - Show mastery in score/status

---

## Edge Cases

- Player logs out while transformed: Reset timer on login
- Player is killed while transformed: Keep mastery, reset timer
- Multiple transformations: Only one at a time, mastery is per-tier
