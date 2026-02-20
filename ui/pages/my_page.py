#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : my_page.py
Time    : 2026/2/11
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import re
import time

from playwright.sync_api import Page

from ui.pages.base_page import BasePage
from utils.log import logger


class MyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config["MY_PAGE"]



    def wait_for_my_page_load(self):
        """等待我的页面加载完成"""
        self.wait_for_selector(self.selectors["favorites_container"])
        self.wait_for_load_state()

    def click_favorites_section(self):
        """点击收藏区域"""
        self.click(self.selectors["favorites_container"])

    def get_favorites_count(self):
        """获取收藏商品数量"""
        # 方法1：通过元素计数
        try:
            favorite_items = self.page.query_selector_all(
                self.selectors["favorite_items"]
            )
            return len(favorite_items)
        except:
            pass

        # 方法2：通过文本解析
        try:
            # 查找包含数量的元素，例如 "商品收藏(5)"
            favorites_text = self.get_text(self.selectors["favorites_text"])
            if "(" in favorites_text and ")" in favorites_text:
                match = re.search(r"\((\d+)\)", favorites_text)
                if match:
                    return int(match.group(1))
        except:
            pass

        return 0

    def get_favorite_products(self):
        """获取收藏商品列表"""
        products = []

        # 获取所有收藏商品卡片
        product_cards = self.page.query_selector_all(
            self.selectors["favorite_product_card"]
        )

        for card in product_cards:
            try:
                # 提取商品信息
                name_element = card.query_selector(".product-name")
                name = name_element.text_content() if name_element else "未知商品"

                price_element = card.query_selector(".product-price")
                price = price_element.text_content() if price_element else "未知价格"

                image_element = card.query_selector(".product-image img")
                image_url = (
                    image_element.get_attribute("src") if image_element else None
                )

                remove_element = card.query_selector(".remove-favorite")

                products.append(
                    {
                        "name": name.strip(),
                        "price": price.strip(),
                        "image_url": image_url,
                        "has_remove_button": remove_element is not None,
                    }
                )
            except:
                continue

        return products

    def remove_favorite(self, index=0):
        """移除收藏商品"""
        # 找到指定索引的商品
        product_cards = self.page.query_selector_all(
            self.selectors["favorite_product_card"]
        )
        if index < len(product_cards):
            remove_btn = product_cards[index].query_selector(".remove-favorite")
            if remove_btn:
                remove_btn.click()
                # 等待移除动画或确认
                time.sleep(1)
                return True
        return False

    def click_favorite_product(self, index=0):
        """点击收藏的商品"""
        product_cards = self.page.query_selector_all(
            self.selectors["favorite_product_card"]
        )
        if index < len(product_cards):
            product_cards[index].click()
            self.wait_for_load_state()
            return True

    def click_logout(self):
        """点击登出按钮"""
        self.click(self.selectors["logout_button"])

    def logout_and_confirm(self):
        """登出并确认"""
        self.click_logout()

        # 检查是否有确认弹窗
        if self.is_visible(self.selectors["logout_confirm_modal"]):
            self.click(self.selectors["logout_confirm_button"])
        else:
            # 直接登出
            time.sleep(1)

    def logout_and_cancel(self):
        """取消登出"""
        self.click_logout()

        # 检查是否有确认弹窗
        if self.is_visible(self.selectors["logout_confirm_modal"]):
            self.click(self.selectors["logout_cancel_button"])

    def get_user_info(self):
        """获取用户信息"""
        user_info = {}

        try:
            # 获取用户名
            if self.is_visible(self.selectors["user_name"]):
                user_info["name"] = self.get_text(self.selectors["user_name"])

            # 获取用户邮箱
            if self.is_visible(self.selectors["user_email"]):
                user_info["email"] = self.get_text(self.selectors["user_email"])

            # 获取账户信息
            if self.is_visible(self.selectors["account_info"]):
                info_text = self.get_text(self.selectors["account_info"])
                user_info["account_info"] = info_text
        except:
            pass

        return user_info

    def navigate_to_orders(self):
        """导航到订单历史"""
        if self.is_visible(self.selectors["orders_tab"]):
            self.click(self.selectors["orders_tab"])
        elif self.is_visible(self.selectors["order_history"]):
            self.click(self.selectors["order_history"])
        self.wait_for_load_state()

    def navigate_to_settings(self):
        """导航到账户设置"""
        if self.is_visible(self.selectors["settings_tab"]):
            self.click(self.selectors["settings_tab"])
        elif self.is_visible(self.selectors["account_settings"]):
            self.click(self.selectors["account_settings"])
        self.wait_for_load_state()

    def navigate_to_addresses(self):
        """导航到地址簿"""
        if self.is_visible(self.selectors["addresses_tab"]):
            self.click(self.selectors["addresses_tab"])
        elif self.is_visible(self.selectors["address_book"]):
            self.click(self.selectors["address_book"])
        self.wait_for_load_state()

    def navigate_to_payment_methods(self):
        """导航到支付方式"""
        if self.is_visible(self.selectors["payment_methods"]):
            self.click(self.selectors["payment_methods"])
        self.wait_for_load_state()

    def is_logged_in(self):
        """检查是否已登录"""
        try:
            # 检查是否存在登出按钮
            if self.is_visible(self.selectors["logout_button"]):
                return True

            # 检查是否存在用户信息
            user_info = self.get_user_info()
            if user_info.get("name") or user_info.get("email"):
                return True
        except:
            pass

        return False

    def scroll_my_page(self, direction="down"):
        """在我的页面滚动"""
        if direction == "down":
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        else:
            self.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

    def logout(self, timeout: int = 30000):
        """
        :param timeout: 超时时间（毫秒）
        """

        login_account_url = "https://www.dogcatstar.com/my-account/"

        self.navigate(login_account_url,timeout=timeout)

        # 可选：等待页面加载完成
        self.goto_logout()
        return True



    def goto_logout(self, timeout: int = 10000) -> bool:
        """
        点击“我的账户”页面的登出按钮。
        成功返回 True，失败返回 False。
        """
        try:
            # 定位包含文本“登出”的 h6 元素，然后取其父级（可点击的容器）
            # logout_btn = self.page.locator('h6:has-text("登出")').locator('xpath=..')
            logout_btn = self.page.locator(
                'h6:has-text("登出"), h6:has-text("Sign Out")'
            ).locator('xpath=..')
            logout_btn.wait_for(state='visible', timeout=timeout)
            logout_btn.click()
            logger.info("登出按钮点击成功")
            return True
        except Exception as e:
            logger.exception(f"登出按钮点击失败: {e}")
            return False


