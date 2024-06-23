# 실시간 로봇 좌표 받아오는 코드 
import requests 


BASE_URL = "http://10.150.149.248:8080"


def get_realtime_locatioin_info():
    url = f"{BASE_URL}/robot/realtime_location"
    response = requests.get(url) 

    if response.status_code == 200: 
        data = response.json() 

        if data:
            return data["location_info"]
    else:
        print(f"실시간 좌표를 받아오는데에 실패하였습니다. 오류코드 [{response.status_code}]")


if __name__ == "__main__":
    data = get_realtime_locatioin_info() 

    print(data)
