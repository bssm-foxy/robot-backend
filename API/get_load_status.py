import requests 

BASE_URL = "http://10.150.149.248:8080"

def check_load_status():
    url = f"{BASE_URL}/isload"
    response = requests.get(url) 

    if response.status_code == 200: 
        data = response.json() 

        if data:
            print(data["number"])
            return data["number"]
    else:
        print(response.status_code)


if __name__ == "__main__":
    check_load_status()