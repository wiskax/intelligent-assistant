import requests
BASE_URL = "http://localhost:8000"
def test_documents_with_token(auth_headers):
    """带token请求受保护接口，返回200"""
    resp = requests.get(f"{BASE_URL}/api/v1/documents", headers=auth_headers)
    assert resp.status_code == 200

def test_documents_returns_list(auth_headers):
    """带token请求受保护接口，返回文档列表"""
    resp = requests.get(f"{BASE_URL}/api/v1/documents", headers=auth_headers)
    data = resp.json()
    assert isinstance(data, list)