# Transformation Powerlevel Drain - Technical Design

## Overview
Transformations should consume powerlevel while active. When the player's current powerlevel drops too low, the transformation should revert automatically.

---

## How It Works

### 1. Powerlevel Drain Rate
- Base drain: 1% of max PL per minute while transformed
- Different rates per transformation tier:
  - SSJ1: 1% per minute
  - SSJ2: 2% per minute
  - SSJ3: 3% per minute
  - SSJ4: 4% per minute
  - SSJ5: 5% per minute

### 2. Revert Threshold
- When current PL drops below 20% of max PL, transformation reverts
- This prevents players from being stuck in transformation with no fighting power

### 3. Interaction with Mastery
- Mastery increases hold time but doesn't affect PL drain
- Player can still be drained out of transformation even at high mastery

---

## Implementation

### 1. Add drain rates to update_transformations() in update.c

```c
// Powerlevel drain rates per transformation
int drain_rates[] = {0, 1, 2, 3, 4, 5};  // Index 0 unused, SSJ1-5

// In update_transformations():
if (ch->trans_current >= TRANS_SSJ1 && ch->trans_current <= TRANS_SSJ5) {
    int mastery_idx = ch->trans_current - 1;
    int drain_rate = drain_rates[ch->trans_current];  // % per minute
    int drain_per_pulse = (ch->max_pl * drain_rate / 100) / 240;  // Divide by pulses per minute

    // Apply drain
    ch->nCurPl -= drain_per_pulse;
    if (ch->nCurPl < 0) ch->nCurPl = 0;

    // Check for low PL warning (20% threshold)
    if (ch->nCurPl < ch->max_pl * 20 / 100) {
        sendch("You feel too weak to maintain your transformation!\n\r", ch);
    }

    // Auto-revert if PL drops too low (10% threshold)
    if (ch->nCurPl < ch->max_pl * 10 / 100) {
        do_revert(ch, "");
        sendch("You're too exhausted to maintain your transformation!\n\r", ch);
    }
}
```

### 2. Adjust update frequency
- Currently runs every pulse (~0.25 seconds)
- Need to track when to apply drain (once per second, not every pulse)
- Add a counter or timestamp to track drain intervals

---

## Edge Cases

- Player at exactly 10% PL: Should revert immediately
- Player gains PL while transformed: Should still drain, but slower relative effect
- Multiple transformations: Only drain based on current transformation

---

## Files to Modify

- update.c - Add powerlevel drain in update_transformations()
- Possibly act_move.c - Show drain rate when transforming
