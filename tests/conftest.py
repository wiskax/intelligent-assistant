import pytest
import requests
import os
import sys
import time
import subprocess
BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    print("🚀fixture被执行了")
    """在测试开始前启动FastAPI服务器，并在测试结束后关闭它"""
    # 启动uvicorn（后台运行）
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    #等待服务器启动（最多等60S）
    for i in range(60):
        try:
            resp = requests.get(f"{BASE_URL}/docs", timeout=2)
            if resp.status_code == 200:
                print(f"\n✅ 服务器已启动（等待 {i+1} 秒）")
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        process.kill()
        raise RuntimeError("服务器启动超时")

    yield  # 测试运行期间

    # 测试结束后终止服务器
    process.terminate()
    process.wait()
    print("\n🛑 服务器已关闭")


@pytest.fixture(scope="session",autouse=True)
def setup_test_user(start_server):
    """在测试开始前创建一个测试用户"""
    # 创建测试用户
    resp = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
        "username": "testuser",
        "password": "123456",
        "email": "test@example.com"
    })
    assert resp.status_code in [200, 400]  # 如果用户已存在，可能返回400

    yield
    # 测试结束后删除测试用户    
    

@pytest.fixture(scope="session")
def token(start_server):
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

