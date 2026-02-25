# Namekian Fusion System - Technical Design

## Overview
When a player kills a Namekian NPC, 0.03% chance the dying Namekian offers to fuse with the player, granting +50% max ki permanently.

---

## Current Code to Modify

### 1. Where to Add Trigger
**File:** `src/fight.c`
**Function:** `death_corpse()` or `raw_kill()`
**Location:** After a player lands the killing blow on an NPC

```c
// Around line where victim is confirmed dead
if (!IS_NPC(victim) && IS_NPC(killer))
{
    // Check if victim is Namekian
    if (victim->race == race_lookup("namekian"))
        check_namekian_fusion_offer(killer, victim);
}
```

### 2. New Functions Needed

```c
// In src/fight.c - check for fusion offer
void check_namekian_fusion_offer(CHAR_DATA *ch, CHAR_DATA *victim);

// In src/fight.c - handle the fusion offer
void do_namekian_fusion_offer(CHAR_DATA *ch, CHAR_DATA *victim);

// In src/merc.h - add prototypes
void check_namekian_fusion_offer args((CHAR_DATA *ch, CHAR_DATA *victim));
void accept_namekian_fusion args((CHAR_DATA *ch));
void decline_namekian_fusion args((CHAR_DATA *ch));
```

---

## Data Structures

### Use Existing PC_DATA Field:
**Already exists in merc.h (line 1610):**
```c
CHAR_DATA *fusion_request;  // Player requesting fusion
```

### Add to PC_DATA (merc.h):
```c
int fusion_offer_timer;      // How long to respond (seconds)
int fusion_count;            // Number of fusions absorbed
bool namek_fused;            // Has absorbed a Namekian
```

---

## Function Flow

### 1. check_namekian_fusion_offer(ch, victim)
```
1. Check if victim is Namekian NPC
2. Roll 0.03% chance (number_range(1, 100000) <= 30)
3. If successful:
   a. Set ch->pcdata->fusion_offer = victim
   b. Set ch->pcdata->fusion_offer_timer = 60 (seconds)
   c. Send offer message to player
   d. Store offer data for later acceptance
4. Return
```

### 2. accept_namekian_fusion(ch)
```
1. Check if ch has valid fusion_offer
2. If valid:
   a. Apply +50% max_ki boost (ch->max_ki * 1.5)
   b. Apply +50% perm_ki boost
   c. Send success message
   d. Log the fusion
   e. Clear fusion_offer
3. If invalid:
   a. Send "offer expired" message
```

### 3. decline_namekian_fusion(ch)
```
1. Check if ch has valid fusion_offer
2. If valid:
   a. Send decline message
   b. Clear fusion_offer
```

---

## Commands Needed

### New Command: `fuse`
Add sub-options:
```
fuse accept    // Accept Namekian fusion offer
fuse decline   // Decline Namekian fusion offer
```

---

## Message Strings

### Offer Message:
```
{The dying Namekian gasps, falling to his knees...

"Wait! I cannot fight anymore... but I am not ready to die!

I offer myself to you! Let us become one! Our power will 
double! I will become your strength!"

Do you accept? (fuse accept/decline){x
```

### Accept Message:
```
{YThe Namekian's body begins to glow!

"Thank you... warrior. Let us become... stronger... together..."

The Namekian dissolves into green energy that flows into your 
body! You feel your power surge as two warriors become one!

{YYour max ki increases by 50%!{x
```

### Decline Message:
```
{y"Very well... I die with dignity. Thank you for this choice..."

The Namekian fades away, his spirit at peace.{x
```

### Expired Message:
```
{yThe Namekian's spirit has faded... the opportunity is lost.{x
```

---

## Implementation Steps

1. **Add PC_DATA fields** (merc.h)
2. **Add function prototypes** (merc.h)
3. **Implement check_namekian_fusion_offer()** (fight.c)
4. **Add accept/decline handlers** (fight.c)
5. **Add to do_fuse()** to handle new subcommands (fusion.c)
6. **Add trigger in raw_kill()** (fight.c)
7. **Test with spawned NPCs**

---

## Files to Modify

- `src/merc.h` - Add PC_DATA fields + prototypes
- `src/fight.c` - Add trigger + fusion functions
- `src/fusion.c` - Add accept/decline to do_fuse()

---

## Edge Cases

- Player already has fusion offer: reject new offer
- Namekian already fused: don't offer
- Player refuses: Namekian dies normally
- Timer expires: offer disappears
- Player disconnects: offer expires
