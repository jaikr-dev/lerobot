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

## Links to Explore

- https://github.com/vladfatu/telerobot
- https://www.giacomoran.com/blog/act-smooth/
- https://github.com/roboninecom/SO-ARM100-101-Parallel-Gripper
- https://arturhabuda.com/2025/07/01/foundation-robotics-model-comparison/
- https://arturhabuda.com/2026/03/20/attention-heatmaps-in-vla-pi0-and-foca/

20260403

## Links to Explore

- GEN-1 gripper design by Generalist AI -- good for dexterous tasks, need to
  design something similar for the SO-101:
  - https://generalistai.com/blog/apr-02-2026-GEN-1
  - https://generalistai.com/blog/jan-29-2026-physical-commonsense
  - https://www.youtube.com/watch?v=SY2xyrmV44Y
  - https://www.youtube.com/watch?v=WgIdj9c4pA8
  - https://www.youtube.com/watch?v=721BZL9jPhU

## Learnings from lerobot_teleoperate.py

### How the teleop loop works

The teleoperation script has two main parts:

1. **TeleoperateConfig** -- a dataclass that holds all settings (robot, teleoperator,
   fps, display options). Each field becomes a CLI flag automatically.
2. **teleop_loop()** -- the actual control loop that runs every frame.

The loop does this each iteration:
- Read the robot's current state (motor positions + camera images if any)
- Read the leader arm's position (the action)
- Process the action through pipelines (currently pass-through, but extensible)
- Send the action to the follower robot
- Optionally display data in the terminal and Rerun

### Action pipeline

The full path for an action is:
teleoperator -> raw_action -> teleop_action_processor -> robot_action_processor -> robot

The processors currently do nothing (identity/pass-through). They exist as hooks for
future features like action scaling, smoothing, or safety limits.

### Cameras are optional

If you don't pass `--robot.cameras`, it defaults to an empty dict. Teleoperation
works fine without cameras -- you just don't get visual feedback. Cameras are only
needed if you want to see what the robot sees or record data.

### display_data flag

Setting `--display_data=true` does two things:
- Prints a live-updating motor values table in the terminal (uses cursor tricks
  to overwrite the same lines each frame instead of scrolling)
- Logs camera images and actions to Rerun for visualization

### Remote visualization with Rerun

You can stream Rerun data to a remote machine by setting `--display_ip` and
`--display_port`. Useful for headless setups (e.g. Beelink with no monitor).
Both machines must be on the same network. Image compression auto-enables when
streaming remotely to save bandwidth. On the viewing machine, run
`rerun --serve --port 9876` and point the flags to that machine's local IP.

### Force feedback

The teleop loop has a special case for the Unitree G1 that sends force feedback
to the teleoperator. Neither the SO-ARM nor OMX arm support this -- both have
`send_feedback()` as a TODO.

The SO-ARM's STS3215 servos lack precise torque control. The OMX arm's Dynamixel
servos (XL430, XL330) are more capable -- they support current control mode where
the motor applies a target force without fighting position changes. This could
enable force feedback where you feel resistance when the follower hits something
but can still move the leader freely.

### Python patterns worth noting

- **Dataclasses for config** -- group related settings into a structured object
  instead of passing many separate arguments.

- **@parser.wrap() decorator** -- walks the dataclass fields and their types
  to auto-generate CLI flags. Nested dataclasses become dot-separated flags.
  No manual argparse code needed.

  Example: given these dataclasses:
  ```python
  @dataclass
  class CameraConfig:
      type: str = "opencv"
      width: int = 640

  @dataclass
  class RobotConfig:
      port: str = "/dev/ttyACM0"
      camera: CameraConfig

  @dataclass
  class MainConfig:
      robot: RobotConfig
  ```
  The decorator sees `MainConfig` -> `robot` (RobotConfig) -> `camera`
  (CameraConfig) -> `width` (int), and auto-generates these CLI flags:
  ```
  --robot.port
  --robot.camera.type
  --robot.camera.width
  ```
  When you run `--robot.camera.width=1920`, the decorator builds:
  ```python
  cfg = MainConfig(
      robot=RobotConfig(
          port="/dev/ttyACM0",
          camera=CameraConfig(type="opencv", width=1920)
      )
  )
  ```
  The dots in the CLI map directly to the nesting in the dataclass.

- **Unused imports for registration** -- imports like `OpenCVCameraConfig` marked
  `# noqa: F401` are not used directly in the file. They're imported so the class
  gets registered in a lookup table, allowing the CLI parser to resolve
  `type: opencv` to the right class.

- **try/finally for cleanup** -- ensures `disconnect()` always runs, even if the
  loop crashes or you press Ctrl+C.

- **_ for discarded return values** -- `_ = robot.send_action(...)` means the
  return value is intentionally ignored.

- **Ternary expressions** -- `True if condition else fallback` is Python's inline
  if/else for simple conditional assignments.

