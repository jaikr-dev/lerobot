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

---

20260222

## Motor Setup

The Motor Bus needs both a USB connection to your laptop and external power from
the DC/DC adapter included in the kit. The USB connection alone is not enough --
the motors will not respond to commands without the DC/DC adapter plugged in.
This is easy to miss since the official docs don't mention it unless you watch
the video tutorials.

So before running the setup script, make sure:

1. The Motor Bus is connected to your laptop via USB
2. The DC/DC adapter is connected and powering the Motor Bus
3. At least one motor is connected to the Motor Bus

Then run:

```bash
# Example -- /dev/leader_arm is a symlink created by the udev rule,
# the actual device port is /dev/ttyACM0
uv run lerobot-setup-motors \
    --teleop.type=so101_leader \
    --teleop.port=/dev/leader_arm
```
