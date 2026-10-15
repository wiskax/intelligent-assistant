from playwright.sync_api import sync_playwright
import time
def test_login_page():
    """测试完整的登录流程"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        #1.打开首页
        page.goto("http://localhost:8000")  # Replace with your application's URL
        assert "智能知识库" in page.title()  # Replace with the expected title of your application

        #2.用id定位用户名输入框
        page.fill("#loginUsername", "testuser") 
        
        #3.用 id 定位密码输入框
        page.fill("#loginPassword", "123456")

        #4.用 id 定位登录按钮并点击
        page.click("#loginBtn")
        
        #5.等待页面响应
        time.sleep(2)

        #6.截图
        page.screenshot(path="login_result.png")

        #7.断言登录成功
        assert "testuser" in page.content()
        browser.close()
    