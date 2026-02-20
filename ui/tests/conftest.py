#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : conftest.py
Time    : 2026/2/10
Author  : xixi
File    :
#-------------------------------------------------------------
"""

from playwright.sync_api import Page
import pytest
import json
from playwright.sync_api import Browser
import os,sys

from ui.pages.cart_page import CartPage
from ui.pages.base_page import BasePage
# 页面对象类
from ui.pages.common import CommonActions
from ui.pages.login_page import LoginPage
from ui.pages.main_page import MainPage
from ui.pages.my_page import MyPage
from ui.pages.cart_sidebar_page import CartSidebarPage
from ui.pages.product_detail_page import ProductDetailPage
from ui.pages.product_list_page import ProductListPage
from utils.login_helpers import perform_login
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# @pytest.fixture(scope="function", autouse=True) autouse=True 自动关闭弹窗；去掉后测试用例中需要自动关弹窗时显式依赖

@pytest.fixture(scope="function",autouse=True)
def auto_close_popups(page: Page):
    """
    自动关闭常见的干扰弹窗
    - 优惠券弹窗：点击 × 或「关闭」按钮
    - 订阅弹窗：点击「不再提示」或 ×
    特定测试临时禁用自动关闭：
    def test_something(page):
    # 临时移除某个 handler
    page.remove_locator_handler(coupon_close)
    # ... 测试逻辑
    """
    def log_and_click(locator):
        locator.click()
    # ---- 优惠/广告弹窗 ----
    coupon_close = page.locator('button:has-text("×"), button:has-text("关闭"), .close-btn, [aria-label="Close"]')
    page.add_locator_handler(coupon_close, lambda: coupon_close.click())

    # ---- 订阅/通知弹窗 ----
    subscribe_close = page.locator('button:has-text("稍后"), button:has-text("不再提示"), .subscribe-close')
    page.add_locator_handler(subscribe_close, lambda: subscribe_close.click())

    # ---- 通用模态层背景点击关闭 ----
    modal_backdrop = page.locator('.modal-backdrop, .overlay')
    page.add_locator_handler(modal_backdrop, lambda: modal_backdrop.click())
    # ---- 春节公告弹窗点击关闭 ----
    today_not_show = page.locator('p:has-text("今日不再顯示")')
    page.add_locator_handler(today_not_show, lambda: today_not_show.click())

    yield  # 测试执行
    # 无需清理，page 会在测试结束后关闭

@pytest.fixture(scope="session")

def browser(playwright):

    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-setuid-sandbox',
            '--disable-accelerated-2d-canvas',
            '--disable-web-security',  # 可选，但可能影响
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-blink-features=AutomationControlled',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-webgl',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-infobars',
            '--disable-breakpad',
            '--disable-crash-reporter',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',
        ]
        # page = browser.new_page()
        # headless=False,
        # args=[
        #     '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
        #     '--disable-dev-shm-usage',        # 解决 Docker 内存问题
        #     '--no-sandbox',                  # 避免沙盒限制
        #     '--disable-gpu',                 # 禁用 GPU（可选）
        #     '--window-size=1920,1080',
        # ]
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser, request):
    """
    参数化注入
    浏览器上下文 fixture，支持通过 request.param 传递 sessionStorage 预设值
    使用方式：@pytest.mark.parametrize('context', [{'key':'value'}], indirect=True)
    """

    context = browser.new_context(viewport={'width': 1366, 'height': 768})
    # 从 request.param 中获取预设
    storage_preset = getattr(request, 'param', {})
    ls_preset = storage_preset.get('localStorage', {})
    ss_preset = storage_preset.get('sessionStorage', {})

    # 构建 localStorage 初始化脚本
    ls_lines = []
    for key, value in ls_preset.items():
        if isinstance(value, dict):
            value = json.dumps(value)  # 确保复杂对象被 JSON 字符串化
        ls_lines.append(f"localStorage.setItem('{key}', '{value}');")

    # 构建 sessionStorage 初始化脚本
    ss_lines = []
    for key, value in ss_preset.items():
        ss_lines.append(f"sessionStorage.setItem('{key}', '{value}');")

    init_script = "\n".join(ls_lines + ss_lines)
    if init_script:
        context.add_init_script(init_script)

    yield context
    context.close()

@pytest.fixture(scope="function")
def base_page(page: Page) -> BasePage:
    """公共操作类实例"""
    return BasePage(page)


@pytest.fixture(scope="function")
def common_actions(page: Page) -> CommonActions:
    """公共操作类实例"""
    return CommonActions(page)


@pytest.fixture(scope="function")
def main_page(page: Page) -> MainPage:
    """主页面实例"""
    return MainPage(page)


@pytest.fixture(scope="function")
def product_list_page(page: Page) -> ProductListPage:
    """商品列表页面实例"""
    return ProductListPage(page)


@pytest.fixture(scope="function")
def product_detail_page(page: Page) -> ProductDetailPage:
    """商品详情页面实例"""
    return ProductDetailPage(page)


@pytest.fixture(scope="function")
def login_page(page: Page):
    """登录页面实例"""
    return LoginPage(page)


@pytest.fixture(scope="function")
def cart_page(page: Page) -> CartPage:
    """购物车页面实例"""
    return CartPage(page)


@pytest.fixture(scope="function")
def my_page(page: Page) -> MyPage:
    """我的页面实例"""
    return MyPage(page)

@pytest.fixture(scope="function")
def cart_sidebar_page(page: Page) -> CartSidebarPage:
    """我的页面实例"""
    return CartSidebarPage(page)

@pytest.fixture(scope="function")
def close_today_not_show(page: Page):
    locator = page.locator('p:has-text("今日不再顯示")')
    if locator.count() > 0 and locator.first.is_visible():
        locator.first.click()
        page.wait_for_timeout(300)


# ------------------ 测试前置 fixture ------------------
@pytest.fixture(scope="function")
def setup_test(page: Page, main_page: MainPage) -> MainPage:
    """
    导航至主页，等待 load 事件完成。
    超时时间设为 60 秒，并自动重试 3 次。
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            page.goto(
                "https://www.dogcatstar.com/",
                wait_until="load",      # load，更稳定
                timeout=100000          # 延长至 60 秒
            )
            # 可选：再等待一个关键元素出现，确保页面可交互
            page.wait_for_selector("body", timeout=10000)
            break
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            print(f"⏳ 页面加载超时，正在重试 ({attempt+1}/{max_retries})...")
            page.wait_for_timeout(2000)  # 等待2秒后重试
    return main_page