- **Dot notation** -- accessing attributes (`self.cameras`) and methods
  (`robot.get_observation()`) on objects.

20260403

## Learnings from so_leader.py

### High-level Overview

Nobody holds the whole thing in their head at once, even experienced developers don't. They work in layers.
People think about them as separate layers that talk to each other through defined interfaces.

SOLeader is a remote control. That's it. It reads where you move the arm and reports those positions. The
teleop loop asks it "where are your joints right now?" and it answers:

__The layers from top to Bottom__

Hardware (STS3215 servos on a serial bus)
    |
FeetechMotorsBus (talks to the servos over serial)
    |
SOLeader (wraps the bus, adds calibration and structure)
    |
teleop_loop (asks SOLeader for positions each frame)

__How the file is organized__

1. Imports - bring in the building blocks (motor bus, motor definitions, decorators)
2. Class Definition - `SOLeader` inherits from `Teleoperator`, meaning it promises to provide certain methods (`connect`, `disconnect`, `get_action`).
3. `__init__` = sets up the motor bus with 6 named motors
4. connect/disconnect - open and close serial connection with calibration in between
5. calibrate - is a one time setup to learn each joint's range
6. configure - sets motor modes
8. get_action - this is the core method that is called everyframe and reads all motor positions

__How developers architect this__

They don't visualize everything at once because they think in terms of contracts. The `Teleoperator` base class says "any teleoperator must have `connect()`, `disconnect()`, `get_action()`, and `send_feedback()`.

20260503

## Learnings from so_follower.py

The whole point of decorators is that they wrap usable behaviour around methods so you don't need to repeat
yourself

### self

`self` refers to the specific instance of the class. If you do `robot = SOFollower(config)`,
then inside any method of that class, `self` is `robot`. It's how methods access the
object's attributes like `self.bus`, `self.cameras`, `self.config`. Every instance method
takes `self` as its first argument -- Python passes it automatically when you call the method.

### with statement (context manager)

`with` runs setup code before the block and cleanup code after, guaranteed -- even if an
error happens inside. For example, `with self.bus.torque_disabled()` disables torque on
enter, runs your code, then re-enables torque on exit. You can't accidentally forget the
cleanup step. It's a cleaner version of try/finally.

### PID tuning on the follower

PID is a control loop that makes the motor reach and hold a target position.

- **P (Proportional)** -- how hard the motor pushes to reach the target. Higher = faster
  but can overshoot and shake. Lower = smoother but slower.
- **I (Integral)** -- corrects for being slightly off target over time. Set to 0 here
  because the target changes every frame anyway.
- **D (Derivative)** -- brakes as the motor approaches the target. Reduces overshoot.

The follower uses P=16 (default is 32), I=0, D=32. The lower P avoids shakiness. These
values are the same for every motor, but ideally each joint would be tuned individually
since different joints carry different loads (shoulder carries more weight than the wrist).
Per-motor tuning would give better performance but adds complexity.

### Python patterns

- **Dictionary comprehension** -- `{f"{motor}.pos": val for motor, val in action.items()}`
  builds a new dict from an existing one. Same idea as list comprehension but produces a
  dict. Pattern: `{key: value for item in iterable}`.
- **Dictionary unpacking** -- `{**dict_a, **dict_b}` merges two dicts into one. If both
  have the same key, the second overwrites the first.
- **`@property`** -- makes a method callable like an attribute (no parentheses). Can only
  be used when the method takes no arguments besides self.
- **`@cached_property`** -- same as `@property` but runs the method once and caches the
  result. Every subsequent access returns the cached result without re-running the method.
- **`all()`** -- built-in that returns True only if every item is True. `any()` returns
  True if at least one is True.
- **`_` for discarded values** -- `_ = func()` means the return value is intentionally
  ignored.
- **Aliases** -- `SO100Leader = SOLeader` creates a second name pointing to the same class.

### How observation and action flow through the system

- **Observation** = what the robot senses (motor positions + camera images)
- **Action** = what the robot can do (motor target positions only, no cameras)
- Keys use `.pos` suffix (e.g. `"shoulder_pan.pos"`) in the pipeline, which gets
  stripped before writing to the motor bus and re-added when returning.

### Gripper protection

The gripper gets extra safety limits (50% max torque, 50% max current, 25% overload
torque) because it's the most likely motor to stall. These can be tuned up if more
grip force is needed but risk overheating or stripping the plastic gears.

### max_relative_target

A safety feature that clips how far a motor can move in one step. Disabled by default
(`None`). Enable with `--robot.max_relative_target=5.0`. Runs during both teleoperation
and policy inference. During teleoperation it rarely matters (smooth movements). During
policy deployment, clipping could break the policy's assumptions -- so either disable it
or set it high enough that it never triggers.

### How developers think about code architecture

