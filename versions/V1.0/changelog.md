# Changelog

## Version 1.0

### Added
- CSI camera-based visual target detection
- real-time target center extraction
- pan-tilt incremental control over USB serial
- stable lock hysteresis logic
- target center smoothing
- lost-target waiting and homing
- automatic `OUT` trigger after stable hold

### Protocol
- compact incremental protocol: `pan_delta,tilt_delta`
- special commands: `HOME`, `OUT`

### Verified
- single-target visual tracking
- stable lock trigger
- automatic homing after target loss

### Notes
This version is considered the first complete milestone of the project, focused on single-target tracking and stable lock-trigger behavior.
