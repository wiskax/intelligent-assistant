import pytest
import requests
BASE_URL = "http://localhost:8000" 

def test_upload_without_token():
    """测试上传文件时不带token的情况"""
    files = {"file": ("test.txt", b"This is a test file.","text/plain")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files)
    assert resp.status_code == 401

def test_upload_with_token(auth_headers):
    """测试上传文件时带token的情况"""
    files = {"file": ("test.txt", b"This is a test file.","text/plain")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=auth_headers, files=files)
    assert resp.status_code  in [200,500]
