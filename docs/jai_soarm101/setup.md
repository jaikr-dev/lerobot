# SOARM101 Project Setup

20260221

## Hardware

- **Motor Controller:** SEEED STUDIO 331-2508220013
- **Interface:** USB CDC ACM (`/dev/ttyACM*`)

## Udev Rules

A script is provided to generate udev rules for MotorBus devices so they get
stable symlinks under `/dev/` (e.g., `/dev/leader_arm`, `/dev/follower_arm`).

### Generating a rule

```bash
sudo bash src/lerobot/scripts/generate_motorbus_udev_rule.bash -d /dev/ttyACM0 -n leader_arm
```

### What the script does

1. Reads the device's vendor ID, product ID, and serial number via `udevadm`
2. Writes a udev rule to `/etc/udev/rules.d/99-tty-<name>.rules`
3. Reloads udev rules and triggers a re-scan

### Removing a rule

Delete the generated file and reload:

```bash
sudo rm /etc/udev/rules.d/99-tty-<name>.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```
