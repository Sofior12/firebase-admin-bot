import requests

FIREBASE_URL = "https://sacho1-default-rtdb.firebaseio.com"

def read_data(path=""):
    url = f"{FIREBASE_URL}/{path}.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Root data
    data = read_data()
    print(data)

    # Examples:
    # print(read_data("All_Users"))
    # print(read_data("All_Users/simDetails"))
    # print(read_data("All_Users/Data/DeviceInfo"))
