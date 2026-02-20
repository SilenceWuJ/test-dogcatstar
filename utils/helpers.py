#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : helpers.py
Time    : 2026/2/11 
Author  : xixi
File    : api/utils
#-------------------------------------------------------------
"""


class TesHelpers:
    @staticmethod
    def setup_browser_context(page, url="https://www.dogcatstar.com/"):
        """设置浏览器上下文"""
        page.goto(url)
        page.wait_for_load_state('networkidle')


    @staticmethod
    def get_test_data():
        """获取测试数据"""
        return {
            'regions': ['TW', 'HK', 'SG', 'MY'],
            'languages': ['zh_TW', 'zh_HK', 'en_US']
        }


    @staticmethod
    def assert_region_language_logic(region, language):
        """断言地区和语言的逻辑关系"""
        if region == 'TW':
            assert language == 'zh_TW', "台湾地区应默认繁体中文(台湾)"
        else:
            assert language == 'en_US', f"{region}地区应默认英文"


    @staticmethod
    def login_with_google(common_actions):
        """使用Google登录"""
        test_data = TesHelpers.get_test_data()
        common_actions.google_login(
            test_data['google_email'],
            test_data['google_password']
        )


    @staticmethod
    def get_test_data():
        """获取测试数据"""
        return {
            'google_email': 'xxx',
            'google_password': 'xxxx',
            'phone_numbers': {
                'valid_tw': '987654321',
                'invalid_short': '123',
                'invalid_chars': 'abcdefg'
            },
            'regions': ['TW', 'HK', 'SG', 'MY'],
            'languages': ['zh_TW', 'zh_HK', 'en_US']
        }


    @staticmethod
    def tes_phone_number_format(login_page, phone_numbers):
        """测试手机号格式验证"""
        results = {}

        for name, phone in phone_numbers.items():
            login_page.enter_phone_number(phone)

            # 检查按钮状态
        is_enabled = login_page.is_login_button_enabled()

        # 检查错误提示
        error_visible = login_page.is_phone_format_error_visible()
        error_text = login_page.get_phone_format_error_text() if error_visible else None

        results[name] = {
            'phone': phone,
            'button_enabled': is_enabled,
            'error_visible': error_visible,
            'error_text': error_text
        }


        return results


    @staticmethod
    def verify_login_success(common_actions, login_page):
        """验证登录成功"""
        # 检查cookie
        userid = common_actions.get_cookie('userid')
        if not userid:
            return False

        # 检查页面状态
        is_logged_in = login_page.is_user_logged_in()
        if not is_logged_in:
            return False

        # 检查URL - 应该重定向到购物车或我的页面
        current_url = login_page.page.url
        if 'cart' in current_url or 'my-account' in current_url:
            return True

        # 检查是否有登录成功提示
        try:
            # 查找欢迎信息或其他登录成功标识
            welcome_text = login_page.page.text_content('body')
            if '歡迎' in welcome_text or 'Welcome' in welcome_text:
                return True
        except:
            pass

        return userid is not None


    @staticmethod
    def get_login_test_data():
        """获取登录测试数据"""
        return {
            'google': {
                'email': '',
                'password': ''
            },
            'phone_numbers': {
                'valid_tw': '987654321',
                'valid_tw_with_zero': '0912345678',
                'invalid_short': '123',
                'invalid_long': '123456789012345',
                'invalid_chars': 'abc123def',
                'empty': ''
            },
            'country_codes': ['+886', '+65', '+852', '+60'],
            'verification_codes': {
                'test': '123456',
                'invalid': '000000'
            }
        }



