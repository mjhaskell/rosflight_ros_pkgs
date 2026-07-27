"""
File: multirotor_gazebo.launch.py
Author: Brandon Sutherland
Created: June 22, 2023
Last Modified: July 17, 2023
Description: ROS2 launch file used to launch multirotor gazebo simulator
"""

import sys

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    """This is a launch file that runs the bare minimum requirements fly a multirotor in gazebo"""

    rosflight_sim_share = FindPackageShare("rosflight_sim")

    aircraft_arg_found = False
    for i, arg in enumerate(sys.argv):
        if arg.startswith('aircraft:='):
            aircraft_arg_found = True
    if not aircraft_arg_found:
        sys.argv.append('aircraft:=multirotor')

    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="False",
        description="Whether the nodes will use sim time or not"
    )
    use_sim_time = LaunchConfiguration('use_sim_time')


    # Start simulator
    simulator_launch_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([rosflight_sim_share, 'launch', 'gazebo_rf_sim.launch.py'])
        ),
        launch_arguments={
            'robot_namespace': 'multirotor',
        }.items()
    )

    # Start independent nodes
    independent_nodes_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([rosflight_sim_share, 'launch', 'common_nodes_gazebo.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Start forces and moments
    mr_forces_moments_node = Node(
        package="rosflight_sim",
        executable="multirotor_forces_and_moments",
        name="multirotor_forces_and_moments",
        output="screen",
        parameters=[
            PathJoinSubstitution([rosflight_sim_share, 'params', 'multirotor_dynamics.yaml']),
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        simulator_launch_include,
        independent_nodes_include,
        mr_forces_moments_node
    ])
