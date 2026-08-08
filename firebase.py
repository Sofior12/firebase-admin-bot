import requests
import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_URL = os.getenv("FIREBASE_DB_URL", "https://sacho1-default-rtdb.firebaseio.com")

def read_data(path=""):
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error reading data: {e}")
        return None

def write_data(path, data):
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.put(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error writing data: {e}")
        return False

def update_data(path, data):
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.patch(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating data: {e}")
        return False

def delete_data(path):
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting data: {e}")
        return False
