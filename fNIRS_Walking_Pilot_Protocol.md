# fNIRS Walking Pilot Protocol

**Date:** 11.04.2026___________________  
**Subject ID:** 01___________________  
**Experimenter:** Adam Emile Aske___________________  
**fNIRS System:** NIRx NIRSport2___________________  
**Sampling Rate:** ___________________

---

## Overview

This protocol tests fNIRS signal quality during four gait-related conditions across **3 rounds**. Each round consists of four sub-modules performed in fixed order. The block-design interrupted walking module (Module 4) is controlled by `walking.py`, which sends LSL triggers and audio cues.

| Module | Condition | Duration |
|--------|-----------|----------|
| 1 | Quiet sitting | 3 min |
| 2 | Quiet standing | 3 min |
| 3 | Continuous walking (around lab) | 3 min |
| 4 | Block-design interrupted walking (`walking.py`) | ~10 blocks, variable duration |

**Total estimated time per round:** ~15–20 min (depending on Module 4 randomisation)  
**Total estimated session time:** ~50–65 min including setup and breaks

---

## Pre-experiment checklist

- [ ] fNIRS cap fitted and channels verified
- [ ] LSL stream confirmed (`Trigger` stream visible in Lab Recorder)
- [ ] Lab Recorder recording all streams
- [ ] `walking.py` tested with dry run
- [ ] Treadmill / walking path cleared
- [ ] Participant briefed on protocol and audio cues (high beep = walk, low beep = stop)

---

## Round 1

### Module 1.1 — Quiet Sitting (3 min)

> Participant sits still, eyes open, fixating forward. Minimal movement.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | 2026-04-11_001 |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 1.2 — Quiet Standing (3 min)

> Participant stands still, feet shoulder-width apart, eyes open, arms at sides.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | 2026-04-11_002 |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 1.3 — Continuous Walking (3 min)

> Participant walks continuously around the lab at a self-selected comfortable pace. No stopping.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | 2026-04-11_003 |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 1.4 — Block-Design Interrupted Walking (`walking.py`)

> 10 blocks of alternating standing/walking with randomised durations.  
> Standing: 12–35 s | Walking: 4–28 s  
> LSL triggers: standing_start=1, standing_end=2, walking_start=3, walking_end=4

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename (fNIRS)** | 2026-04-11_005 |
| **Filename (trigger log)** | |
| **Signal quality (pre)** | |
| **Blocks completed** | /10 |
| **Notes** | |
| **Video** | |
---

### Break after Round 1

| Duration | Notes |
|----------|-------|
| | |

---

## Round 2

### Module 2.1 — Quiet Sitting (3 min)

> Participant sits still, eyes open, fixating forward. Minimal movement.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 2.2 — Quiet Standing (3 min)

> Participant stands still, feet shoulder-width apart, eyes open, arms at sides.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 2.3 — Continuous Walking (3 min)

> Participant walks continuously around the lab at a self-selected comfortable pace. No stopping.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 2.4 — Block-Design Interrupted Walking (`walking.py`)

> 10 blocks of alternating standing/walking with randomised durations.  
> Standing: 12–35 s | Walking: 4–28 s  
> LSL triggers: standing_start=1, standing_end=2, walking_start=3, walking_end=4

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename (fNIRS)** | |
| **Filename (trigger log)** | |
| **Signal quality (pre)** | |
| **Blocks completed** | /10 |
| **Notes** | |

---

### Break after Round 2

| Duration | Notes |
|----------|-------|
| | |

---

## Round 3

### Module 3.1 — Quiet Sitting (3 min)

> Participant sits still, eyes open, fixating forward. Minimal movement.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 3.2 — Quiet Standing (3 min)

> Participant stands still, feet shoulder-width apart, eyes open, arms at sides.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 3.3 — Continuous Walking (3 min)

> Participant walks continuously around the lab at a self-selected comfortable pace. No stopping.

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename** | |
| **Signal quality (pre)** | |
| **Notes** | |

---

### Module 3.4 — Block-Design Interrupted Walking (`walking.py`)

> 10 blocks of alternating standing/walking with randomised durations.  
> Standing: 12–35 s | Walking: 4–28 s  
> LSL triggers: standing_start=1, standing_end=2, walking_start=3, walking_end=4

| Field | Value |
|-------|-------|
| **Start time** | |
| **End time** | |
| **Filename (fNIRS)** | |
| **Filename (trigger log)** | |
| **Signal quality (pre)** | |
| **Blocks completed** | /10 |
| **Notes** | |

---

## Post-experiment

| Field | Value |
|-------|-------|
| **Session end time** | |
| **Total cap-on time** | |
| **Channels lost during session** | |
| **Participant feedback** | |
| **General notes** | |

---

## `walking.py` trigger reference

| Trigger | Value | Audio cue |
|---------|-------|-----------|
| `standing_start` | 1 | None |
| `standing_end` | 2 | None |
| `walking_start` | 3 | High beep (1200 Hz, 400 ms) |
| `walking_end` | 4 | Low beep (500 Hz, 400 ms) |

**Parameters:** 10 blocks, 5 s startup delay, standing 12–35 s, walking 4–28 s