Nobody holds an entire codebase in their head. They think in layers and contracts.
A base class (like `Robot` or `Teleoperator`) defines a contract -- what methods must
exist. Subclasses (like `SOFollower`, `SOLeader`) fulfill that contract for specific
hardware. The teleop loop doesn't care how -- it just calls the interface methods.
Focus on one layer at a time, not everything at once.

### STS3215 custom firmware

An open-source clean-room reimplementation of the STS3215 firmware exists
(github.com/0o8o0-blip/sts3215-firmware). It adds a current/torque control mode
(mode 4) that the factory firmware doesn't have. This could enable force feedback on the
SO-ARM101 without swapping to Dynamixel servos -- same hardware, different firmware.
The hardware already has a current sense resistor on the PCB; the factory firmware just
never exposed it as a control mode.

### Teleoperation

For basic SO-101 teleoperation, kinematics is not used. The leader reads joint positions, the follower copies them directly. No FK or IK involved.

The `robot_kinematic_processor.py` is for a different use-case. It is for end-effector (cartesion control). Instead of commanding individual joint positions, you command where you want the gripper
top to be in 3D space (x, y, z, rotation), and the system uses:

- Forward Kinematics: converts current joint angles to the gripper's current 3D position

- Inverse Kinematics: converts a desired 3D position back to the joint angles the motors can execute

This is used when:
- A gamepad/joystick controls the gripper in Cartesion space rather
than commanding individual joint positions.

- A policy outputs end-effector targets instead of joint targets

- You want workspace bounds and safety limits in Cartesian space (the EEBoundsAndSafety class

ACT operates entirely in joint-space - it does not need FK/IK. The policy outputs the same kind of joint angles that my teleoperation records. No cartesian conversion needed. However, kinemaitcs mattesr for
Gravity compensation and Custom Grippers:

- Gravity compensation -- to compute the torque gravity exerts on each joint, you need to know where each link's center of mass is in 3D space relative to each joint. That's forward kinematics. The torque on the shoulder joint depends on where the elbow, wrist, and gripper are in space and how much they weigh. Without FK, you can't compute the gravity torque vector.

- Custom grippers -- changing the gripper changes the last link of the kinematic chain (different length, weight, center of mass). If you ever use Cartesian control or gravity compensation, the kinematic model needs to reflect the actual gripper geometry. For pure joint-space ACT, a different gripper doesn't require kinematics -- but it does change the calibration and range of motion.

### Intel RealSense D405 General Information

The D405 uses a passive stereo configuration with a pair of global shutter images separated by an 18mm baseline. It has no dedicated RGB lenses. Rather, the RGB is obtained from the depth sensor itself and then
the ISP (Image Signal Processor) enhances the RGB.

The lenses are fixed focus with no auto-focus capability for varying object distances within the working range.

The depth (and color, since on the D405 color is derived from the depth sensor) __ground truth origin__ is at
the ___left infrared imager__ which is on my right when I look at the front face of the camera.

### Intel RealSense D405 Groundtruth Origin

[Reference Link](https://forum.digikey.com/t/the-intel-realsense-depth-camera-d405/50822) for Onshape-to-Robot: The origin (0,0,0) is defined as follows:
- The centreline of the 1/4-20 tripod mounting hole runs vertically through the camera body. This is the Y axis.
- The line perpendicular to it, passing through the same point, is the X axis.
- Where they intersect is the XY origin.

From that origin, the left imager (the depth/colour origin) is located at:

- X = +9 mm — 9 mm to the right as you face the front of the camera
- X = +9 mm — 9 mm to the right as you face the front of the camera
- Z = -3.7 mm — the front glass face is Z = 0, and the optical origin sits 3.7 mm behind it, into the body

Place your mate connector 9 mm to the right of the tripod mount centreline, vertically centred, with Z pointing outward and offset 3.7mm into the body.

### Onshape-to-Robot upgrades for the SO-ARM101

The original assembly and Onshape file had hundreds of parts with random names that made no sense (sorry). Now, the main Onshape-to-robot subassembly has one composite part per link. This collapses all the visual/structure geometry into one rigid body per link, which maps cleanly to URDF links. 

The good about this approach:

- One composite part per link means onshape-to-robot has no ambiguity about what constitutes each rigid body
- Clean assembly tree makes debugging much easier
- The 7 subassemblies are connected to each other with revolute mates at the joint locations
- Things that I had to ensure:
  - `onshape-to-robot` uses the mate connector axes to define the joint rotation axes in the URDF. So, if I just snap geometry together arbitrarily, the joint axes in the output will be wrong and unpredictable.
  - For each revolute mate I needed to ensure that the mate connector is positioned at the joints centre of rotations and the z axis aligned with the rotation axis. `onshape-to-robot` treats z as the joint axis by convention.
  - These mate connectors are in the sub-assemblies rather than the main assembly. This ensures that the mate connector lives relative to the part geometry. If I ever move or modify the sub-assembly, the connector moves with it.
  