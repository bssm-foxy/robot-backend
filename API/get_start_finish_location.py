# 시작 위치 좌표 받아오는 코드 
import requests 


def get_start_location_info():
    url = "http://10.150.149.248:8080/robot/get_start_location_info"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json() 
        return data
                
    else:
        print(response.status_code)

def get_finish_location_info():
    url = "http://10.150.149.248:8080/robot/get_finish_location_info"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json() 
        return data
                
    else:
        print(response.status_code)


if __name__ == "__main__":
    data = get_finish_location_info()
    print(data)