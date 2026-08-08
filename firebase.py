import requests
import json

FIREBASE_URL = "https://sacho1-default-rtdb.firebaseio.com"

def read_data(path=""):
    """Read data from Firebase"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error reading data: {e}")
        return None

def write_data(path, data):
    """Write/Set data to Firebase (overwrites existing)"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        response = requests.put(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error writing data: {e}")
        return False

def update_data(path, data):
    """Update specific fields in Firebase (preserves other fields)"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        response = requests.patch(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating data: {e}")
        return False

def delete_data(path):
    """Delete data from Firebase"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting data: {e}")
        return False

def push_data(path, data):
    """Push data with auto-generated unique key"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()  # Returns the generated key
    except requests.exceptions.RequestException as e:
        print(f"Error pushing data: {e}")
        return None

if __name__ == "__main__":
    # Testing functions
    print("Testing Firebase Connection...")
    
    # Read root data
    data = read_data()
    print(f"Root Data: {data}")
    
    # Test write
    # write_data("test/test1", {"name": "Test", "value": 123})
    
    # Test update
    # update_data("test/test1", {"value": 456})
    
    # Test delete
    # delete_data("test/test1")
    
    # Test push
    # push_data("test", {"name": "New Item"})
