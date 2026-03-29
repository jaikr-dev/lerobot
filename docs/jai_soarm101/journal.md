# SOARM101 Journal

20260221

## Naming Convention

All project-specific additions use the `jai_` prefix to distinguish them from
upstream lerobot content. This applies to branches, docs directories, and any
custom scripts or configs added as part of this project.

## Hardware

- **Motor Controller:** SEEED STUDIO 331-2508220013
- **Interface:** USB CDC ACM (`/dev/ttyACM*`)

## Udev Rule Script

- Created `generate_motorbus_udev_rule.bash` for generating udev rules for
  MotorBus devices
- Removed FTDI-specific `ATTR{device/latency_timer}` -- not applicable to the
  SEEED STUDIO CDC ACM devices used in this project
- Set `MODE="0666"` for broad device access
- Added `set -euo pipefail` for safer script execution

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

## Leader Arm Motor Gear Ratios

The HuggingFace docs mention that the leader arm needs specific gear ratios but
don't say which motor serial/model numbers correspond to which gear ratio. This
table maps it out for the Feetech STS3215 motors.

| Axis | Motor ID | Joint          | Gear Ratio | Motor Model Number |
|------|----------|----------------|------------|--------------------|
| 1    | 1        | Base/Shoulder Pan   | 1/191  | STS3215-C044       |
| 2    | 2        | Shoulder Lift       | 1/345  | STS3215-C001       |
| 3    | 3        | Elbow Flex          | 1/191  | STS3215-C044       |
| 4    | 4        | Wrist Flex          | 1/147  | STS3215-C046       |
| 5    | 5        | Wrist Roll          | 1/147  | STS3215-C046       |
| 6    | 6        | Gripper             | 1/147  | STS3215-C046       |

In total you need:

- 3x 1/147 gear ratio (C046) -- wrist flex, wrist roll, gripper
- 2x 1/191 gear ratio (C044) -- base/shoulder pan, elbow flex
- 1x 1/345 gear ratio (C001) -- shoulder lift

The higher-load joints (base, shoulder, elbow) use the higher gear ratios so the
arm can support its own weight. The wrist and gripper use lower ratios so they
stay easy to move by hand.

### Leader Arm Component Weights

Measured without horns or screws.

| Component        | Motor Model  | Motor (g) | Cable (g) |
|------------------|--------------|-----------|-----------|
| Servo Bus        | --           | 7.29      | --        |
| ID 1 (Base)      | STS3215-C044 | 54.22     | 3.55      |
| ID 2 (Shoulder)  | STS3215-C001 | 54.32     | 3.49      |
| ID 3 (Elbow)     | STS3215-C044 | 54.29     | 3.52      |
| ID 4 (Wrist Flex)| STS3215-C046 | 53.91     | 3.44      |
| ID 5 (Wrist Roll)| STS3215-C046 | 54.26     | 3.50      |
| ID 6 (Gripper)   | STS3215-C046 | 54.11     | 3.50      |

**The goal is to have accurate component masses for feedforward gravity
compensation. If system identification doesn't work well enough, these measured
values can be used directly to build a dynamics model of the arm. Each link's
total mass comes mostly from the motor and cable, so capturing these during
assembly -- before everything is buried inside the printed parts -- saves having
to tear the arm down later. These same values are also needed if the arm ever
gets modeled in simulation (URDF/MJCF), where realistic masses and inertias
make the difference between a sim that transfers to real and one that doesn't.**

## Follower Arm Motor Gear Ratios

The follower arm uses the same gear ratio (1/345) for all six motors. Since this
build uses the 12V version, that corresponds to the STS3215-C018.

| Axis | Motor ID | Joint               | Gear Ratio | Motor Model Number |
|------|----------|---------------------|------------|--------------------|
| 1    | 1        | Base/Shoulder Pan   | 1/345      | STS3215-C018       |
| 2    | 2        | Shoulder Lift       | 1/345      | STS3215-C018       |
| 3    | 3        | Elbow Flex          | 1/345      | STS3215-C018       |
| 4    | 4        | Wrist Flex          | 1/345      | STS3215-C018       |
| 5    | 5        | Wrist Roll          | 1/345      | STS3215-C018       |
| 6    | 6        | Gripper             | 1/345      | STS3215-C018       |

In total you need 6x 1/345 gear ratio (C018).

