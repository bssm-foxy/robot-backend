import rclpy
import yaml
import time 
import threading
import math
import requests

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose

from API.GetStartPosition import GetStartPosition
from API.GetRobotPosition import GetRobotPosition


class MoveToGoal:
    def __init__(self):
        self.PointName = None 
        self.Point_X = None 
        self.Point_Y = None

    def wait_for_start_point(self):
        if self.PointName is None:
            while True:
                
                self.PointName = GetStartPosition()["point_name"]
                self.Point_X = GetStartPosition()["position_x"]
                self.Point_Y = GetStartPosition()["position_y"]

                if self.PointName:
                    print(f"출발지 설정 완료: {self.PointName}")
                    break
                else:
                    print("출발지 설정 대기 중...")
                    time.sleep(1)

    def move(self):
        self.wait_for_start_point() 
        rclpy.init()
        node = rclpy.create_node('move_to_goal')
        goal_publisher = node.create_publisher(PoseStamped, '/goal_pose', 10)

        print(f"출발지: {self.PointName}, 좌표: ({self.Point_X}, {self.Point_Y})")

        goal_pose = PoseStamped()
        goal_pose.pose.position.x = float(self.Point_X)
        goal_pose.pose.position.y = float(self.Point_Y)
        goal_pose.pose.position.z = 0.050000
        goal_pose.pose.orientation.w = 1.0  # 기본 방향으로 설정

        for i in range(5):
            time.sleep(1)
            goal_publisher.publish(goal_pose)

        node.destroy_node()
        rclpy.shutdown()

    @classmethod
    def post_arrived_true(self):
        url = "http://10.150.149.248:8080/robot/arrived"
        response = requests.post(url)

        if response.status_code == 200:
            print(response.json()["Success_or_not"])
        else:
            print(response.status_code)

    def compare_position(self):
        arrival_threshold = 0.3  # ±0.3 오차 범위 설정

        while True:
            try:
                latest_x = float(GetRobotPosition()["point_x"])
                latest_y = float(GetRobotPosition()["point_y"])

                distance_to_goal = math.sqrt((latest_x - self.Point_X)**2 + (latest_y - self.Point_Y)**2)

                if distance_to_goal <= arrival_threshold:
                    print(f"로봇이 출발지에 도착하였습니다.")
                    break
                else:
                    print(f"아직 도착하지 않음. 현재 위치: ({latest_x}, {latest_y})")

                time.sleep(1)
            except TypeError as e:
                time.sleep(1)
                print("로봇 위치 추척 코드가 실행되고 있지 않습니다.")

        self.post_arrived_true()
        

if __name__ == '__main__':
    a = MoveToGoal()
    a.wait_for_start_point()
    a.move()
    a.compare_position()
