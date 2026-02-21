# SOARM101 Decisions and Notes

20260221

## Naming Convention

All project-specific additions use the `jai_` prefix to distinguish them from
upstream lerobot content. This applies to branches, docs directories, and any
custom scripts or configs added as part of this project.

## Udev Rule Script

- Created `generate_motorbus_udev_rule.bash` for generating udev rules for
  MotorBus devices
- Removed FTDI-specific `ATTR{device/latency_timer}` -- not applicable to the
  SEEED STUDIO CDC ACM devices used in this project
- Set `MODE="0666"` for broad device access
- Added `set -euo pipefail` for safer script execution
