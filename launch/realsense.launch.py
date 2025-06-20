import os
import sys
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():

    realsense = Node(
        package='realsense',
        executable='realsense.py',
        name='realsense',
        output='screen',
    )

    launch_description = LaunchDescription()
    launch_description.add_action(realsense)

    return launch_description

def main(args=None):
    try:
        generate_launch_description()
    except KeyboardInterrupt:
        # quit
        sys.exit()


if __name__ == "__main__":
    main()