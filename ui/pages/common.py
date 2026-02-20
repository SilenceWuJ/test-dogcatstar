#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : common.py
Time    : 2026/2/11 
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import datetime
import requests
from playwright.sync_api import Page
from utils.log import logger
import os
import json
from ui.pages.base_page import BasePage
from typing import Optional, Dict
from datetime import datetime


class CommonActions(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)


    def get_region_by_ip(self,use_proxy: bool = False, proxies: Optional[Dict] = None):
        """通过IP获取地区"""
        # IP 服务商列表，按优先级排序
        self.IP_SERVICES = [
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/json/',
                'timeout': 5,
                'parser': lambda data: {
                    'ip': data.get('ip'),
                    'country_code': data.get('country_code', '').upper(),
                    'country_name': data.get('country_name'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'timezone': data.get('timezone'),
                    'currency': data.get('currency')
                }
            },
            {
                'name': 'ip-api.com',
                'url': 'http://ip-api.com/json/',
                'timeout': 5,
                'parser': lambda data: {
                    'ip': data.get('query'),
                    'country_code': data.get('countryCode', '').upper(),
                    'country_name': data.get('country'),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'timezone': data.get('timezone'),
                    'currency': None
                }
            },
            {
                'name': 'ipinfo.io',
                'url': 'https://ipinfo.io/json',
                'timeout': 5,
                'parser': lambda data: {
                    'ip': data.get('ip'),
                    'country_code': data.get('country', '').upper(),
                    'country_name': None,
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'timezone': data.get('timezone'),
                    'currency': None
                }
            }
        ]
        for service in self.IP_SERVICES:
            try:
                response = requests.get(
                    service['url'],
                    timeout=service['timeout'],
                    proxies=proxies if use_proxy else None
                )
                if response.status_code == 200:
                    data = response.json()
                    ip_info = service['parser'](data)
                    print(f"  国家/地区: {ip_info.get('country_name', '未知')} ({ip_info.get('country_code', '未知')})")
                    return ip_info.get('country_code')
            except Exception as e:
                    print(f"从 {service['name']} 获取 IP 信息失败: {e}")
                    return None

    def get_session_storage(self, key: str) -> str:
        """安全地获取 sessionStorage 值，自动等待页面就绪"""
        # 等待至少 DOM 加载完成
        self.page.wait_for_load_state('domcontentloaded')
        if self.page.url == 'about:blank' or not self.page.url.startswith('http'):
            raise RuntimeError(f"Cannot access sessionStorage on page with URL: {self.page.url}")
        try:
            value = self.page.evaluate(f"() => sessionStorage.getItem('{key}')")
            logger.info(f"获取到 sessionStorage: {value}")

            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
        except Exception as e:
            # 如果仍然失败，重试一次
            self.page.wait_for_timeout(500)
            value = self.page.evaluate(f"() => sessionStorage.getItem('{key}')")
            logger.info(f"失败重试获取到sessionStorage: {value}")
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value

    def set_session_storage(self, key: str, value: str) -> None:
        """安全地设置 sessionStorage 值，自动等待页面就绪"""
        # 1. 确保页面已加载且具有合法源
        self.page.wait_for_load_state('domcontentloaded')
        if self.page.url == 'about:blank' or not self.page.url.startswith('http'):
            raise RuntimeError(f"Cannot access sessionStorage on page with URL: {self.page.url}")

        # 2. 设置值
        try:
            self.page.evaluate(f"() => sessionStorage.setItem('{key}', '{value}')")
            logger.info(f"已设置 sessionStorage[{key}] = {value}")
        except Exception as e:
            logger.exception(f"设置 sessionStorage 失败: {e}")
            # 可选：重试一次
            self.page.wait_for_timeout(500)
            self.page.evaluate(f"() => sessionStorage.setItem('{key}', '{value}')")


    def get_cookie(self, name):
        """获取指定名称的 cookie 值，不存在返回 None"""
        self.page.wait_for_load_state('domcontentloaded')
        cookies = self.page.context.cookies()

        for cookie in cookies:
            if cookie['name'] == name:
                value = cookie['value']
                logger.info(f"获取到 cookie: {value}")
                if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                return value
        # 可选：打印所有 cookie 名称以便调试
        cookie_names = [c['name'] for c in cookies]
        logger.debug(f"当前 cookies: {cookie_names}")
        return None
    def set_cookie(self, name, value, domain='www.dogcatstar.com'):
        """设置cookie"""
        try:
            self.page.context.add_cookies([
                {
                    'name': name,
                    'value': value,
                    'domain': domain,
                    'path': '/'
                }
            ])
            return True
        except Exception as e:
            logger.exception(f"设置cookie: {e}")
            return False


    def preset_session(context, **kwargs):
        """页面注入session
        用法：
        def test_with_custom_preset(page):
            preset_session(page.context, has_user_confirmed_country_code='false')
            page.goto("https://www.dogcatstar.com/")"""

        script = "".join(f"sessionStorage.setItem('{k}', '{v}');" for k, v in kwargs.items())
        context.add_init_script(script)



    def set_local_storage(self, key: str, value: str) -> None:
        """
        设置 localStorage 的键值对（要求页面已加载并处于同源下）
        """
        try:
            # 确保页面已加载，避免在 about:blank 上操作
            self.page.wait_for_load_state('domcontentloaded')
            self.page.evaluate(f"() => localStorage.setItem('{key}', '{value}')")
            logger.info(f"已设置 localStorage[{key}] = {value}")
        except Exception as e:
            logger.exception(f"设置 localStorage 失败: {e}")

    def set_local_storage_batch(self, items: dict) -> None:
        """
        批量设置 localStorage 键值对
        :param items: 字典，如 {'key1': 'value1', 'key2': 'value2'}
        """
        script = "() => {\n"
        for key, value in items.items():
            script += f"  localStorage.setItem('{key}', '{value}');\n"
        script += "}"
        try:
            self.page.wait_for_load_state('domcontentloaded')
            self.page.evaluate(script)
            logger.info(f"已批量设置 localStorage: {items}")
        except Exception as e:
            logger.exception(f"批量设置 localStorage 失败: {e}")


    def get_all_cookies(self) -> list:
        """
        获取当前浏览器上下文中的所有 cookies。
        返回 cookies 列表，每个元素为字典，包含 name、value、domain 等信息。
        """
        try:
            self.page.wait_for_load_state('domcontentloaded')
            cookies = self.page.context.cookies()
            logger.info(f"获取到 {len(cookies)} 个 cookies")
            # 可选：精简返回，只保留 name 和 value
            # return [{'name': c['name'], 'value': c['value']} for c in cookies]
            return cookies
        except Exception as e:
            logger.exception(f"获取所有 cookies 失败: {e}")
            return []

    def get_all_local_storage(self) -> dict:
        """
        获取当前页面中的所有 localStorage 键值对。
        返回字典，键为 localStorage 的 key，值为对应的字符串 value。
        """
        try:
            # 确保页面已加载且具有合法源
            self.page.wait_for_load_state('domcontentloaded')
            if self.page.url == 'about:blank' or not self.page.url.startswith('http'):
                raise RuntimeError(f"Cannot access localStorage on page with URL: {self.page.url}")

            # 使用 JavaScript 获取所有 localStorage 项
            storage_dict = self.page.evaluate("""() => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }""")
            logger.info(f"获取到 {len(storage_dict)} 条 localStorage 数据")
            return storage_dict
        except Exception as e:
            logger.exception(f"获取所有 localStorage 失败: {e}")
            return {}



    def get_all_session_storage(self) -> Dict[str, str]:
        """
        获取当前页面中的所有 sessionStorage 键值对。
        返回字典，键为 sessionStorage 的 key，值为对应的字符串 value。
        """
        try:
            self.page.wait_for_load_state('domcontentloaded')
            if self.page.url == 'about:blank' or not self.page.url.startswith('http'):
                raise RuntimeError(f"Cannot access sessionStorage on page with URL: {self.page.url}")

            storage_dict = self.page.evaluate("""() => {
                const items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            }""")
            logger.info(f"获取到 {len(storage_dict)} 条 sessionStorage 数据")
            return storage_dict
        except Exception as e:
            logger.exception(f"获取所有 sessionStorage 失败: {e}")
            return {}


    def save_all_storage_to_files(self, test_name: str = "", directory: str = "storage",
                                  add_timestamp: bool = True) -> bool:
        """
        将 Cookies、localStorage 和 sessionStorage 保存到文件。
        :param test_name: 测试名称（可选，用于区分不同用例）
        :param directory: 存储目录
        :param add_timestamp: 是否在文件名中添加时间戳
        """
        try:
            os.makedirs(directory, exist_ok=True)

            # 生成时间戳（格式：YYYYMMDD_HHMMSS）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if add_timestamp else ""

            # 构建文件名后缀（包含测试名称和时间戳）
            suffix_parts = []
            if test_name:
                suffix_parts.append(test_name)
            if timestamp:
                suffix_parts.append(timestamp)
            suffix = "_" + "_".join(suffix_parts) if suffix_parts else ""

            # 获取数据
            cookies = self.get_all_cookies()
            local_storage = self.get_all_local_storage()
            session_storage = self.get_all_session_storage()

            # 保存 cookies
            cookies_path = os.path.join(directory, f"cookies{suffix}.json")
            with open(cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)

            # 保存 localStorage
            local_path = os.path.join(directory, f"local_storage{suffix}.json")
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(local_storage, f, ensure_ascii=False, indent=2)

            # 保存 sessionStorage
            # session_path = os.path.join(directory, f"session_storage{suffix}.json")
            # with open(session_path, 'w', encoding='utf-8') as f:
            #     json.dump(session_storage, f, ensure_ascii=False, indent=2)

            logger.info(f"存储数据已保存至目录: {directory}，后缀: {suffix}")
            return True
        except Exception as e:
            logger.exception(f"保存存储数据失败: {e}")
            return False





