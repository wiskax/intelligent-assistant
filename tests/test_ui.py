from playwright.sync_api import sync_playwright
import time
def test_login_page():
    """测试完整的登录流程"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8000")  # Replace with your application's URL
        assert "智能知识库" in page.title()  # Replace with the expected title of your application
        browser.close()
    