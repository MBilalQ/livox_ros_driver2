import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # 1. Locate the original MID360 launch file
    livox_driver_pkg = get_package_share_directory('livox_ros_driver2')
    livox_launch_path = os.path.join(livox_driver_pkg, 'launch_ROS2', 'msg_MID360_launch.py')

    # 2. Include the driver, but REMAP the topic to Autoware's input
    livox_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(livox_launch_path),
        launch_arguments={
            'x_transfer': '0',
            'y_transfer': '0',
            'z_transfer': '0',
            'xfer_format' : '0'
        }.items()
    )

    # 3. Static Transform (The "Glue")
    # This attaches the 'livox_frame' to Autoware's 'velodyne_top'
    # Adjust the numbers (x y z yaw pitch roll) if your physical mount is different.
    tf_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '0', '0', '0', '0', '0', '0',  # x y z yaw pitch roll
            'velodyne_top',                # Parent (Autoware Frame)
            'livox_frame'                  # Child (Livox Frame)
        ]
    )
    
    # 4. (Optional) PointCloud2 Remapper Node 
    # If the IncludeLaunchDescription remap doesn't catch deeper nodes, 
    # we rely on the driver config. 
    # ideally, we modify the MID360_config.json, but TF is usually enough 
    # if we manually point Rviz to the topic.
    
    return LaunchDescription([
        livox_driver,
        tf_publisher
    ])