if __name__ == '__main__':

    from playwright.sync_api import sync_playwright

    # 启动 Playwright
    with sync_playwright() as p:
        # 启动浏览器（无头模式设为 False 可看到界面）
        browser = p.chromium.launch(
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
                '--enable-automation',  # 注意：通常会被检测，可能需要移除
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-infobars',
                '--disable-breakpad',
                '--disable-crash-reporter',
                '--disable-dev-shm-usage',
                '--disable-software-rasterizer',
            ]
        )
        # 创建新页面
        page = browser.new_page()

        from ui.pages.login_page import LoginPage
        from ui.pages.main_page import MainPage

        # 实例化 CartPage，传入 page
        login_page = LoginPage(page)
        main_page = MainPage(page)

        # 调用方法（需要先确保这些方法已定义）
        login_page.navigate(url="https://www.dogcatstar.com/my-account/")


        #
        login_page.wait_for_login_modal()



        # login_page.is_login_modal_visible()
        # login_page.get_login_title()
        user_name = 'wuf625555@gmail.com'
        password = 'www1337001893'

        # login_page.wait_for_login_modal()
        login_page.click_google_login_button()

        login_page.complete_google_login_embedded(user_name,password)

        # login_page.navigate(url="https://www.dogcatstar.com/my-account/")

        my_page = MyPage(page)

        my_page.logout()

        time.sleep(60)



        # 关闭浏览器
        browser.close()
