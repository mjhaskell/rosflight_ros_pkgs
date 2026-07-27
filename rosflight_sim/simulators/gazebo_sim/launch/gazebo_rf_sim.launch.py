"""
File: gazebo_rf_sim.launch.py
Author: Brandon Sutherland
Created: June 15, 2023
Last Modified: July 21, 2023
Description: ROS2 launch file used to launch Gazebo with the rosflight SIL.
"""

import sys

import xacro
from ament_index_python import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import TextSubstitution, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    """Launches a SIL vehicle in Gazebo"""

    # aircraft = LaunchConfiguration('aircraft')
    # TODO: We have to parse it in two places, the parent file and this file, since we 
    # need that info in both. LaunchConfiguration cannot be converted to a string by anything
    # other than the other launch actions... There is potentially a way to use the Command launch
    # action, which evaluates a command (i.e. evaluates the xacro command)
    # TODO: I think we could structure this so that we only need one XXXX_gazebo.launch.py....
    aircraft = 'anaconda' # default aircraft
    aircraft_3d_file = 'skyhunter'
    for arg in sys.argv:
        if arg.startswith("aircraft:="):
            aircraft = arg.split(":=")[1]

    if aircraft == 'multirotor':
        aircraft_3d_file = 'multirotor'

    rosflight_sim_share = FindPackageShare("rosflight_sim")


    # Launch Arguments
    x = LaunchConfiguration('x')
    x_launch_arg = DeclareLaunchArgument(
        'x', default_value=TextSubstitution(text='0')
    )
    y = LaunchConfiguration('y')
    y_launch_arg = DeclareLaunchArgument(
        'y', default_value=TextSubstitution(text='0')
    )
    z = LaunchConfiguration('z')
    z_launch_arg = DeclareLaunchArgument(
        'z', default_value=TextSubstitution(text='0.2')
    )
    yaw = LaunchConfiguration('yaw')
    yaw_launch_arg = DeclareLaunchArgument(
        'yaw', default_value=TextSubstitution(text='4.71')
    )
    paused = LaunchConfiguration('paused')
    paused_launch_arg = DeclareLaunchArgument(
        'paused', default_value=TextSubstitution(text='false')
    )
    gui = LaunchConfiguration('gui')
    gui_launch_arg = DeclareLaunchArgument(
        'gui', default_value=TextSubstitution(text='true')
    )
    verbose = LaunchConfiguration('verbose')
    verbose_launch_arg = DeclareLaunchArgument(
        'verbose', default_value=TextSubstitution(text='false')
    )
    world_file = LaunchConfiguration('world_file')
    world_file_launch_arg = DeclareLaunchArgument(
        'world_file', default_value=PathJoinSubstitution(
            [rosflight_sim_share, 'gazebo_resource', 'runway.world']
        )
    )
    tf_prefix = LaunchConfiguration('tf_prefix')
    tf_prefix_launch_argument = DeclareLaunchArgument(
        'tf_prefix', default_value=TextSubstitution(text="")
    )
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_launch_argument = DeclareLaunchArgument(
        'robot_namespace', default_value=TextSubstitution(text='fixedwing')
    )
    gazebo_namespace = LaunchConfiguration('gazebo_namespace')
    gazebo_namespace_launch_argument = DeclareLaunchArgument(
        'gazebo_namespace', default_value=TextSubstitution(text="")
    )
    log_level = LaunchConfiguration('ros_log_level')
    log_level_launch_argument = DeclareLaunchArgument(
        'ros_log_level', default_value=TextSubstitution(text='info')
    )

    # Start simulator
    gazebo_launch_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare('gazebo_ros'), 'launch', 'gazebo.launch.py']
            )
        ),
        launch_arguments={
            'pause': paused,
            'gui': gui,
            'verbose': verbose,
            'world': world_file,
            'params_file': PathJoinSubstitution(
                [rosflight_sim_share, 'params', f'{aircraft}_dynamics.yaml']
            )
        }.items(),
    )

    # Render xacro file
    rosflight_sim_path = get_package_share_path("rosflight_sim")
    xacro_filepath = rosflight_sim_path / 'xacro' / f'{aircraft}.urdf.xacro'
    urdf_filepath = rosflight_sim_path / 'gazebo_resource' / f'{aircraft}.urdf'
    robot_description = xacro.process_file(
        str(xacro_filepath),
        mappings={
            'mesh_file_location': str(
                rosflight_sim_path / 'common_resource' / f'{aircraft_3d_file}.dae'
            )
        }
    ).toxml()
    urdf_filepath.write_text(robot_description)

    # Spawn vehicle
    spawn_vehicle_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        respawn=False,
        output='screen',
        parameters=[
            {'tf_prefix': tf_prefix}
        ],
        arguments=[
            '-file', str(urdf_filepath),
            '-entity', 'robot',
            '-robot_namespace', robot_namespace,
            '-gazebo_namespace', gazebo_namespace,
            '-x', x,
            '-y', y,
            '-z', z,
            '-Y', yaw,
            '--ros-args', '--log-level', log_level
        ]
    )

    return LaunchDescription([
        x_launch_arg,
        y_launch_arg,
        z_launch_arg,
        yaw_launch_arg,
        paused_launch_arg,
        gui_launch_arg,
        verbose_launch_arg,
        world_file_launch_arg,
        tf_prefix_launch_argument,
        robot_namespace_launch_argument,
        gazebo_namespace_launch_argument,
        log_level_launch_argument,
        gazebo_launch_include,
        spawn_vehicle_node
    ])
