import pytest
import requests
BASE_URL = "http://localhost:8000" 
@pytest.fixture
def token():
    """先获取token"""
    resp= requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": "testuser",
        "password": "123456"
    })
    return resp.json()["access_token"]
def test_upload_without_token():
    """测试上传文件时不带token的情况"""
    files = {"file": ("test.txt", b"This is a test file.","text/plain")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files)
    assert resp.status_code == 401

def test_upload_with_token(token):
    """测试上传文件时带token的情况"""
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test.txt", b"This is a test file.","text/plain")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=headers, files=files)
    assert resp.status_code  in [200,500]
