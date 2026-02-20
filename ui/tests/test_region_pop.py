#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : test_region_pop.py
Time    : 2026/2/12 
Author  : xixi
File    : tests
#-------------------------------------------------------------
"""

import allure
import pytest
from pytest_check import check



@pytest.mark.region
@pytest.mark.smoke
@allure.feature("地区语言选择")  # Allure 特性标记
@allure.story("地区语言弹窗UI验证")  # Allure 用户故事标记
class TestMainRegion:

    @allure.title("检查弹窗内默认地区&语言，检查写入session和cookie")  # 自定义报告标题
    def test_default_region_language_check_session_and_cookie(self,setup_test,main_page,common_actions):
        # main_page = setup_test
        # 1、进入主页面，检查session storage是否已选择语言和地区,预期结果:session中没有key值：has_user_confirmed_country_code
        with allure.step("1.检查session storage是否已选择语言和地区,预期结果:session中没有key值：has_user_confirmed_country_code"):
            with check:
                session = common_actions.get_session_storage("has_user_confirmed_country_code")
                assert  not session,"session storage KEY:has_user_confirmed_country_code空"
        # 2、获取当前地区，检查语言和地区弹窗中的默认地区和语言
        with allure.step("2.检查弹窗中的语言和地区默认值"):
            with check:
                # 获取当前ip地区
                ip_countryCode = common_actions.get_region_by_ip()
                # 获取弹窗中的国家默认code

                default_countryCode = main_page.get_default_region()
                default_language = main_page.get_default_language()

                if ip_countryCode not in ["TW","HK","SG","MY"]:
                    # 当前Ip不在支持的范围内，地区默认是台湾，语言默认是英文
                    assert default_countryCode == 'TW', "地区不在支持范围内默认国家是台湾"
                    assert default_language == 'en_US', "地区不在支持范围内默认语言是英文"
                elif ip_countryCode =='TW':
                    # 当前ip是台湾，语言默认是繁中-tw
                    assert default_language == 'zh_TW' ,"地区是台湾，语言默认繁-台湾"
                elif ip_countryCode =='HK':
                    assert default_language == 'zh_HK',"地区是香港，语言默认繁-港澳"
                else:
                    # 其他情况默认语言是英文
                    assert default_language == 'en_US',"其他地区，语言默认英文"
        with allure.step("3.检查语言和地区下拉框可选,并确定"):
            with check:
                 assert main_page.select_region("HK"),"手动选择下拉框-香港"
                 assert main_page.select_language("en_US"),"手动选择下拉框-英文"
                 main_page.click_proceed_region()
        with allure.step("4.session storage中写入的key值has_user_confirmed_country_code"):
            with check:
                # 读取session storage
                country_code_value = None
                locale_value = None

                for i in range(10):
                    country_code_value = common_actions.get_session_storage("has_user_confirmed_country_code")
                    locale_value = common_actions.get_session_storage("has_user_confirmed_locale")

                    if country_code_value == 'true' and locale_value == 'true':
                        break
                assert country_code_value == "true", f"sessionStorage 写入失败，值为 {country_code_value}"
                assert locale_value == "true", f"sessionStorage 写入失败，值为 {locale_value}"

        with allure.step("5.cookie中写入的key值"):
            with check:
                cookie_value = None
                for i in range(10):
                    cookie_value = common_actions.get_cookie("user_selected_lang")
                    if cookie_value == "en_US":
                        break
                assert cookie_value == "en_US", f"cookie 写入失败，值为 {cookie_value}"

    @allure.title("写入session,不弹窗")  # 自定义报告标题
    @pytest.mark.parametrize('context', [
        {'has_user_confirmed_country_code': 'true', 'has_user_confirmed_locale': 'true'}
    ], indirect=True)
    def test_region_and_language_do_not_(self,context,base_page,main_page):
        with allure.step("1.写入session不再弹窗"):
            with check:
                # context 已按参数注入 sessionStorage
                base_page.navigate(url="https://www.dogcatstar.com/")
                assert not main_page.wait_for_region_language_modal()

    def test_region_cookie_(self,common_actions,base_page):
        with allure.step("验证cookie写入-无测试点"):
            with check:
                common_actions.set_cookie(name = "user_selected_lang",value = "en_US",domain="www.dogcatstar.com")
                cookie_value = None
                base_page.navigate(url="https://www.dogcatstar.com/")
                for i in range(10):
                    cookie_value = common_actions.get_cookie("user_selected_lang")
                    if cookie_value == "en_US":
                        break
                assert cookie_value == "en_US", f"cookie 写入成功，值为 {cookie_value}"








