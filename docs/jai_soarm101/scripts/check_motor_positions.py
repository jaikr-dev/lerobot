"""Check raw motor positions to debug calibration offset errors."""

from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig

config = SO101LeaderConfig(port="/dev/leader_arm", id="jai_leader_arm")
leader = SO101Leader(config)
leader.connect(calibrate=False)
positions = leader.bus.sync_read("Present_Position", normalize=False)
for motor, pos in positions.items():
    offset = abs(pos - 2047)
    flag = " <-- OUT OF RANGE" if offset > 2047 else ""
    print(f"{motor}: {pos} (offset: {offset}){flag}")
leader.disconnect()
