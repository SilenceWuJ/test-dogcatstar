#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : test_after_cart_and_login.py
Time    : 2026/2/12 
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


@pytest.mark.cart_and_login
@pytest.mark.cart_scenario
@pytest.mark.ui
@allure.feature("会员登入且加入购物车用例")  # Allure 特性标记
@allure.story("会员登录且加入购物车")  # Allure 用户故事标记
class TestLoginAndCartEvent:
    """先加入购物车后登录"""
    @allure.title("先加入购物车后登录：老用户第三方登录（带购物车合并）")  # 自定义报告标题
    @pytest.mark.parametrize('context', [
        {
            'sessionStorage': {
                'has_user_confirmed_country_code': 'true',
                'has_user_confirmed_locale': 'true'
            },
            'localStorage': {
                'popup_states': {
                    "global": {"triggeredTimes": 1, "lastTriggered": "2026-02-20 8:00:35"},
                    "popup_179": {"triggeredTimes": 1, "suppressUntil": "2026-02-20 23:59:59",
                                  "lastTriggered": "2026-02-20 8:48:35"}
                }
            }
        }
    ], indirect=True)
    def test_account_narratological_google(self,context,main_page, login_page,common_actions, auto_close_popups, base_page, product_list_page, cart_sidebar_page,close_today_not_show,cart_page,test_name,my_page):


        # with allure.step("获取购物车数量"):
        #
        #     with check:
        #
        #         main_page.get_cart_bubble_count()
        #
        #         assert main_page.get_cart_bubble_count()

        with allure.step("1.跳转商品列表url：猫咪商品-猫咪主食"):

            base_page.navigate(url="https://www.dogcatstar.com/product-category/cat/cat_food/")

            base_page.close_known_popups()

        with allure.step("加购商品:【早餐罐｜汪喵星球迷你無膠早餐罐】，早餐罐/55g/鱸魚雞肉/数量3///商品列表页选择具体商品：「早餐罐」并点击加入购物车按钮"):
            # 使用部分名称匹配，即使标题有前缀/后缀也能工作
            assert product_list_page.add_to_cart_and_wait_for_modal("早餐罐"),  "加入购物车失败"

        with allure.step("选择系列"):

            # 等待购物车弹窗出现
            product_list_page.wait_for_cart_modal()

            series_list = cart_sidebar_page.get_available_series()
            assert len(series_list) >= 1, f"期望至少1个系列，实际 {series_list}"
            # 选择系列-
            cart_sidebar_page.select_series("營養罐")

            assert cart_sidebar_page.select_series("營養罐"), "选择系列失败"

        with allure.step("选择规格"):

            # 选择规格-
            cart_sidebar_page.select_spec("55g")
            # 检查是否选中规则
            cart_sidebar_page.get_selected_spec()
            # 获取所有可用规格
            specs = cart_sidebar_page.get_available_specs()
            assert len(specs) >= 1, f"期望至少1个规格，实际 {specs}"

            assert cart_sidebar_page.select_spec("55g"), "选择规格失败"
        with allure.step("选择口味"):
            # 1. 获取所有可用口味
            flavors = cart_sidebar_page.get_available_flavors()
            assert len(flavors) >= 1, f"期望至少2种口味，实际 {flavors}"
            # 2. 获取当前选中的口味（默认为 '鮮嫩雞肉'）
            cart_sidebar_page.get_selected_flavor()

            assert cart_sidebar_page.select_flavor("鱸魚雞肉"), "选择口味失败"
            # 3. 切换到 '鱸魚雞肉'
            # cart_sidebar_page.get_selected_flavor()
            # assert new_selected == "鱸魚雞肉", f"切换后应为 '鱸魚雞肉'，实际 {new_selected}"

        with allure.step("增加数量"):

            assert cart_sidebar_page.increase_cart_sidebar_quantity(),"+号增加数量失败"

        with allure.step("减少数量"):
            assert cart_sidebar_page.decrease_cart_sidebar_quantity(),"-号减少数量失败"

        with allure.step("手动输入数量，加入购物车--验证购物车数量"):

            add_cart_num =int(3)

            assert cart_sidebar_page.set_cart_sidebar_quantity(add_cart_num),"手动输入数量失败"

        with allure.step("加入购物车"):

            cart_sidebar_page.click_add_to_cart_and_wait()

        with allure.step("验证主页面购物车气泡数量"):

            with check:

                after_num = main_page.get_cart_bubble_count()

                assert after_num >0 ,f"当前购物车数量不是3"

        with allure.step("进入购物车页面"):

            cart_page.goto_cart()  # 需要先实现此方法
            base_page.close_known_popups()

        with allure.step("验证购物车内商品：数量、名称、规格"):

            with check:

                items = cart_page.get_cart_items()
                assert len(items) > 0, "购物车为空"
                for item in items:
                    if item['name'] == '汪喵星球 無膠純肉泥':
                        assert item['spec'] == '55g | 鱸魚雞肉 | 營養罐', f"选择的商品未加入购物车，购物车规格{item['spec']}"
                        assert item['quantity'] == 3, f"选择的商品未加入购物车，商品数量{item['quantity']}"

        with allure.step("获取storage"):
            with check:
                common_actions.save_all_storage_to_files(test_name=test_name)

        with allure.step("导航到用户登录页面"):
            with check:
                # login_page.navigate(url="https://www.dogcatstar.com/my-account/")
                login_page.goto_login_account()
        with allure.step("读取google账号用户名和密码"):

            google_name = login_page.user_account['GoogleAccount']
            google_password = login_page.user_account['GooglePassWord']

        with allure.step("google账号登录"):

            login_page.wait_for_login_modal()

            login_page.click_google_login_button()

            login_page.complete_google_login_embedded(google_name, google_password)

            # login_page.click_google_login_button()
            #
            # assert login_page.complete_google_login_embedded(google_name,google_password),f"登录失败"

        with allure.step("获取重定向页面"):

            url = base_page.get_current_url()

        with allure.step("进入购物车页面-验证未登录加购的：商品：数量、名称、规格登录后合并"):

            with check:


                cart_page.goto_cart()  # 需要先实现此方法

                base_page.close_known_popups()

                items = cart_page.get_cart_items()

                assert len(items) > 0, "购物车为空"

                for item in items:

                    if item['name'] == '汪喵星球 無膠純肉泥':

                        assert item['spec'] == '55g | 鱸魚雞肉 | 營養罐', f"选择的商品未加入购物车，购物车规格{item['spec']}"
                        assert item['quantity'] == 3, f"选择的商品未加入购物车，商品数量{item['quantity']}"

        with allure.step("获取storage-存储UID"):

            with check:

                common_actions.save_all_storage_to_files(test_name='login_'+test_name)
                googleAccount_user_id = common_actions.get_cookie("user_id")

        with allure.step("登出"):

            assert my_page.logout(),f"登出失败"

        with allure.step("登出后购物车空"):

            with check:

                cart_page.goto_cart()  # 需要先实现此方法

                base_page.close_known_popups()

                # items = cart_page.get_cart_items()

                assert cart_page.is_cart_empty(), "购物车没有置空"

        with allure.step("继续加购[加购商品：【早餐罐｜汪喵星球迷你無膠早餐罐】早餐罐/55g/鱸魚雞肉/数量2】【肉泥罐｜貓咪 益菌PRO+綿密肉泥主食罐：One-Time Purchase|直購（一次配送）/小罐80g/鮮甜虱目魚/数量6】]"):

            pass
        with allure.step("加购商品：【早餐罐｜汪喵星球迷你無膠早餐罐】營養罐/55g/鱸魚雞肉/数量2】"):



            base_page.navigate(url="https://www.dogcatstar.com/product-category/cat/cat_food/")

            base_page.close_known_popups()

            assert product_list_page.add_to_cart_and_wait_for_modal("早餐罐｜汪喵星球迷你無膠早餐罐"),  "加入购物车按钮点击失败"

            product_list_page.wait_for_cart_modal()

            # 选择系列-
            assert cart_sidebar_page.select_series("營養罐"),"选择系列失败"
            # 选择规格
            assert cart_sidebar_page.select_spec("55g"), "选择规格失败"
            # 选择口味
            assert cart_sidebar_page.select_flavor("鱸魚雞肉"), "选择口味失败"

            # 加号三次增加数量

            for i in range(0,3):
                cart_sidebar_page.increase_cart_sidebar_quantity(),"+号增加数量失败"

            cart_sidebar_page.click_add_to_cart_and_wait()

        with allure.step("加购商品：【肉泥罐｜貓咪 益菌PRO+綿密肉泥主食罐：One-Time Purchase|直購（一次配送）/小罐80g/鮮甜虱目魚/数量6】"):

            assert product_list_page.add_to_cart_and_wait_for_modal("肉泥罐｜貓咪 益菌PRO+綿密肉泥主食罐"),  "加入购物车按钮点击失败"

            product_list_page.wait_for_cart_modal()

            # 选择系列-
            assert cart_sidebar_page.select_series("直購（一次配送）"),"选择系列失败"
            # 选择规格
            assert cart_sidebar_page.select_spec("小罐80g"), "选择规格失败"
            # 选择口味
            assert cart_sidebar_page.select_flavor("鮮甜虱目魚"), "选择口味失败"

            # 加号三次增加数量

            for i in range(0,5):
                cart_sidebar_page.increase_cart_sidebar_quantity(),"+号增加数量失败"

            cart_sidebar_page.click_add_to_cart_and_wait()

        with allure.step("验证购物车气泡数量"):

            with check :

                assert main_page.get_cart_bubble_count()  > 12, f"当前购物车数量错误不是:12"


        with allure.step("校验购物车内商品：数量、名称、规格、价格（价格暂且不算币种）"):

            with check:

                cart_page.goto_cart()  # 需要先实现此方法
                base_page.close_known_popups()
                actual_items = cart_page.get_cart_items()
                # 3. 定义预期数据（可根据测试数据动态生成）
                # 暂时不算价格，根据汇率和美元折算
                expected_items = [
                    {
                        'name': '早餐罐｜汪喵星球迷你無膠早餐罐',
                        'spec': '55g | 鱸魚雞肉 | 營養罐',
                        'price': 234,
                        'quantity': 6
                    },
                    {
                        'name': '肉泥罐｜貓咪 益菌PRO+綿密肉泥主食罐',
                        'spec': '直購（一次配送） | 小罐80g｜鮮甜虱目魚 ',
                        'price': 288,
                        'quantity': 6
                    }
                ]

                # 4. 执行验证
                verify_cart_items(actual_items, expected_items)

        with allure.step("UID一致"):
            with check:

                common_actions.save_all_storage_to_files(test_name='login_'+test_name)
                googleAccount_user_id_2 = common_actions.get_cookie("user_id")
                assert googleAccount_user_id == googleAccount_user_id_2 ,"用户ID不一致"






















