import rclpy
import time
import requests

from rclpy.node import Node
from nav_msgs.msg import Odometry


URL = "http://10.150.149.248:8080/robot/position"

class OdomSubscriber(Node):
    def __init__(self):
        super().__init__('odom_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        pose = msg.pose.pose
        position = pose.position

        datas = {
            "x": round(position.x, 6),
            "y": round(position.y, 6), 
            "z": round(position.z, 6)
        }

        response = requests.post(URL, json=datas)

        self.get_logger().info('x=%f, y=%f, z=%f' % (round(position.x, 6), round(position.y, 6), round(position.z, 6)))

def main():
    rclpy.init()
    odom_subscriber = OdomSubscriber()
    
    try:
        while True:
            rclpy.spin_once(odom_subscriber)  # Spin once per iteration
            time.sleep(1)  # Wait for 1 second before the next iteration
    except KeyboardInterrupt:
        pass  # Exit cleanly on Ctrl+C
    
    odom_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
