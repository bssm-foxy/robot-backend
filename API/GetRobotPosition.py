import requests 


def GetRobotPosition():
    url = "http://10.150.149.248:8080/robot/position"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json() 

        if data["Success_or_not"]:
            return data["Position"]
        else: 
            print("not created position")

    else:
        print(response.status_code)


if __name__ == "__main__":
    print(GetRobotPosition())