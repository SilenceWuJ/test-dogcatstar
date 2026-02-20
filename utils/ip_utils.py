#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : ip_utils.py
Time    : 2026/2/10 
Author  : xixi
File    : 根据IP获取地区
#-------------------------------------------------------------
"""
import json
from typing import Optional, Dict, Any

# ip_utils.py
import requests


class IPInfoFetcher:
    """IP 信息获取工具类"""

    # IP 服务商列表，按优先级排序
    IP_SERVICES = [
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

    # IP 到地区代码的映射
    IP_TO_REGION = {
        # 台湾
        'TW': ['TW'],
        # 香港
        'HK': ['HK'],
        # 新加坡
        'SG': ['SG'],
        # 马来西亚
        'MY': ['MY'],
    }

    @classmethod
    def get_ip_info(cls, use_proxy: bool = False, proxies: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        获取当前 IP 的详细信息

        Args:
            use_proxy: 是否使用代理
            proxies: 代理配置，格式如 {'http': 'http://proxy:port', 'https': 'https://proxy:port'}

        Returns:
            包含 IP 信息的字典，如果失败返回 None
        """
        for service in cls.IP_SERVICES:
            try:
                print(f"尝试从 {service['name']} 获取 IP 信息...")

                response = requests.get(
                    service['url'],
                    timeout=service['timeout'],
                    proxies=proxies if use_proxy else None
                )

                if response.status_code == 200:
                    data = response.json()
                    ip_info = service['parser'](data)

                    print(f"成功从 {service['name']} 获取 IP 信息:")
                    print(f"  IP: {ip_info.get('ip')}")
                    print(f"  国家/地区: {ip_info.get('country_name', '未知')} ({ip_info.get('country_code', '未知')})")
                    print(f"  城市: {ip_info.get('city', '未知')}")
                    print(f"  地区: {ip_info.get('region', '未知')}")

                    return ip_info

            except Exception as e:
                print(f"从 {service['name']} 获取 IP 信息失败: {e}")
                continue

        print("所有 IP 服务都失败了")
        return None

    @classmethod
    def detect_region_from_ip(cls, use_proxy: bool = False, proxies: Optional[Dict] = None) -> Optional[str]:
        """
        根据 IP 检测地区代码

        Args:
            use_proxy: 是否使用代理
            proxies: 代理配置

        Returns:
            地区代码 (TW, HK, SG, MY) 或 None
        """
        ip_info = cls.get_ip_info(use_proxy, proxies)

        if not ip_info:
            return None

        country_code = ip_info.get('country_code', '').upper()

        # 映射到我们的地区代码
        for region_code, country_codes in cls.IP_TO_REGION.items():
            if country_code in country_codes:
                print(f"检测到地区: {region_code} (根据国家代码: {country_code})")
                return region_code

        print(f"无法识别的国家代码: {country_code}")
        return country_code

    @classmethod
    def get_region_with_fallback(cls, default_region: str = 'TW',
                                 use_proxy: bool = False,
                                 proxies: Optional[Dict] = None) -> str:
        """
        获取地区代码，如果失败则使用默认值

        Args:
            default_region: 默认地区代码
            use_proxy: 是否使用代理
            proxies: 代理配置

        Returns:
            地区代码
        """
        region = cls.detect_region_from_ip(use_proxy, proxies)
        return region if region else default_region

    @classmethod
    def get_supported_regions(cls) -> Dict[str, Dict]:
        """
        获取支持的地区配置

        Returns:
            地区配置字典
        """
        return {
            'TW': {
                'name': '台湾',
                'default_language': 'zh-TW',
                'currency': 'NT$',
                'timezone': 'Asia/Taipei',
                'ip_country_codes': ['TW']
            },
            'HK': {
                'name': '香港',
                'default_language': 'en_US',
                'currency': 'HK$',
                'timezone': 'Asia/Hong_Kong',
                'ip_country_codes': ['HK']
            },
            'SG': {
                'name': '新加坡',
                'default_language': 'en_US',
                'currency': 'S$',
                'timezone': 'Asia/Singapore',
                'ip_country_codes': ['SG']
            },
            'MY': {
                'name': '马来西亚',
                'default_language': 'en_US',
                'currency': 'RM',
                'timezone': 'Asia/Kuala_Lumpur',
                'ip_country_codes': ['MY']
            }
        }


# 快捷函数
def get_current_ip() -> Optional[str]:
    """获取当前 IP 地址"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json().get('ip')
    except Exception as e:
        print(f"获取当前 IP 失败: {e}")
        return None


def verify_proxy_working(proxy_url: str) -> bool:
    """验证代理是否工作"""
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        ip_before = get_current_ip()
        print(f"原始 IP: {ip_before}")

        ip_after = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=10
        ).json().get('ip')

        print(f"代理 IP: {ip_after}")

        return ip_before != ip_after
    except Exception as e:
        print(f"验证代理失败: {e}")
        return False


if __name__ == "__main__":
    # 示例 1: 获取当前 IP 信息
    print("=== 示例 1: 获取当前 IP 信息 ===")
    ip_info = IPInfoFetcher.get_ip_info()
    # print(f"ip_info:{ip_info}")
    if ip_info:
        print(f"IP 信息: {json.dumps(ip_info, indent=2, ensure_ascii=False)}")

    # 示例 2: 检测地区
    print("\n=== 示例 2: 检测地区 ===")
    region = IPInfoFetcher.detect_region_from_ip()
    if region:
        print(f"检测到的地区: {region}")
    else:
        print("无法检测地区")

    # 示例 3: 获取地区（带回退）
    print("\n=== 示例 3: 获取地区（带回退）===")
    region_with_fallback = IPInfoFetcher.get_region_with_fallback(default_region='TW')
    print(f"最终地区: {region_with_fallback}")
