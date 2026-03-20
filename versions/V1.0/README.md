# Version 1.0 - Single-Target Visual Tracking and Stable Lock Trigger Prototype

## Overview

Version 1.0 is the first complete prototype of the project.  
It implements a full closed-loop pipeline from visual perception to pan-tilt actuation and output triggering.

The system uses a Raspberry Pi 5 with a CSI camera for visual target detection and an ESP32-based servo controller for pan-tilt motion execution. A red target is tracked in real time. Once the target remains stably aligned for a preset duration, the system automatically sends an `OUT` command to trigger the output indicator.

This version represents the first milestone where the system is not only able to detect and track a target, but also to perform stable lock confirmation and automatic output triggering.

---

## Implemented Functions

Version 1.0 currently supports:

- CSI camera real-time image acquisition on Raspberry Pi 5
- Single red target color-block detection
- Real-time target center extraction
- Pan-tilt command generation based on image error
- USB serial communication between Raspberry Pi and ESP32
- Dual-servo pan-tilt tracking
- Tracking smoothing and anti-jitter stabilization
- Lost-target waiting and automatic homing
- Stable lock timing
- Automatic `OUT` trigger after stable alignment

---

## System Architecture

### Raspberry Pi side
The Raspberry Pi is responsible for:

- camera image acquisition
- target detection
- image-center error computation
- tracking command generation
- serial communication with ESP32
- stable lock timing logic

### ESP32 side
The ESP32 is responsible for:

- receiving serial commands
- parsing incremental motion commands
- controlling the two servos
- executing `HOME`
- executing `OUT`

---

## Current Motion Convention

The compact incremental command protocol is defined as:

- `pan_delta > 0` → move right
- `pan_delta < 0` → move left
- `tilt_delta > 0` → move down
- `tilt_delta < 0` → move up

Examples:

- `+10,0` → move right
- `-10,0` → move left
- `0,+10` → move down
- `0,-10` → move up

---

## Stable Lock Logic

To reduce oscillation and false triggering, the system includes:

- target center smoothing
- hysteresis-based stable-zone logic
- stable hold timing

When the target remains inside the stable region continuously for a predefined time (`OUT_HOLD_TIME`), the Raspberry Pi sends:

```text
OUT
