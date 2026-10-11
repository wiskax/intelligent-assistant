import pytest
import requests
BASE_URL = "http://localhost:8000"
@pytest.fixture(scope="session")
def token():
    """先获取token"""
    resp= requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": "testuser",
        "password": "123456"
    })
    return resp.json()["access_token"]
@pytest.fixture
def auth_headers(token):
    """返回带token的请求头"""
    return {"Authorization": f"Bearer {token}"}
@pytest.fixture
def upload_doc_ids(auth_headers):
    doc_ids = []
    yield doc_ids
    # 清理上传的文档
    for doc_id in doc_ids:
        resp = requests.delete(f"{BASE_URL}/api/v1/documents/{doc_id}", headers=auth_headers)
        print(f"\n🧹 清理文档 id={doc_id}，状态码={resp.status_code}")

def test_upload_kong_token(auth_headers):
    """上传空文件时带token的情况"""
    files = {"file": ("test.txt", b"","text/plain")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=auth_headers, files=files)
    if resp.status_code == 200:
        doc_id = resp.json().get("id")
        if doc_id:
            upload_doc_ids.append(doc_id)
    assert resp.status_code  in [200,400,422,500]
def test_upload_unsupported_type(auth_headers):
    """测试上传不支持的文件类型"""
    files = {"file": ("test.exe", b"This is a test file.","application/octet-stream")}
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=auth_headers, files=files)
    if resp.status_code == 200:
        doc_id = resp.json().get("id")
        if doc_id:
            upload_doc_ids.append(doc_id)
    
    assert resp.status_code in [400,415,422]
def test_upload_no_file(auth_headers):
    """测试上传时不带文件的情况"""
    resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=auth_headers)
    assert resp.status_code == 422