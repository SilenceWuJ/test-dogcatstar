#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : test_login_and_cart.py
Time    : 2026/2/19 
Author  : xixi
File    : tests
#-------------------------------------------------------------
"""

import pytest
import allure
from pytest_check import check


def verify_cart_items(actual_items: list, expected_items: list):
    """
    验证购物车商品列表与预期是否一致。
    :param actual_items: get_cart_items() 返回的实际商品列表
    :param expected_items: 预期的商品列表，每个元素为包含 name, spec, price, quantity 的字典
    """
    assert len(actual_items) == len(expected_items), \
        f"商品数量不符：预期 {len(expected_items)}，实际 {len(actual_items)}"

    for i, (actual, expected) in enumerate(zip(actual_items, expected_items)):
        with allure.step(f"验证第 {i+1} 个商品"):
            with check:
                assert actual['name'] == expected['name'], \
                    f"商品{i+1}名称不符：预期 '{expected['name']}'，实际 '{actual['name']}'"
            with check:
                assert actual['spec'] == expected['spec'], \
                    f"商品{i+1}规格不符：预期 '{expected['spec']}'，实际 '{actual['spec']}'"
            with check:
                assert actual['price'] == expected['price'], \
                    f"商品{i+1}价格不符：预期 {expected['price']}，实际 {actual['price']}"
            with check:
                assert actual['quantity'] == expected['quantity'], \
                    f"商品{i+1}数量不符：预期 {expected['quantity']}，实际 {actual['quantity']}"


@pytest.mark.login_and_cart
@pytest.mark.cart_scenario
@pytest.mark.ui
@allure.feature("会员登入且加入购物车用例")  # Allure 特性标记
@allure.story("会员登录且加入购物车")  # Allure 用户故事标记
class TestLoginAndCartEvent:
    """先加入购物车后登录"""
    @allure.title("登录后加入购物车")  # 自定义报告标题
    @pytest.mark.parametrize('logged_in_page', [
        {
            'sessionStorage': {
                'has_user_confirmed_country_code': 'true',
                'has_user_confirmed_locale': 'true'
            },
            'localStorage': {
                'popup_states': {
                    "global": {"triggeredTimes": 1, "lastTriggered": "2026-02-20 8:48:35"},
                    "popup_179": {"triggeredTimes": 1, "suppressUntil": "2026-02-20 23:59:59",
                                  "lastTriggered": "2026-02-19 8:48:35"}
                }
            }
        }
    ], indirect=True)
    def test_account_narratological_google(self,logged_in_page,logined_cart_page,logined_base_page,logined_product_list_page,logined_cart_sidebar_page,logined_main_page,logined_close_today_not_show):


        with allure.step("导航到猫咪主食url"):



            logined_base_page.navigate(url="https://www.dogcatstar.com/product-category/cat/cat_food/")


        with allure.step("获取购物车气泡数量"):

            befor_num = logined_main_page.get_cart_bubble_count()

        with allure.step("选择早餐罐商品-加入购物车"):
            assert logined_product_list_page.add_to_cart_and_wait_for_modal("早餐罐"), "加入购物车失败"

        with allure.step("购物车弹窗"):

            assert logined_product_list_page.wait_for_cart_modal(),"购物车弹窗没有出现"

        with allure.step("选择系列\规格\口味\数量"):

            assert logined_cart_sidebar_page.select_series("營養罐"), "选择系列失败"
            assert logined_cart_sidebar_page.select_spec("55g"), "选择规格失败"
            assert logined_cart_sidebar_page.select_flavor("鱸魚雞肉"), "选择口味失败"

        with allure.step("调整数量=3（加号）"):

            for i in range(0,3):
                logined_cart_sidebar_page.increase_cart_sidebar_quantity()

        with allure.step("弹窗内-加入购物车"):

            logined_cart_sidebar_page.click_add_to_cart_and_wait()

        with allure.step("主页面购物车气泡数量"):

            with check:

                after_num = logined_main_page.get_cart_bubble_count()

                assert after_num == (befor_num+4) ,f"当前购物车数量未累加"

        with allure.step("进入购物车页面"):

            logined_cart_page.goto_cart()  # 需要先实现此方法
            logined_cart_page.close_known_popups()

        with allure.step("购物车页面：验证购物车内商品：数量、名称、规格"):

            with check:

                items = logined_cart_page.get_cart_items()
                assert len(items) > 0, "购物车为空"
                for item in items:
                    if item['name'] == '汪喵星球 無膠純肉泥':
                        assert item['spec'] == '單包（ 5 條） | 雞肉', f"加入购物车的商品规格不对，购物车规格{item['spec']}"
                        assert item['quantity'] > 0, f"加入购物车的商品数量不对，商品数量{item['quantity']}"


