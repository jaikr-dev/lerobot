# SOARM101 Hardware Reference

20260222

## SO-101 Leader Arm Motor Gear Ratios

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

## SO-101 Follower Arm Motor Gear Ratios

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

## Power Supply

- Leader arm -- always uses 7.4V motors, powered at 5V
- Follower arm -- uses 12V Pro motors, powered at 12V

Make sure you use the correct power supply for each arm.
