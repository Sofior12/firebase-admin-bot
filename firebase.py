import requests

FIREBASE_URL = "https://sacho1-default-rtdb.firebaseio.com"

def read_data(path="/"):
    url = f"{FIREBASE_URL}/{path}.json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

if __name__ == "__main__":
    data = read_data()
    print(data)
