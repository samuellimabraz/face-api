from fastapi.testclient import TestClient
from dotenv import load_dotenv
import os
import time

from src.api.main import app

load_dotenv()
client = TestClient(app)

def test_create_organization():
    response = client.post("/orgs", json={"organization": "test_org"})
    assert response.status_code == 200
    assert response.json() == {"message": "Organization created successfully"}

def test_create_api_key(api_key_name: str = "test_key"):
    response = client.post(
        "/orgs/test_org/api-key", 
        json={"user": "test_user", "api_key_name": api_key_name}
    )
    json_response = response.json()
    print(json_response)
    
    assert response.status_code == 200
    assert "key" in json_response
    assert json_response["user"] == "test_user"
    
    return response.json()["key"]

def test_duplicate_api_key():
    user = "test_user"
    api_key_name = "test_key_2"
    org = "test_org"
    
    response1 = client.post(
        f"/orgs/{org}/api-key", 
        json={
            "user": user, 
            "api_key_name": api_key_name
        }
    )
    response2 = client.post(
        f"/orgs/{org}/api-key", 
        json={
            "user": user, 
            "api_key_name": api_key_name
        }
    )
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert response2.json() == {"detail": f"Failed to create API key"}
    

def test_revoke_api_key():
    api_key = test_create_api_key("test_key_to_remove")
    time.sleep(1.0)
    response = client.request(
        method="DELETE",
        url="/orgs/test_org/api-key",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "api_auth": {
                "user": "test_user",
                "api_key_name": "test_key_to_remove"
            }
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "API key revoked successfully"}

def test_register_person():
    api_key = test_create_api_key("test_key_to_register")
    root_dir = "/home/samuel/Codes/unifei/ecot01a/project/assets/images"
    
    images = [os.path.join(root_dir, path) for path in os.listdir(root_dir) if path.endswith(".jpg")]
    print(images)
    response = client.post(
        "/register/test_org", 
        json={
            "images": images, "name": "José",
            "api_auth": {
                "user": "test_user",
                "api_key_name": "test_key_to_register"
            }
        },
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

def test_recognize_person():
    api_key = test_create_api_key("test_key_to_recognize")
    root_dir = "/home/samuel/Codes/unifei/ecot01a/project/assets/images"
    image_name = "test_image.jpg"
    
    response = client.post(
        "/recognize/test_org", 
        json = {
            "image": os.path.join(root_dir, image_name), 
            "threshold": 0.5,
            "api_auth": {
                "user": "test_user",
                "api_key_name": "test_key_to_recognize"
            }
        },
        headers={"Authorization": f"Bearer {api_key}"}
    )
    json_response = response.json()
    print(json_response)
    assert response.status_code == 200
    assert json_response["searchs"][0]["name"] == "José"
    assert json_response["searchs"][0]["distance"] > 0.5
    
