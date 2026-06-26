# rover_global_localization

ROS 2 package for global GPS-based localization of a rover using `robot_localization`.

This package adds the global localization layer required to publish the transform:

```text
map -> odom
```

It is designed to work together with an existing local EKF that already publishes:

```text
odom -> base_link
```

## Purpose

The local EKF usually fuses wheel or track odometry with IMU data to produce a smooth local odometry estimate. This local estimate is continuous, but it can drift over time.

This package uses GPS data with `navsat_transform_node` and a second EKF to correct that drift in a global `map` frame.

Final TF tree:

```text
map -> odom -> base_link
```

## Architecture

Existing local localization:

```text
/odom + /imu/raw
        |
        v
Local EKF
        |
        v
/odometry/filtered
TF: odom -> base_link
```

Global localization added by this package:

```text
/gps/fix + /imu/raw + /odometry/filtered
        |
        v
navsat_transform_node
        |
        v
/odometry/gps
        |
        v
Global EKF
        |
        v
/odometry/global
TF: map -> odom
```

## Input Topics

This package expects the following topics:

```text
/odometry/filtered   nav_msgs/msg/Odometry
/imu/raw             sensor_msgs/msg/Imu
/gps/fix             sensor_msgs/msg/NavSatFix
```

`/odometry/filtered` should come from the local EKF.

`/imu/raw` should contain IMU data. Ideally, the IMU message should include a valid orientation.

`/gps/fix` should contain GPS data as `sensor_msgs/msg/NavSatFix`.

## Output Topics

This package publishes:

```text
/odometry/gps        nav_msgs/msg/Odometry
/odometry/global     nav_msgs/msg/Odometry
```

It also publishes the TF:

```text
map -> odom
```

## Required Existing TF

Before launching this package, the robot should already have:

```text
odom -> base_link
```

Usually this is published by the local EKF.

The robot should also have static transforms for its sensors, for example:

```text
base_link -> imu_link
base_link -> gps_link
```

## Dependencies

This package depends on:

```text
robot_localization
nav_msgs
sensor_msgs
tf2_ros
rclpy
```

Install `robot_localization`:

```bash
sudo apt update
sudo apt install ros-jazzy-robot-localization
```

If you are not using ROS 2 Jazzy, replace `jazzy` with your ROS 2 distribution name.

## Package Structure

```text
rover_global_localization
├── config
│   ├── ekf_global.yaml
│   └── navsat.yaml
├── launch
│   └── global_localization.launch.py
├── rover_global_localization
│   └── __init__.py
├── resource
│   └── rover_global_localization
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
```

## Configuration

### navsat.yaml

`navsat_transform_node` converts GPS latitude/longitude into a local odometry message.

Important parameters:

```yaml
use_odometry_yaw: false
zero_altitude: true
wait_for_datum: false
publish_filtered_gps: true
```

If the IMU does not provide a valid orientation, `use_odometry_yaw` may need to be set to `true`.

### ekf_global.yaml

The global EKF fuses:

```text
/odometry/filtered
/odometry/gps
/imu/raw
```

The important frame configuration is:

```yaml
map_frame: map
odom_frame: odom
base_link_frame: base_link
world_frame: map
publish_tf: true
```

The key parameter is:

```yaml
world_frame: map
```

This makes the global EKF publish:

```text
map -> odom
```

## Build

From the ROS 2 workspace:

```bash
cd ~/ros2_ws
colcon build --packages-select rover_global_localization
source install/setup.bash
```

## Run

First, launch the local EKF and sensor drivers.

The following topics should already exist:

```bash
ros2 topic list | grep -E "imu|gps|odom"
```

Expected topics include:

```text
/imu/raw
/gps/fix
/odom
/odometry/filtered
```

Then launch the global localization package:

```bash
ros2 launch rover_global_localization global_localization.launch.py
```

## Verification

Check the GPS fix:

```bash
ros2 topic echo /gps/fix --once
```

Check the IMU:

```bash
ros2 topic echo /imu/raw --once
```

Check the local EKF output:

```bash
ros2 topic echo /odometry/filtered --once
```

Check the GPS odometry output from `navsat_transform_node`:

```bash
ros2 topic echo /odometry/gps --once
```

Check the global EKF output:

```bash
ros2 topic echo /odometry/global --once
```

Check the local transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Check the global transform:

```bash
ros2 run tf2_ros tf2_echo map odom
```

Check the full transform chain:

```bash
ros2 run tf2_ros tf2_echo map base_link
```

## RViz

Launch RViz:

```bash
rviz2
```

Set:

```text
Fixed Frame = map
```

Recommended displays:

```text
TF
Odometry: /odometry/filtered
Odometry: /odometry/global
NavSatFix: /gps/fix
```

Expected TF tree:

```text
map
└── odom
    └── base_link
        ├── imu_link
        └── gps_link
```

## Notes

Only one node should publish each TF.

Recommended setup:

```text
Local EKF  -> odom -> base_link
Global EKF -> map -> odom
```

The odometry node should not publish `odom -> base_link` if the local EKF already does it.

The global EKF should not replace the local EKF. The local EKF provides smooth short-term motion, while the global EKF corrects drift using GPS.

## Troubleshooting

### `/odometry/gps` is not publishing

Check that all required inputs exist:

```bash
ros2 topic echo /gps/fix --once
ros2 topic echo /imu/raw --once
ros2 topic echo /odometry/filtered --once
```

Also check that the IMU orientation is valid.

If the IMU orientation is invalid, try setting:

```yaml
use_odometry_yaw: true
```

in `navsat.yaml`.

### No `map -> odom` transform

Check that the global EKF is running:

```bash
ros2 node list
```

Check the global odometry output:

```bash
ros2 topic echo /odometry/global --once
```

Check the TF:

```bash
ros2 run tf2_ros tf2_echo map odom
```

Make sure the global EKF has:

```yaml
world_frame: map
publish_tf: true
```

### Wrong IMU topic name

If your IMU topic is `/imu/data` instead of `/imu/raw`, replace `/imu/raw` with `/imu/data` in:

```text
config/ekf_global.yaml
launch/global_localization.launch.py
```

## License

MIT
