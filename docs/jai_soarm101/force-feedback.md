4 April 2026

## Force Feedback for the SOARM101

### Hardware Challenges

- The STS3215 has position, velocity, PWM, and step modes -- but no dedicated current/torque control mode. PWM mode is the closest, where we control raw motor power, 
but it's open-loop (no precise torque control). 
- There servo can read it's current load (there is a `Present_Load` register, so you could read what force the follower feels.
- But to **push back** on the leader, you'd need to enable torque and write PWM values proportional to the follower's load. However, the problem is that the operator is also
physically moving the leader, and the motor would fight or interfere with hand movements unpredictably.
 
### What I'd actually need:

- Read side (follower) -- I need to read `Present_Load` from the follower's motors. This already works with the existing hardware.
- Write side (leader) -- this is the hard part. I'd need motors that support `current control mode` where I'd set a target torque, not a target position. The motor applies force
but doesn't resist being moved. Dynamixel servos can do this but STS3215 can't. 

### Realistic options:

- Swap leader motors to Dynamixels with current control -- but that means a different motor bus, different wiring, different firmware. Basically, a different leader arm.
- Use a completely different teleop device with built-in haptics.
