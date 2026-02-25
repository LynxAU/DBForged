# Charge Ability System - Technical Design

## Overview
A charge ability that allows players to store up to 2 charges and unleash them for bonus damage or effects.

---

## How It Works

### 1. Charge Mechanics
- Player can store up to 2 charges
- Charges are consumed to perform charged attacks
- Charges regenerate over time (1 charge per 30 seconds)

### 2. Commands
- `charge` - Gain a charge (if not at max)
- `discharge` - Release all charges as a power blast

### 3. Integration with Combat
- Charged attacks deal bonus damage based on number of charges
- 1 charge: +25% damage
- 2 charges: +50% damage + knockback effect

---

## Data Structures

### In PC_DATA:
```c
int charge_count;    // Current charges (0-2)
int charge_timer;   // Time until next charge
```

---

## Implementation

### 1. Add fields to PC_DATA in merc.h

### 2. Create do_charge and do_discharge commands in act_move.c

### 3. Integrate with combat system
- Modify damage calculation to check for charges
- Apply bonus damage when charges are used

---

## Files to Modify

- merc.h - Add PC_DATA fields
- act_move.c - Add charge/discharge commands
- fight.c - Apply charge bonus to damage
