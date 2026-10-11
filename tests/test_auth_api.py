import pytest
import requests
BASE_URL = "http://localhost:8000"
def test_login_success():
    """先获取token"""
    resp= requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": "testuser",
        "password": "123456"
        })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
def test_login_wrong_password():
    """测试密码错误返回401"""
    resp= requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": "testuser",
        "password": "wrong"
        })
    assert resp.status_code == 401
def test_login_without_token():
    """不带token请求受保护接口，返回401"""
    resp = requests.get(f"{BASE_URL}/api/v1/documents")
    assert resp.status_code == 401
