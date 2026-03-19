V0.4 simplifies the dual-axis serial control protocol into a compact two-value format. 
The Raspberry Pi sends incremental commands such as +15,-24 to the ESP32 over USB serial,
where the first value represents pan increment and the second value represents tilt increment. 
The ESP32 parses the command, updates the two servo positions, and also supports special commands such as HOME and OUT.

2026/3/19      by VHFX_xingyun