The 12V Pro version provides 30 kg-cm of stall torque compared to around
16.5 kg-cm for the 7.4V standard motors.

### Follower Arm Component Weights

Measured without horns or screws.

| Component        | Motor Model  | Motor (g) | Cable (g) |
|------------------|--------------|-----------|-----------|
| ID 1 (Base)      | STS3215-C018 | 55.67     | 3.50      |
| ID 2 (Shoulder)  | STS3215-C018 | 55.72     | 3.27      |
| ID 3 (Elbow)     | STS3215-C018 | 55.55     | 3.54      |
| ID 4 (Wrist Flex)| STS3215-C018 | 55.58     | 3.52      |
| ID 5 (Wrist Roll)| STS3215-C018 | 55.34     | 3.58      |
| ID 6 (Gripper)   | STS3215-C018 | 55.45     | 3.52      |

## Power Supply

- Leader arm -- always uses 7.4V motors, powered at 5V
- Follower arm -- uses 12V Pro motors, powered at 12V

Make sure you use the correct power supply for each arm.

20260301

## Leader Arm Assembly

### General

- The assembly videos on the
  [HuggingFace docs](https://huggingface.co/docs/lerobot/en/so101?assembly=Leader)
  don't match the text instructions. This was confusing at first but the videos
  are more reliable -- just watch those and ignore the text when they conflict.
- Overall assembly was pretty easy and straightforward. No tolerance issues with
  the 3D printed parts.

### M2 x 6mm Self-Threading Screws

These are used throughout the assembly. They're self-threading which makes
things very easy, especially with 3D printed parts where holes aren't always
perfectly aligned or have sagged slightly during printing.

### M3 Screw Holes and Counterbores Are Slightly Small

Had to use a lot of force in several places to get the M3 screw heads into the
counterbores, and then more force to drive the screws through the 3D printed
parts into the servo horn holes. Next time I print a set, I need to modify the
CAD files on Onshape to increase the M3 screw holes and counterbores by
0.05--0.1 mm.

### Trigger Installation

The trigger was the hardest part to install because it kept moving around. The
approach that worked: use two M3 6mm screws to align the holes first, then
slowly tighten both screws alternately until they lock into the servo horn.
After that, add the remaining two screws.

20260329

## Upstream PRs

Submitted two PRs to huggingface/lerobot:

- **Fix SO-101 assembly instruction order to match videos** -- reordered motor
  horn installation to come before placing motors in the housing, added note
  that bottom horns don't require screws.
- **Replace chmod 666 with persistent udev rules** -- added
  `generate_motorbus_udev_rule.bash` script and updated SO-101, SO-100, Koch,
  and LeKiWi docs to use it instead of temporary chmod.

## Project Docs Consolidation

Merged setup.md, decisions.md, assembly.md, and hardware.md into this single
journal file. Easier to append new entries without deciding which file something
belongs in.

## Python Version

The lerobot codebase uses `type` statement syntax (Python 3.12+). The previous
venv was Python 3.10 which caused a `SyntaxError` on import. Recreated with
Python 3.12:

```bash
uv venv --python 3.12
uv pip install -e ".[all]"
```

`[all]` fails due to `egl-probe` (a transitive dependency via hf-libero ->
robomimic) being incompatible with newer CMake. Workaround:

```bash
CMAKE_POLICY_VERSION_MINIMUM=3.5 uv pip install -e ".[all]"
```

## Leader Arm Input Voltage Error

During `lerobot-setup-motors`, motor 2 (shoulder_lift) threw
`[RxPacketError] Input voltage error!`. This is overvoltage protection -- the
leader arm uses 7.4V motors and must be powered with the 5V supply, not the 12V
one. The 12V supply is for the follower arm only. Switching to 5V fixed it.
The motors were not damaged -- the STS3215 has built-in overvoltage protection
that refuses to operate rather than frying.

See huggingface/lerobot#2387 for other reports of the same issue.

## Calibration Homing Offset Out of Range

During `lerobot-calibrate`, got `ValueError: Magnitude 2055 exceeds 2047`.
This means one of the joints wasn't close enough to the center of its physical
range when pressing Enter. The tolerance is tight -- a few degrees matters.

Created `docs/jai_soarm101/scripts/check_motor_positions.py` to read raw motor
positions and identify which joint is off before retrying calibration.
