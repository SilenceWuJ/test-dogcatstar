#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : product_detail_page.py
Time    : 2026/2/11
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import re
import time

from playwright.sync_api import Page

from ui.pages.base_page import BasePage


class ProductDetailPage(BasePage):
    """商品详情页操作类"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config["PRODUCT_DETAIL"]

    # -------------------- 页面加载与基本信息 --------------------
    def wait_for_product_detail_load(self):
        """等待商品详情页加载完成"""
        self.wait_for_selector(self.selectors["product_title"])
        self.wait_for_load_state()

    def get_product_title(self):
        """获取商品标题"""
        return self.get_text(self.selectors["product_title"])

    def get_product_price(self):
        """获取商品价格"""
        try:
            # 尝试获取折扣价
            if self.is_visible(self.selectors["discount_price"]):
                price = self.get_text(self.selectors["discount_price"])
            else:
                # 获取原价
                price = self.get_text(self.selectors["product_price"])
            return price.strip()
        except:
            # 备用方法：查找包含价格的元素
            price_elements = self.page.query_selector_all(
                '[class*="price"], [class*="Price"]'
            )
            for element in price_elements:
                text = element.text_content()
                if "$" in text or "NT$" in text:
                    return text.strip()
            return "价格未找到"

    def get_original_price(self):
        """获取原价（如果有折扣）"""
        if self.is_visible(self.selectors["original_price"]):
            return self.get_text(self.selectors["original_price"])
        return None

    def get_currency(self):
        """获取货币符号"""
        if self.is_visible(self.selectors["currency_symbol"]):
            return self.get_text(self.selectors["currency_symbol"])
        return "NT$"  # 默认新台币

    # -------------------- 款式选择 --------------------
    def get_style_options(self):
        """获取所有款式选项"""
        styles = []

        # 查找款式按钮
        style_buttons = self.page.query_selector_all(
            self.selectors["style_buttons"].split(", ")[0]
        )

        for i, button in enumerate(style_buttons):
            try:
                # 获取款式名称
                style_name = button.text_content()

                # 检查是否已售完
                sold_out = button.query_selector(self.selectors["sold_out_badge"])

                # 检查是否有补货按钮
                restock_btn = button.query_selector(self.selectors["restock_button"])

                styles.append(
                    {
                        "index": i,
                        "name": style_name.strip() if style_name else f"款式{i + 1}",
                        "is_sold_out": sold_out is not None,
                        "has_restock_button": restock_btn is not None,
                        "element": button,
                    }
                )
            except:
                continue

        return styles

    def select_style(self, style_name: str) -> bool:
        """选择指定款式"""
        # 构建选择器
        selector = self.selectors["style_button_template"].replace(
            "{style_name}", style_name
        )

        if self.is_visible(selector):
            self.click(selector)
            time.sleep(0.5)  # 等待款式切换
            return True
        return False

    def select_style_by_index(self, index: int) -> bool:
        """通过索引选择款式"""
        styles = self.get_style_options()
        if index < len(styles):
            styles[index]["element"].click()
            time.sleep(0.5)
            return True
        return False

    def get_selected_style(self):
        """获取当前选中的款式"""
        styles = self.get_style_options()
        for style in styles:
            # 检查按钮是否被选中（通过类名或其他属性）
            classes = style["element"].get_attribute("class") or ""
            if "selected" in classes or "active" in classes:
                return style
        return styles[0] if styles else None

    # -------------------- 库存与数量 --------------------
    def get_quantity_input_value(self) -> int:
        """获取库存输入框的值"""
        if self.is_visible(self.selectors["quantity_input"]):
            value = self.page.get_attribute(self.selectors["quantity_input"], "value")
            return int(value) if value else 1
        return 1

    def get_max_stock(self):
        """获取最大库存限制"""
        if self.is_visible(self.selectors["stock_limit"]):
            max_value = self.page.get_attribute(
                self.selectors["stock_limit"], "max"
            )
            return int(max_value) if max_value and max_value != "0" else None

        # 检查是否有库存上限消息
        if self.is_visible(self.selectors["max_stock_message"]):
            # 尝试从消息中解析数字
            message = self.get_text(self.selectors["max_stock_message"])
            numbers = re.findall(r"\d+", message)
            if numbers:
                return int(numbers[0])

        return None

    def set_quantity(self, quantity: int) -> bool:
        """手动设置库存数量"""
        if self.is_visible(self.selectors["quantity_input"]):
            # 清空输入框
            self.page.fill(self.selectors["quantity_input"], "")
            # 输入新值
            self.page.fill(self.selectors["quantity_input"], str(quantity))
            time.sleep(0.3)
            return True
        return False

    def increase_quantity(self) -> bool:
        """增加库存数量"""
        if self.is_visible(self.selectors["increase_quantity_button"]):
            current_value = self.get_quantity_input_value()
            self.click(self.selectors["increase_quantity_button"])
            time.sleep(0.3)
            new_value = self.get_quantity_input_value()
            return new_value > current_value
        return False

    def decrease_quantity(self) -> bool:
        """减少库存数量"""
        if self.is_visible(self.selectors["decrease_quantity_button"]):
            current_value = self.get_quantity_input_value()
            self.click(self.selectors["decrease_quantity_button"])
            time.sleep(0.3)
            new_value = self.get_quantity_input_value()
            return new_value < current_value
        return False

    # -------------------- 购物车操作 --------------------
    def click_add_to_cart(self) -> int:
        """点击加入购物车按钮，返回点击前的购物车数量"""
        # 等待按钮可点击
        self.wait_for_selector(self.selectors["add_to_cart_button"])

        # 获取点击前的购物车数量（如果有）
        cart_count_before = 0
        try:
            # 从主页面获取购物车数量
            cart_icon = self.page.query_selector('img[alt="Cart"]')
            if cart_icon:
                parent = cart_icon.query_selector("xpath=..")
                bubble = parent.query_selector(".cart-count, .badge, .bubble")
                if bubble:
                    cart_count_before = int(bubble.text_content())
        except:
            pass

        # 点击加入购物车
        self.click(self.selectors["add_to_cart_button"])

        # 等待加载提示出现
        try:
            self.page.wait_for_selector(
                self.selectors["loading_toast"], timeout=5000
            )
            time.sleep(1)  # 等待提示显示
        except:
            pass

        return cart_count_before

    def wait_for_cart_update(self, timeout: int = 10000):
        """等待购物车更新完成"""
        try:
            # 等待加载提示消失
            self.page.wait_for_selector(
                self.selectors["loading_toast"], state="hidden", timeout=timeout
            )
        except:
            pass

        # 等待一小段时间确保更新完成
        time.sleep(1)

    def get_cart_count_after_add(self) -> int:
        """获取添加后的购物车数量"""
        try:
            cart_icon = self.page.query_selector('img[alt="Cart"]')
            if cart_icon:
                parent = cart_icon.query_selector("xpath=..")
                bubble = parent.query_selector(".cart-count, .badge, .bubble")
                if bubble:
                    return int(bubble.text_content())
        except:
            pass
        return 0

    # -------------------- 收藏操作 --------------------
    def click_favorite(self) -> bool:
        """点击收藏按钮"""
        if self.is_visible(self.selectors["favorite_button"]):
            self.click(self.selectors["favorite_button"])
            time.sleep(0.5)
            return True
        return False

    def is_favorited(self) -> bool:
        """检查商品是否已收藏"""
        try:
            # 查找收藏按钮的父元素
            favorite_btn = self.page.query_selector(
                self.selectors["favorite_button"]
            )
            if favorite_btn:
                parent = favorite_btn.query_selector("xpath=..")
                classes = parent.get_attribute("class") or ""
                if "active" in classes or "selected" in classes:
                    return True
        except:
            pass
        return False

    # -------------------- 会员积分 --------------------
    def get_member_points_info(self) -> dict:
        """获取会员积分信息"""
        points_info = {}

        if self.is_visible(self.selectors["login_member_text"]):
            points_info["login_text"] = self.get_text(
                self.selectors["login_member_text"]
            )

        if self.is_visible(self.selectors["points_text"]):
            points_text = self.get_text(self.selectors["points_text"])
            points_info["points_text"] = points_text

            # 从文本中提取积分数量
            numbers = re.findall(r"\d+", points_text)
            if numbers:
                points_info["points"] = int(numbers[0])

        return points_info

    # -------------------- 图片与描述 --------------------
    def get_product_images(self) -> list:
        """获取商品图片列表"""
        images = []
        image_elements = self.page.query_selector_all(
            self.selectors["product_images"]
        )

        for element in image_elements:
            src = element.get_attribute("src")
            alt = element.get_attribute("alt")
            images.append({"src": src, "alt": alt})

        return images

    def click_product_image(self, index: int = 0) -> bool:
        """点击商品图片"""
        image_elements = self.page.query_selector_all(
            self.selectors["product_images"]
        )
        if index < len(image_elements):
            image_elements[index].click()
            time.sleep(1)
            return True
        return False

    def get_product_description(self):
        """获取商品描述"""
        if self.is_visible(self.selectors["product_description"]):
            return self.get_text(self.selectors["product_description"])
        return None

    def get_product_specs(self):
        """获取商品规格"""
        if self.is_visible(self.selectors["product_specs"]):
            return self.get_text(self.selectors["product_specs"])
        return None

    # -------------------- 页面滚动 --------------------
    def scroll_to_section(self, section: str) -> bool:
        """滚动到指定区域"""
        sections = {
            "title": self.selectors["product_title"],
            "price": self.selectors["product_price"],
            "styles": self.selectors["style_section_title"],
            "quantity": self.selectors["quantity_container"],
            "description": self.selectors["product_description"],
            "specs": self.selectors["product_specs"],
        }

        if section in sections:
            selector = sections[section]
            if self.is_visible(selector):
                self.page.evaluate(
                    f"""
                    () => {{
                        const element = document.querySelector('{selector}');
                        if (element) {{
                            element.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                        }}
                    }}
                """
                )
                time.sleep(1)
                return True

        return False

    # -------------------- 按钮状态 --------------------
    def is_add_to_cart_enabled(self) -> bool:
        """检查加入购物车按钮是否可用"""
        add_to_cart_btn = self.page.query_selector(
            self.selectors["add_to_cart_button"]
        )
        if add_to_cart_btn:
            disabled = add_to_cart_btn.get_attribute("disabled")
            return disabled is None or disabled == "false"
        return False

    # -------------------- 售罄与补货 --------------------
    def is_style_sold_out(self, style_name: str) -> bool:
        """检查指定款式是否售罄"""
        styles = self.get_style_options()
        for style in styles:
            if style["name"] == style_name:
                return style["is_sold_out"]
        return False

    def click_restock_notification(self, style_name: str) -> bool:
        """点击补货通知我按钮"""
        # 先选择该款式（如果未选择）
        self.select_style(style_name)

        # 查找补货通知按钮
        if self.is_visible(self.selectors["restock_button"]):
            self.click(self.selectors["restock_button"])
            time.sleep(1)
            return True
        return False

    # -------------------- 推荐商品 --------------------
    def get_recommended_products(self) -> list:
        """获取推荐商品"""
        products = []

        if self.is_visible(self.selectors["recommended_products"]):
            product_cards = self.page.query_selector_all(
                ".recommended-product, .product-card"
            )

            for card in product_cards:
                try:
                    name_element = card.query_selector(".product-name, .title")
                    name = name_element.text_content() if name_element else "未知"

                    price_element = card.query_selector(".product-price, .price")
                    price = price_element.text_content() if price_element else "未知"

                    products.append({"name": name.strip(), "price": price.strip()})
                except:
                    continue

        return products