@pytest.fixture
def test_name(request):
    """返回当前测试的名称（可用于文件名）"""
    return request.node.name.replace("[", "_").replace("]", "_")  # 替换可能影响文件名的字符


# ---------------loginedd--------------------

load_dotenv()  # 加载 .env 文件

LOGIN_METHOD = os.getenv("LOGIN_METHOD", "google")
AUTH_FILE = f"auth_{LOGIN_METHOD}.json"


@pytest.fixture(scope="function")
def logged_in_page(browser: Browser, request):
    # 处理存储预设
    storage_preset = getattr(request, 'param', {})
    ls_preset = storage_preset.get('localStorage', {})
    ss_preset = storage_preset.get('sessionStorage', {})

    # 构建初始化脚本
    script_lines = []
    for key, value in ls_preset.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        script_lines.append(f"localStorage.setItem('{key}', '{value}');")
    for key, value in ss_preset.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        script_lines.append(f"sessionStorage.setItem('{key}', '{value}');")
    init_script = "\n".join(script_lines) if script_lines else None

    # 根据登录状态文件是否存在决定context创建方式
    if os.path.exists(AUTH_FILE):
        print("auth_file存在，加载登录状态")
        context = browser.new_context(
            storage_state=AUTH_FILE,
            viewport={'width': 1366, 'height': 768}
        )
    else:
        print("无登录状态，需要执行登录")
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        # 先添加存储注入脚本（登录前可能需要）
        if init_script:
            context.add_init_script(init_script)

        # 创建页面并执行登录
        page = context.new_page()
        page.goto("https://www.dogcatstar.com")

        if LOGIN_METHOD == "google":
            credentials = {
                'email': os.getenv("GOOGLE_EMAIL"),
                'password': os.getenv("GOOGLE_PASSWORD")
            }
        elif LOGIN_METHOD == "facebook":
            credentials = {
                'username': os.getenv("FB_USERNAME"),
                'password': os.getenv("FB_PASSWORD")
            }
        else:
            raise ValueError(f"不支持的登录方式: {LOGIN_METHOD}")

        print(f"执行登录:{LOGIN_METHOD}")
        perform_login(page, method=LOGIN_METHOD, credentials=credentials)

        # 等待登录成功（可根据实际情况调整等待条件）
        page.wait_for_url("**www.dogcatstar.com**", timeout=15000)
        print("登录成功，写入auth.file")
        context.storage_state(path=AUTH_FILE)

    # 如果登录状态下也需要添加存储脚本（且之前未添加），则添加
    if os.path.exists(AUTH_FILE) and init_script:
        context.add_init_script(init_script)

    # 从最终使用的context创建新页面并返回
    page = context.new_page()
    yield page
    context.close()

