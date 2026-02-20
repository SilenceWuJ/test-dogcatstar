#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : login_helpers.py
Time    : 2026/2/19 
Author  : xixi
File    : utils
#-------------------------------------------------------------
"""
from playwright.sync_api import Page
from utils.log import logger
import time
import re
from ui.pages.login_page import LoginPage


def perform_google_login(page, email: str, password: str):
    """执行 Google 登录流程"""

    login_page = LoginPage(page)

    login_page.navigate(url="https://www.dogcatstar.com/my-account/")

    #
    login_page.wait_for_login_modal()

    login_page.click_google_login_button()



    try:
        # --- 第一步：输入邮箱 ---
        # 使用 id 定位邮箱输入框，非常稳定（id="identifierId"）
        email_input = page.locator('#identifierId').first
        email_input.wait_for(state='visible', timeout=10000)
        email_input.fill(email)
        logger.info("已输入邮箱")
        time.sleep(5)

        # --- 第二步：点击“下一步”按钮 ---
        # 使用正则匹配中英文按钮文本
        next_button = page.get_by_role("button", name=re.compile("Next|下一步")).first
        next_button.wait_for(state='visible', timeout=10000)
        next_button.click()
        logger.info("点击下一步按钮")
        time.sleep(5)

        # --- 第三步：等待并输入密码 ---
        # 使用 name 属性定位密码输入框（name="Passwd"）
        password_input = page.locator('input[name="Passwd"]').first
        password_input.wait_for(state='visible', timeout=10000)
        password_input.fill(password)
        logger.info("已输入密码")
        time.sleep(5)
        # # --- 第四步：点击“下一步”按钮 ---
        next_button = page.get_by_role("button", name=re.compile("Next|下一步")).first
        next_button.wait_for(state='visible', timeout=10000)
        next_button.click()
        logger.info("点击下一步按钮")
        time.sleep(3)

        # --- 第五步：等待登录成功并重定向到汪喵星球域名此时没有判断具体路径，具体路径判断需要到具体的测试用例中 ---
        # self.page.wait_for_url("**/my-account/**", timeout=timeout)
        page.wait_for_url("**www.dogcatstar.com**", timeout=10000)

        logger.info("Google 内嵌登录成功，已重定向")
        return True

    except Exception as e:
        logger.exception(f"Google 内嵌登录失败: {e}")
        return False


def perform_facebook_login(page: Page, username: str, password: str):
    """执行 Facebook 登录流程"""
    page.get_by_role("button", name="使用 Facebook 帳號登入").click()
    # ... 处理 Facebook 登录 ...

def perform_phone_login(page: Page, phone: str, code: str):
    """执行手机号登录流程"""
    # ... 处理手机号、验证码 ...
    pass
# 定义一个统一的登录入口
def perform_login(page, method: str, credentials: dict):
    """根据指定的 method 执行登录"""
    if method == "google":
        perform_google_login(page, credentials['email'], credentials['password'])
        print("登录成功")
    elif method == "facebook":
        perform_facebook_login(page, credentials['username'], credentials['password'])
    elif method == "phone":
        perform_phone_login(page, credentials['phone'], credentials['code'])
    else:
        raise ValueError(f"不支持的登录方式: {method}")