20260404

## Force Feedback for the SOARM101

### Hardware Challenges

- The STS3215 has position, velocity, PWM, and step modes -- but no dedicated current/torque control mode. PWM mode is the closest, where we control raw motor power,
but it's open-loop (no precise torque control).
- There servo can read it's current load (there is a `Present_Load` register, so you could read what force the follower feels.
- But to **push back** on the leader, you'd need to enable torque and write PWM values proportional to the follower's load. However, the problem is that the operator is also
physically moving the leader, and the motor would fight or interfere with hand movements unpredictably.

### What I'd actually need

- Read side (follower) -- I need to read `Present_Load` from the follower's motors. This already works with the existing hardware.
- Write side (leader) -- this is the hard part. I'd need motors that support `current control mode` where I'd set a target torque, not a target position. The motor applies force
but doesn't resist being moved. Dynamixel servos can do this but STS3215 can't.

### Realistic options

- Swap leader motors to Dynamixels with current control -- but that means a different motor bus, different wiring, different firmware. Basically, a different leader arm.
- Use a completely different teleop device with built-in haptics.

### More information about Dynamixel servos

- The Dynamixel has these 4 modes: Current, Velocity, Position, and Extended Position. The current mode is the mode that enables force feedback -- you set a target current (force) and the motor applies it, but I can still move it by hand. So I need to put the Dynamixels in current mode, read the follower's load, and write
proportional current goals to the leader. For Dynamixels, *current is torque*. Current and Torque are directly proportional because they're governed by **Torque Constant**. The Dynamixel datasheets give you the conversion. For the XL330-M288 for example, each current unit corresponds to a specific amount of torque. So when I read a load value from the follower and want the leader to push back with that same force, I just write that value as the current goal to the leader. *In practice, I'd scale it down so the feedback feels gentle rather than fighting the operator*.