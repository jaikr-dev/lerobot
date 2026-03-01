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