# @pytest.fixture(scope="function")
# def logged_in_page(browser: Browser, request):
#     """
#     返回一个已登录且注入了存储预设的页面对象。
#     该 fixture 会：
#     1. 根据是否存在 auth 文件决定是否登录。
#     2. 应用通过 parametrize 传入的 localStorage/sessionStorage 预设。
#     3. 返回一个 Page 实例，可直接用于页面对象。
#     """
#     # 1. 处理存储预设参数
#     storage_preset = getattr(request, 'param', {})
#     ls_preset = storage_preset.get('localStorage', {})
#     ss_preset = storage_preset.get('sessionStorage', {})
#     context = browser.new_context(viewport={'width': 1366, 'height': 768})
#
#     # 3. 在上下文上应用存储预设脚本（无论是否加载了登录状态）
#     script_lines = []
#     for key, value in ls_preset.items():
#         if isinstance(value, (dict, list)):
#             value = json.dumps(value, ensure_ascii=False)
#         script_lines.append(f"localStorage.setItem('{key}', '{value}');")
#     for key, value in ss_preset.items():
#         if isinstance(value, (dict, list)):
#             value = json.dumps(value, ensure_ascii=False)
#         script_lines.append(f"sessionStorage.setItem('{key}', '{value}');")
#
#     if script_lines:
#         context.add_init_script("\n".join(script_lines))
#
#     # 2. 创建上下文（可能加载登录状态）
#     if os.path.exists(AUTH_FILE):
#         print("auth_file存在")
#         context = browser.new_context(
#             storage_state=AUTH_FILE,
#             viewport={'width': 1366, 'height': 768}
#         )
#         page = context.new_page()
#     else:
#         # 无登录状态时，先创建空上下文
#         print("无登录状态")
#         context = browser.new_context(viewport={'width': 1366, 'height': 768})
#
#
#         page = context.new_page()
#         # page.goto("https://www.dogcatstar.com")
#
#         # 执行登录
#         if LOGIN_METHOD == "google":
#
#             credentials = {
#                 'email': os.getenv("GOOGLE_EMAIL"),
#                 'password': os.getenv("GOOGLE_PASSWORD")
#             }
#         elif LOGIN_METHOD == "facebook":
#             credentials = {
#                 'username': os.getenv("FB_USERNAME"),
#                 'password': os.getenv("FB_PASSWORD")
#             }
#         else:
#             raise ValueError(f"不支持的登录方式: {LOGIN_METHOD}")
#
#         print(f"执行登录:{LOGIN_METHOD}")
#
#         perform_login(page, method=LOGIN_METHOD, credentials=credentials)
#
#         print("登录成功，写入auth.file")
#
#         context.storage_state(path=AUTH_FILE)
#
#     yield page
#
#     context.close()



@pytest.fixture(scope="function")
def logined_base_page(logged_in_page):
    """公共操作类实例"""
    return BasePage(logged_in_page)


@pytest.fixture(scope="function")
def logined_common_actions(logged_in_page) -> CommonActions:
    """公共操作类实例"""
    return CommonActions(logged_in_page)


@pytest.fixture(scope="function")
def logined_main_page(logged_in_page) -> MainPage:
    """主页面实例"""
    return MainPage(logged_in_page)


@pytest.fixture(scope="function")
def logined_product_list_page(logged_in_page) -> ProductListPage:
    """商品列表页面实例"""
    return ProductListPage(logged_in_page)


@pytest.fixture(scope="function")
def logined_product_detail_page(logged_in_page) -> ProductDetailPage:
    """商品详情页面实例"""
    return ProductDetailPage(logged_in_page)


@pytest.fixture(scope="function")
def logined_login_page(logged_in_page):
    """登录页面实例"""
    return LoginPage(logged_in_page)


@pytest.fixture(scope="function")
def logined_cart_page(logged_in_page) -> CartPage:
    """购物车页面实例"""
    return CartPage(logged_in_page)


@pytest.fixture(scope="function")
def logined_my_page(logged_in_page) -> MyPage:
    """我的页面实例"""
    return MyPage(logged_in_page)

@pytest.fixture(scope="function")
def logined_cart_sidebar_page(logged_in_page):
    """加入购物车弹窗实例"""
    return CartSidebarPage(logged_in_page)

@pytest.fixture(scope="function")
def logined_close_today_not_show(logged_in_page):
    locator = logged_in_page.locator('p:has-text("今日不再顯示")')
    if locator.count() > 0 and locator.first.is_visible():
        locator.first.click()
        logged_in_page.wait_for_timeout(300)

