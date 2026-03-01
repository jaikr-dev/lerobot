# Upstream PRs

20260301

## Fix SO-101 Assembly Text Instructions

The text instructions on the
[SO-101 HuggingFace docs](https://huggingface.co/docs/lerobot/en/so101?assembly=Leader)
don't match the assembly videos. Need to note the specific discrepancies during
follower arm build (most of the assembly is the same) and submit a PR with
corrections.

## Add Udev Rule Generator for SO-101

The upstream SO-101 docs only suggest `sudo chmod 666 /dev/ttyACM0` which is
temporary and doesn't survive reboots. The `generate_motorbus_udev_rule.bash`
script creates persistent symlinks (e.g., `/dev/leader_arm`,
`/dev/follower_arm`) using vendor ID, product ID, and serial number.

Before submitting, consider making the script work for both CDC ACM and FTDI
devices (e.g., auto-detect or add a flag for the `latency_timer` attribute) so
it's useful across all lerobot platforms, not just SO-101.

## Gravity Compensation for SO-101

LeRobot has feed-forward gravity compensation for the Unitree G1 (using
Pinocchio's RNEA to compute gravity torques from joint positions), but nothing
for the SO-101 or Koch arms.

The core problem is hardware. The Feetech STS3215 motors used in the SO-101
only support position, velocity, PWM, and step modes -- there is no
torque/current control mode. You cannot command a target torque. The Koch arm's
Dynamixel XL430-W250 has the same limitation -- position, velocity, extended
position, and PWM only.

### Motor comparison for torque control feasibility

| Motor | Torque Control | Stall Torque | Dimensions (mm) | Weight | Price |
|-------|---------------|--------------|-----------------|--------|-------|
| Feetech STS3215 (7.4V) | No | 16.5 kg-cm @ 6V | 24.7 x 45.2 x 35 | 55 g | ~$10 |
| Feetech STS3215 (12V) | No | 30 kg-cm @ 12V | 24.7 x 45.2 x 35 | 55 g | ~$12 |
| Dynamixel XL430-W250 | No | 15.3 kg-cm @ 12V | 28.5 x 46.5 x 34 | 65 g | ~$50 |
| Dynamixel XL330-M288 | Yes (current mode, current-based position mode) | 5.3 kg-cm @ 5V | 20 x 34 x 26 | 18 g | ~$24 |
| Dynamixel XM430-W350 | Yes (current-based position mode) | 41.8 kg-cm @ 12V | 28.5 x 46.5 x 34 | 82 g | ~$50+ |

The XL330-M288 is price-comparable to the STS3215 and has the right control
modes, but its torque is very low for a 6-DOF arm. The XM430-W350 has both the
control modes and the torque but is significantly more expensive.

This is not a straightforward PR -- it would require either a hardware change
(different motors) or an external software torque control loop running through
USB serial, which is fragile and bandwidth-limited.
