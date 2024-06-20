import requests 


def GetStartPosition():
    url = "http://10.150.149.248:8080/robot/get_start_point"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json() 
        return data
                
    else:
        print(response.status_code)


if __name__ == "__main__":
    start_class_name = GetStartPosition()
    print(start_class_name)