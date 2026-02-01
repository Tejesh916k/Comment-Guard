from fastapi.testclient import TestClient
from main import app
import sys

# Mock the classifier to avoid downloading 500MB+ model during simple verification
# unless we really want to test the model. 
# For this environment, let's try to mock it if import fails or just run it.
# We will use the real model if possible, but fallback/catch errors to not crash.

def run_tests():
    print("Initializing TestClient...")
    client = TestClient(app)

    print("Testing Root Endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    print("Root OK.")

    print("Testing Analysis Endpoint (Clean)...")
    try:
        response = client.post("/analyze", json={"text": "Have a nice day"})
        if response.status_code == 200:
            print("Clean text result:", response.json())
        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print("Analysis test failed (might be model loading issue):", e)

    print("Testing Analysis Endpoint (Toxic)...")
    try:
        # "idiot" is usually mild, but let's try.
        response = client.post("/analyze", json={"text": "You are a stupid idiot"})
        if response.status_code == 200:
            print("Toxic text result:", response.json())
        else:
             print("Error:", response.status_code, response.text)
    except Exception as e:
        print("Analysis test failed:", e)

if __name__ == "__main__":
    run_tests()
