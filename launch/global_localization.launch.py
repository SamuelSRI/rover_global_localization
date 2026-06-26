from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    pkg_share = get_package_share_directory('rover_global_localization')

    navsat_config = os.path.join(pkg_share, 'config', 'navsat.yaml')
    ekf_global_config = os.path.join(pkg_share, 'config', 'ekf_global.yaml')

    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform',
        output='screen',
        parameters=[navsat_config],
        remappings=[
            ('/imu', '/imu/raw'),
            ('/gps/fix', '/gps/fix'),
            ('/odometry/filtered', '/odometry/filtered'),
            ('/odometry/gps', '/odometry/gps'),
        ],
    )

    ekf_global_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_global_node',
        output='screen',
        parameters=[ekf_global_config],
        remappings=[
            ('/odometry/filtered', '/odometry/global'),
        ],
    )

    return LaunchDescription([
        navsat_transform_node,
        ekf_global_node,
    ])
