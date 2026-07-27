"""
File: multirotor_holoocean.launch.py
Author: Brandon Sutherland, Andema Mongane, Jacob Moore
Description: ROS2 launch file used to launch all the nodes to simulate a multirotor in HoloOcean
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    rosflight_sim_share = FindPackageShare('rosflight_sim')

    dynamics_param_file = PathJoinSubstitution(
        [rosflight_sim_share, 'params', 'multirotor_dynamics.yaml']
    )

    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Whether the nodes will use sim time or not"
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    ##########
    # Launch #
    ##########

    # Start simulator
    simulator_launch_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([rosflight_sim_share, 'launch', 'holoocean_sim.launch.py'])
        ),
        launch_arguments={
            'agent': 'multirotor'
        }.items()
    )


    # Start common nodes
    common_nodes_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [rosflight_sim_share, 'launch', 'common_nodes_standalone.launch.py']
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'dynamics_param_file': dynamics_param_file,
        }.items()
    )

    # Start forces and moments
    mr_forces_moments_node = Node(
        package="rosflight_sim",
        executable="multirotor_forces_and_moments",
        name='multirotor_forces_and_moments',
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time}, dynamics_param_file
        ],
    )

    # Start dynamics node
    standalone_dynamics_node = Node(
        package="rosflight_sim",
        executable="standalone_dynamics",
        name='standalone_dynamics',
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}, dynamics_param_file]
    )

    return LaunchDescription(
        [
            use_sim_time_arg,
            simulator_launch_include,
            common_nodes_include,
            mr_forces_moments_node,
            standalone_dynamics_node,
        ]
    )
