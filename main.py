import rclpy
import time 
import math
import requests
import threading

from threading import Event
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


from API.get_realtime_robot_location import get_realtime_locatioin_info
from API.get_start_finish_location import get_start_location_info, get_finish_location_info
from API.get_load_status import check_load_status

# BASE_URL = "http://192.168.25.24:8080"
BASE_URL = "http://10.150.149.248:8080"

class MoveToGoal():
    def __init__(self, start_or_finish):
        self.location_name = None
        self.location_x = None
        self.location_y = None 
        self.start_or_finish = start_or_finish
    
    def set_start_location(self):
        self.location_name = get_start_location_info()["location_name"]
        self.location_x = get_start_location_info()["location_x"]
        self.location_y = get_start_location_info()["location_y"]

    def set_finish_location(self):
        self.location_name = get_finish_location_info()["location_name"]
        self.location_x = get_finish_location_info()["location_x"]
        self.location_y = get_finish_location_info()["location_y"]

    def wait_for_user_input(self):
        # 웹에서 유저의 입력을 기다림
        if self.location_name is None:
            while True: 
                if self.start_or_finish == "start":  
                    self.set_start_location()  # 출발지로 좌표 설정
                    if self.location_name:
                        print(f"출발지: {self.location_name} 으로/로 좌표가 설정되었습니다.")
                        break
                    else:
                        print("입력 대기 중...")
                else:  
                    self.set_finish_location()  # 도착지로 좌표 설정
                    if self.location_name:
                        print(f"도착지: {self.location_name} 으로/로 좌표가 설정되었습니다.")
                        break
                    else:
                        print("입력 대기 중...")

    def move(self):
        self.wait_for_user_input() 

        # print(self.location_x, self.location_y)

        rclpy.init()
        node = rclpy.create_node('move_to_goal')
        goal_publisher = node.create_publisher(PoseStamped, '/goal_pose', 10)

        goal_pose = PoseStamped()
        goal_pose.pose.position.x = float(self.location_x)
        goal_pose.pose.position.y = float(self.location_y)
        goal_pose.pose.position.z = 0.050000  # 2D 라이다를 사용하므로 고정값 사용
        goal_pose.pose.orientation.w = 1.0  # 기본 방향으로 설정

        # 노드 씹힘 문제 해결하기 위해 5번 전송
        for i in range(5): 
            time.sleep(1)
            goal_publisher.publish(goal_pose)

        node.destroy_node()
        rclpy.shutdown()

        return self.checking_arrived()

    def checking_arrived(self):
        arrival_threshold = 0.3  # ±0.3 오차 범위 설정

        while True:
            try:
                latest_x = float(get_realtime_locatioin_info()["x"])
                latest_y = float(get_realtime_locatioin_info()["y"])

                distance_to_goal = math.sqrt((latest_x - self.location_x)**2 + (latest_y - self.location_y)**2)

                if distance_to_goal <= arrival_threshold:
                    break
                else:
                    print(f"목적지로 가는 중... 현재 위치: ({latest_x}, {latest_y})")

                time.sleep(3)
            except TypeError as e:
                time.sleep(1)
                print("로봇 위치 추척 코드가 실행되고 있지 않습니다.")

        return self.set_arrived_true()

    def set_arrived_true(self) -> bool:
        if self.start_or_finish == "start":
            url = f"{BASE_URL}/robot/set_start_location_arrived"
        else:
            url = f"{BASE_URL}/robot/set_finish_location_arrived"
        response = requests.get(url)

        if response.status_code == 200:
            # print(response.json()["Success_or_not"])
            return True
        else:
            print(response.status_code)
            return False


def post_realtime_robot_location(counter, is_arrived):
    if counter == 0:
        rclpy.init()
    odom_subscriber = OdomSubscriber()

    try:
        while True:
            if is_arrived:
                break
            rclpy.spin_once(odom_subscriber) 
            time.sleep(1)  
    except KeyboardInterrupt:
        pass 

    odom_subscriber.destroy_node()
    rclpy.shutdown()

def move_to_goal(start_or_finish):
    # start: 출발지로 출발 
    # finish: 도착지로 출발
    # start_or_finish = "finish"

    counter = 0
    is_arrived = MoveToGoal(start_or_finish).move()

    while is_arrived is None:
        if is_arrived:
            post_realtime_robot_location(counter, is_arrived)


        else:
            print("error")
        
        counter += 1
    
    print(f"Arrived: {is_arrived}")


if __name__ == "__main__":
    start_url = f"{BASE_URL}/robot/check_arrived_status?start_or_finish=start"
    finish_url = f"{BASE_URL}/robot/check_arrived_status?start_or_finish=finish"

    counter = 0

    while True:
        response = requests.post(start_url)
        if response.status_code == 201:
            origin_number = response.json()["value"]["latest_number"]

            while True:
                time.sleep(1)  # 주기적으로 1초 대기

                response = requests.post(start_url)
                if response.status_code == 201:
                    latest_number = response.json()["value"]["latest_number"]
                    print(counter, "origin_number", origin_number, "latest_number", latest_number)

                    if origin_number != latest_number:
                        print("robot move to start goal")
                        move_to_goal("start")

                        ## my code 
                        while True:
                            is_load = check_load_status()

                            if is_load:
                                move_to_goal("finish")
                                break
                            else:
                                print("wait")
                                time.sleep(1)
                        break
                    else:
                        counter += 1
                        # print("same, counter:", counter)
                else:
                    print("Failed to get response, status code:", response.status_code)
                    break
        else:
            print("Failed to get initial response, status code:", response.status_code)
            break