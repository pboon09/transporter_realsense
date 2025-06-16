#!/usr/bin/python3

import rclpy
from rclpy.node import Node
import numpy as np
import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from interfaces.srv import SetTarget

class Realsense(Node):
    def __init__(self):
        super().__init__('Realsense')

        self.kp_linear = 1.0
        self.ki_linear = 0.0
        self.kd_linear = 0.0

        self.kp_angular = 1.0
        self.kd_angular = 0.0
        self.ki_angular = 0.0

        self.linear_error_sum = 0.0
        self.angular_error_sum = 0.0
        self.last_linear_error = 0.0
        self.last_angular_error = 0.0

        self.robot_pose = [0.0, 0.0, 0.0]
        self.target = [0.0, 0.0]
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', qos_profile=rclpy.qos.QoSProfile(
                reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
                history=rclpy.qos.HistoryPolicy.KEEP_LAST,
                depth=10))
        self.create_subscription(Odometry, '/camera/pose/sample',self.pose_callback, qos_profile=rclpy.qos.QoSProfile(
                reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
                history=rclpy.qos.HistoryPolicy.KEEP_LAST,
                depth=10))

        self.cli_target_service = self.create_service(SetTarget, 'set_target', self.target_callback)

        self.create_timer(0.001, self.timer_callback)

    def timer_callback(self):
        diff_x = self.target[0] - self.robot_pose[0]
        diff_y = self.target[1] - self.robot_pose[1]
        diff_theta = 0.0 - self.robot_pose[2]
        distance = np.sqrt(diff_x**2 + diff_y**2)

        p_linear = self.kp_linear * distance
        self.linear_error_sum += distance
        i_linear = self.ki_linear * self.linear_error_sum
        d_linear = self.kd_linear * (distance - self.last_linear_error)
        linear_velocity = p_linear + i_linear + d_linear

        vx = min(max(linear_velocity, -0.3), 0.3)

        p_angular = self.kp_angular * diff_theta
        self.angular_error_sum += diff_theta
        i_angular = self.ki_angular * self.angular_error_sum
        d_angular = self.kd_angular * (diff_theta - self.last_angular_error)
        angular_velocity = p_angular + i_angular + d_angular

        wz = min(max(angular_velocity, -0.06), 0.06)

        self.cmdvel(vx, wz)

        if distance < 0.01 and abs(diff_theta) < 0.01:
            self.cmdvel(0.0, 0.0)
            self.linear_error_sum = 0.0
            self.angular_error_sum = 0.0
        
        self.last_linear_error = distance
        self.last_angular_error = diff_theta

    def cmdvel(self, v, w):
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self.cmd_vel_pub.publish(msg)

    def pose_callback(self, msg):
        self.robot_pose[0] = msg.pose.pose.position.x
        self.robot_pose[1] = msg.pose.pose.position.z
        
        quaternion = msg.pose.pose.orientation
        self.robot_pose[2] = self.quaternion_to_pitch(quaternion.x, quaternion.y, quaternion.z, quaternion.w)

    @staticmethod
    def quaternion_to_pitch(x, y, z, w):
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        return pitch

    def target_callback(self, request:SetTarget.Request, response:SetTarget.Response):
        self.target[0] = request.target.x 
        self.target[1] = request.target.y
        return response

def main(args=None):
    rclpy.init(args=args)
    node = Realsense()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()