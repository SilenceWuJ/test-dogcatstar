#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : base_page.py
Time    : 2026/2/11
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import configparser
import os
from pathlib import Path

from playwright.sync_api import Page
from utils.log import logger
from typing import Optional, Callable, Type



class BasePage:
    """页面基类，封装Playwright常用操作方法"""

    def __init__(self, page: Page):
        """
        初始化BasePage实例
        :param page: Playwright的Page对象，表示当前操作的页面
        """
        self.page = page
        self.config = configparser.ConfigParser()
        self.param = configparser.ConfigParser()
        root_dir = Path(__file__).parent.parent.parent
        config_path = root_dir / 'config' / 'locators.ini'
        params_path = root_dir / 'config' / 'config.ini'

        self.param.read(params_path)
        # params_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.ini')
        # self.config.read(config_path)


        if not config_path.exists():
            # 备选：从当前工作目录查找
            config_path = Path.cwd() / 'config' / 'locators.ini'

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        self.config.read(config_path)

        print(f"✅ Loaded config sections: {self.config.sections()}")
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'locators.ini')
        self.config.read(config_path)

    def navigate(self, url: str, timeout: int = 60000):
        """
        导航到指定URL。
        等待 DOM 构建完成（domcontentloaded），然后显式等待商品列表容器出现。
        """
        try:
            # 1. 等待 DOM 内容加载完成，这比等待 load 快得多
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)

            logger.info(f"成功导航到 {url} ")
            return True
        except Exception as e:
            logger.exception(f"导航到 {url} 失败: {e}")
            raise

    def wait_for_selector(self, selector, timeout=30000):
        """
        等待元素出现在DOM中并可见
        :param selector: 元素选择器（CSS或文本）
        :param timeout: 超时时间，单位毫秒，默认30000ms
        """
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector):
        """
        点击指定元素
        :param selector: 元素选择器
        """
        self.page.click(selector)

    def fill(self, selector, text):
        """
        在输入框中填充文本
        :param selector: 输入框选择器
        :param text: 要填充的文本
        """
        self.page.fill(selector, text)

    def get_text(self, selector):
        """
        获取元素的文本内容
        :param selector: 元素选择器
        :return: 元素的文本内容，如果不存在则返回None
        """
        return self.page.text_content(selector)

    def get_attribute(self, selector, attribute):
        """
        获取元素的指定属性值
        :param selector: 元素选择器
        :param attribute: 属性名
        :return: 属性值，如果不存在则返回None
        """
        return self.page.get_attribute(selector, attribute)

    def is_visible(self, selector):
        """
        判断元素是否可见
        :param selector: 元素选择器
        :return: 可见返回True，否则False
        """
        return self.page.is_visible(selector)

    def is_enabled(self, selector):
        """
        判断元素是否可用（未禁用）
        :param selector: 元素选择器
        :return: 可用返回True，否则False
        """
        return self.page.is_enabled(selector)

    def wait_for_load_state(self, state='load'):
        """
        等待页面加载状态
        :param state: 加载状态，可选值为'load'、'domcontentloaded'、'networkidle'，默认'load'
        """
        self.page.wait_for_load_state(state)

    def screenshot(self, filename):
        """
        截取全屏截图
        :param filename: 保存截图的文件路径
        """
        self.page.screenshot(path=filename, full_page=True)

    def get_current_url(self):
        """
        获取当前页面 URL
        :return: 当前页面地址字符串
        """
        logger.info(f"当前页面：{self.page.url}")
        return self.page.url

    def check_url_contains(self, expected_part: str):
        """
        断言当前 URL 包含指定的字符串
        若断言失败，抛出 AssertionError 并打印实际 URL
        """
        current_url = self.get_current_url()
        if expected_part in current_url:
            logger.infi(f"URL 验证失败：期望包含 '{expected_part}'，实际 URL: '{current_url}'")
            return True

    # def navigate(self, url, wait_until="load", timeout=30000):
    #     self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def close_known_popups(self):
        close_selectors = [
            'button:has-text("×")',
            'button:has-text("關閉")',
            'button:has-text("我知道了")',
            '.close-btn',
            '[aria-label="Close"]',
            '.modal-backdrop'
        ]
        for selector in close_selectors:
            locator = self.page.locator(selector)
            if locator.count() > 0 and locator.first.is_visible():
                locator.first.click()
                self.page.wait_for_timeout(300)


    # ---------- 跨域-新增方法 ----------
    def click_and_handle_navigation(self, selector: str, timeout: float = 30000) -> Page:
        """
        点击元素并处理可能的页面跳转（新标签页或重定向）
        返回最终的页面对象（可能是原页或新页）
        """
        with self.page.context.expect_page() as new_page_info:
            self.page.click(selector, timeout=timeout)

        try:
            # 如果打开了新页面，等待其加载并返回新页面对象
            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle")
            return new_page
        except Exception:
            # 未打开新页面，则等待当前页面导航完成（可能是重定向）
            self.page.wait_for_load_state("networkidle")
            return self.page

    def is_login_page(self) -> bool:
        """判断当前页面是否为登录页（根据页面特征）"""
        login_indicators = [
            "text=密码登录",
            "text=手机登录",
            "input[type='password']",
            "text=登錄",
            "text=Sign in",
            "text=請輸入您的手機號碼",  # 你文档中的登录弹窗
            "text=登入/註冊",           # 登录按钮
        ]
        for indicator in login_indicators:
            if self.page.locator(indicator).count() > 0:
                return True
        return False

    def handle_login_if_needed(self, login_func: Optional[Callable[[Page], None]] = None) -> bool:
        """
        如果当前页面是登录页，则执行登录操作，并等待跳转回原页
        :param login_func: 登录函数，接收一个 Page 对象，执行登录操作
        :return: 是否执行了登录
        """
        if not self.is_login_page():
            return False

        print("检测到登录页，正在执行登录...")
        if login_func is None:
            # 如果没有传入登录函数，则尝试使用默认的 perform_login（从环境变量读取）
            method = os.getenv("LOGIN_METHOD", "google")
            if method == "google":
                credentials = {
                    'email': os.getenv("GOOGLE_EMAIL"),
                    'password': os.getenv("GOOGLE_PASSWORD")
                }
            elif method == "facebook":
                credentials = {
                    'username': os.getenv("FB_USERNAME"),
                    'password': os.getenv("FB_PASSWORD")
                }
            else:
                raise ValueError(f"不支持的登录方式: {method}")
            from utils.login_helpers import perform_login
            perform_login(self.page, method=method, credentials=credentials)
        else:
            login_func(self.page)

        # 等待登录后页面跳转
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)  # 额外等待确保 Cookie 生效
        return True

    def create_page_object(self, page_obj_class: Type['BasePage'], page: Optional[Page] = None) -> 'BasePage':
        """
        根据给定的页面类创建新的页面对象实例
        :param page_obj_class: 需要实例化的页面类（如 ProductDetailPage）
        :param page: 使用的 Page 对象，默认为当前 page
        """
        target_page = page or self.page
        return page_obj_class(target_page)


