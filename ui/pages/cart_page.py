#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : cart_page.py
Time    : 2026/2/11 
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
from playwright.sync_api import Page

from ui.pages.base_page import BasePage
from utils.log import logger
import re
from ui.pages.login_page import LoginPage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config['CART_PAGE']
        self.user_account = {
            'username': self.param.get('USER', 'GoogleAccount'),
            'password': self.param.get('USER', 'GooglePassWord'),
        }

    def goto_cart(self, timeout: int = 30000):
        """
        导航到购物车页面
        :param timeout: 超时时间（毫秒）
        """
        cart_url = "https://www.dogcatstar.com/cart"
        self.navigate(cart_url,timeout=timeout)
        # 可选：等待页面加载完成，例如等待购物车容器出现
        # self.page.wait_for_selector(self.selectors['cart_items'], timeout=10000)
        logger.info("已进入购物车页面")




    def get_cart_items(self) -> list:
        """
        获取购物车中所有商品的详细信息，返回字典列表。
        每个字典包含商品名称、规格、单价、数量、小计、链接等。
        """
        items = []
        try:
            # 等待至少一个商品容器出现
            self.page.wait_for_selector(self.selectors['cart_items'], timeout=10000)
            # 获取所有商品容器
            containers = self.page.locator(self.selectors['cart_items']).all()
            logger.info(f"找到 {len(containers)} 个商品容器")

            for idx, container in enumerate(containers):
                item = {}

                # 1. 商品名称（在 h6 内）
                name_el = container.locator(self.selectors['item_name']).first
                item['name'] = name_el.text_content().strip() if name_el.count() > 0 else ""

                # 2. 商品规格
                spec_el = container.locator(self.selectors['item_spec']).first
                item['spec'] = spec_el.text_content().strip() if spec_el.count() > 0 else ""

                # 3. 商品单价（提取数字）
                price_el = container.locator(self.selectors['item_price']).first
                price_text = price_el.text_content() if price_el.count() > 0 else "0"
                price_match = re.search(r'\d+', price_text)
                item['price'] = int(price_match.group()) if price_match else 0

                # 4. 商品数量
                qty_el = container.locator(self.selectors['item_quantity']).first
                qty_value = qty_el.get_attribute('value') if qty_el.count() > 0 else "1"
                item['quantity'] = int(qty_value) if qty_value.isdigit() else 1

                # 5. 小计
                item['subtotal'] = item['price'] * item['quantity']

                # 6. 商品链接（第一个包含 /product/ 的 a 标签）
                link_el = container.locator('a[href*="/product/"]').first
                item['link'] = link_el.get_attribute('href') if link_el.count() > 0 else ""

                # 7. 是否有删除按钮
                remove_el = container.locator(self.selectors['item_remove_button']).first
                item['has_remove_button'] = remove_el.count() > 0

                items.append(item)

            logger.info(f"成功获取 {len(items)} 个商品的详细信息")
            logger.info(f"cart_items: {items}")
            return items

        except Exception as e:
            logger.exception(f"获取购物车商品信息失败: {e}")
            return []



    def get_total_amount(self):
        """获取总金额"""
        return self.get_text(self.selectors['total_amount'])

    def get_cart_item_count(self) -> int:
        """
        获取购物车中商品项的数量（复用已有的商品列表逻辑）
        """
        try:
            # 等待商品容器出现
            self.page.wait_for_selector(self.selectors['cart_items'], timeout=10000)
            # 定位所有商品容器
            items = self.page.locator(self.selectors['cart_items']).all()
            logger.info(f"购物车内商品：: {items}")
            count = len(items)
            logger.info(f"购物车商品数量: {count}")
            return count
        except Exception as e:
            logger.warning(f"获取购物车商品数量失败，购物车可能为空: {e}")
            return 0
    def click_promotion_banner(self, timeout: int = 10000) -> bool:
        """
        点击购物车页面的促销横幅（新会员登录入口）
        成功返回 True，失败返回 False
        """
        try:
            # 定位包含促销文本的链接（根据实际结构调整）
            banner = self.page.locator('a:has-text("新會員登入")')
            # 如果上面定位不到，可尝试更精确的：
            # banner = self.page.locator('a:has(strong:has-text("新會員登入"))')

            banner.wait_for(state='visible', timeout=timeout)
            banner.click()
            logger.info("点击促销横幅成功")
            return True
        except Exception as e:
            logger.exception(f"点击促销横幅失败: {e}")
            return False

    def login_via_promotion(self, email: str, password: str) -> bool:
        """通过促销横幅发起登录，并完成 Google 登录流程"""
        if not self.click_promotion_banner():
            return False
        # 等待登录弹窗
        user_name = self.user_account['username']
        password = self.user_account['password']
        login_page = LoginPage(self.page)
        login_page.wait_for_login_modal()
        login_page.click_google_login()
        login_page.handle_google_login_popup(user_name,password)
        login_page.handle_google_login_popup(user_name,password)
        return login_page.complete_google_login(user_name,password)

    def is_cart_empty(self, timeout: int = 5000) -> bool:
        """
        判断购物车是否为空。
        通过等待页面中出现“購物車中沒有商品”的提示元素来实现。
        :param timeout: 等待元素出现的超时时间（毫秒）
        :return: 空车返回 True，否则返回 False
        """
        try:
            empty_locator = self.page.locator(self.selectors['cart_empty_indicator'])
            empty_locator.wait_for(state='visible', timeout=timeout)
            logger.info("购物车为空")
            return True
        except Exception as e:
            logger.info("购物车不为空或元素未出现")
            return False


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright

    # 启动 Playwright
    with sync_playwright() as p:
        # 启动浏览器（无头模式设为 False 可看到界面）
        browser = p.chromium.launch(headless=False)
        # 创建新页面
        page = browser.new_page()

        # 实例化 CartPage，传入 page
        cart_page = CartPage(page)

        # 调用方法（需要先确保这些方法已定义）
        cart_page.goto_cart()  # 导航到购物车
        count = cart_page.get_cart_item_count()  # 获取商品数量
        print(f"购物车商品数量: {count}")

        # 关闭浏览器
        browser.close()

