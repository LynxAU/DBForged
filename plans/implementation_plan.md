# DBForged Implementation Plan

## Overview
This plan is derived from the DBZ bible (`EVENNIA_DBZ_DESIGN.md`) and organizes implementation into 12 categories that can be worked on sequentially or in parallel where dependencies allow.

## Categories (Execution Order)

### Category 1: Transformation Master System (Core)
Priority: HIGH - Core combat mechanic

1.1 Add trans_mastery field to Character typeclass (ListField for SSJ1-5, 0-100)
1.2 Add trans_start_time and trans_current fields to Character
1.3 Implement transformation timeout logic (60s base + mastery bonus)
1.4 Add PL drain per minute while transformed (1-5% based on form tier)
1.5 Add mastery gain while transformed (+1 per 10 seconds)
1.6 Add warning messages at 80% ("aura flickers") and 90% ("transformation slipping!")
1.7 Add auto-revert at 100% with "transformation fades" message
1.8 Add mastery command to display transformation mastery levels
1.9 Integrate with existing forms.py (already has drain_tick, drain_tech)

### Category 2: Kaioken Hold-Down System
Priority: HIGH - Core combat mechanic

2.1 Implement Kaioken multiplier based on hold time (x2 per second, max x20)
2.2 Add self-damage based on elapsed² (1, 4, 9, 16... 100)
2.3 Add warning at 5+ seconds ("body is straining!")
2.4 Force revert if HP drops too low
2.5 Store kaioken_multiplier for damage calculations

### Category 3: Beam Clash System
Priority: HIGH - Core combat mechanic

3.1 Create BeamClash class to manage beam struggles
3.2 Implement beam collision detection
3.3 Add push command with timing bonus system
3.4 Implement position decay toward center
3.5 Add winner/loser resolution (damage + knockback)
3.6 Add beam struggle visual indicators

### Category 4: Spirit Bomb & Flurry Attacks
Priority: MEDIUM - Advanced combat

4.1 Implement Spirit Bomb charge command (10-30 second charge)
4.2 Calculate damage based on charge time (PL * 0.5 * multiplier)
4.3 Add interrupt mechanic (caster takes damage if interrupted)
4.4 Implement room-wide AoE effect
4.5 Add cinematic messages during charge
4.6 Implement Flurry Attack (3-5 rapid strikes at 50% damage each)
4.7 Add random flurry trigger in combat

### Category 5: Ultra Instinct Death Trigger
Priority: MEDIUM - Advanced combat

5.1 Add 20% chance trigger when HP < 10%
5.2 Auto-trigger highest available transformation
5.3 Add 1-2 second invulnerability window
5.4 Add 30-second boosted stats duration
5.5 Reset HP to 50% after effect ends

### Category 6: Namekian Fusion System
Priority: MEDIUM - Special system

6.1 Add fusion trigger on Namekian NPC kill (0.03% chance)
6.2 Implement fusion offer message with accept/decline
6.3 Add fuse accept/decline commands
6.4 Apply +50% max KI on fusion accept
6.5 Set namek_fused flag
6.6 Handle edge cases (expired offers, already fused)

### Category 7: Energy Sensing / Scan Command
Priority: MEDIUM - Utility

7.1 Implement sense/scan command
7.2 Display power levels of all characters in room
7.3 Show status (fighting/resting)
7.4 Add danger indicator for enemies above player's PL
7.5 Implement ki sense for detecting hidden enemies

### Category 8: Mobility Systems
Priority: MEDIUM - Utility

8.1 Implement timeskip command (teleport behind target)
8.2 Add PL requirement check (50% of target's PL)
8.3 Implement position swap mechanic
8.4 Add teleport command (save/lock location)
8.5 Implement Instant Transmission (teleport to ally)

### Category 9: Dragon Ball System
Priority: MEDIUM - Endgame content

9.1 Create Dragon Ball objects (1-7)
9.2 Implement collection tracking
9.3 Add summon_shenron command when all 7 collected
9.4 Implement Shenron appearance (ASCII art)
9.5 Create wish system (5 wishes)
9.6 Implement wish effects (PL boost, stats, transformation unlock, revive, knowledge)

### Category 10: Aura & Visual Effects
Priority: LOW - Polish

10.1 Add aura display for transformed characters (ANSI)
10.2 Add aura HTML/CSS for web client
10.3 Implement hair color changes for SSJ forms
10.4 Add visual shaders (electric arcs for SSJ2, violent gold for SSJ3)
10.5 Implement automap system with sector symbols

### Category 11: Planet Cracker (Endgame)
Priority: LOW - Endgame

11.1 Add planet cracker technique (requires 1M+ PL)
11.2 Implement 10% learn chance
11.3 Add room destruction mechanic
11.4 Add once-per-day usage limit
11.5 Add exhaustion penalty if miss (1 hour)

### Category 12: Training Partners
Priority: LOW - Content

12.1 Create trainer NPCs (Roshi, King Kai, Guru, Whis)
12.2 Implement train with <npc> command
12.3 Add XP bonus system (1x-3x based on trainer)
12.4 Implement technique learning from trainers

## Already Implemented (Don't Repeat)
- Character data model (PL, Ki, HP, stats)
- Race system (11 races in racials.py)
- Racial traits (33 total - 3 per race)
- Technique registry (comprehensive in techniques.py)
- Transformation forms (SSJ1-4, Kaioken, Potential Unleashed in forms.py)
- Quest system (in quests.py)
- Basic combat system
- Web client integration
- LSSJ (Legendary Super Saiyan)

## Parallelization Notes
- Categories 1-3 should be done sequentially (core combat)
- Categories 4-8 can be done in parallel (independent systems)
- Categories 9-12 can be done in parallel (later content)

## Important Notes
- Each task must be launch-ready before moving to next category
- Do NOT delete any existing files
- Use existing code patterns from the codebase
- Test thoroughly before marking complete
