#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : cart_sidebar_page.py
Time    : 2026/2/18 
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
# 加入购物车弹窗
import re
import time
from typing import List, Optional, Dict
from playwright.sync_api import Page
from ui.pages.base_page import BasePage
from utils.log import logger


class CartSidebarPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config["CART_SIDEBAR_PAGE"]

    # -------------------- 判断弹窗是否出现 --------------------

    def get_modal_content(self, as_html: bool = False) :
        """
        获取当前弹窗（购物车侧边栏）的内容。
        :param as_html: 如果为 True，返回整个弹窗的 HTML；否则返回纯文本。
        :return: 弹窗内容字符串，如果弹窗不存在或不可见则返回空字符串。
        """
        try:
            # 使用稳定的弹窗容器定位器
            modal = self.page.locator('[data-testid="dialog-paper"]')
            if modal.count() == 0 or not modal.first.is_visible():
                logger.warning("弹窗不存在或不可见")
                return ""

            if as_html:
                # 返回内部 HTML
                return modal.first.inner_html()
            else:
                # 返回所有文本
                return modal.first.text_content()
        except Exception as e:
            logger.exception(f"获取弹窗内容失败: {e}")
            return ""

    def analyze_modal_content(self, modal_text: str) -> dict:
        """
        分析弹窗文本，提取商品信息。
        :param modal_text: get_modal_content() 返回的文本
        :return: 包含提取信息的字典
        """
        import re

        result = {
            "product_name": None,
            "price": None,
            "points": None,
            "series": [],
            "specs": [],
            "flavors": [],
            "selected_series": None,
            "selected_spec": None,
            "selected_flavor": None,
        }

        if not modal_text:
            return result

        lines = modal_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        # 提取商品名称（通常在弹窗顶部）
        if lines:
            result["product_name"] = lines[0]

        # 提取价格（例如 "NT$48"）
        price_match = re.search(r'NT\$\s*(\d+)', modal_text)
        if price_match:
            result["price"] = int(price_match.group(1))

        # 提取积分（例如 "購買此商品可獲得 48 點"）
        points_match = re.search(r'獲得\s*(\d+)\s*點', modal_text)
        if points_match:
            result["points"] = int(points_match.group(1))

        # 提取系列选项
        # 假设系列选项前有 "選擇系列" 标题，后续行包含系列名称，直到遇到下一个标题或空白
        if "選擇系列" in modal_text:
            series_section = modal_text.split("選擇系列")[1].split("選擇規格")[0].split("選擇口味")[0]
            series_lines = series_section.split('\n')
            for line in series_lines:
                line = line.strip()
                if line and not any(x in line for x in ["選擇", "規格", "口味"]):
                    result["series"].append(line)

        # 提取规格选项
        if "選擇規格" in modal_text:
            spec_section = modal_text.split("選擇規格")[1].split("選擇口味")[0].split("選擇系列")[0]
            spec_lines = spec_section.split('\n')
            for line in spec_lines:
                line = line.strip()
                if line and not any(x in line for x in ["選擇", "系列", "口味"]):
                    result["specs"].append(line)

        # 提取口味选项
        if "選擇口味" in modal_text:
            flavor_section = modal_text.split("選擇口味")[1]
            # 可能后面还有 "已達庫存上限" 等，简单分割
            flavor_lines = flavor_section.split('\n')
            for line in flavor_lines:
                line = line.strip()
                if line and not any(x in line for x in ["選擇", "系列", "規格", "庫存"]):
                    result["flavors"].append(line)

        # 识别当前选中的选项（可以通过 data-testid="selected" 或样式判断）
        # 如果弹窗内选中项有特殊标记（如高亮），可能需要更复杂的逻辑
        # 这里简化处理，假设可以通过文本匹配

        return result

    def wait_for_cart_modal(self, timeout=10000):
        """等待购物车弹窗出现，并返回分析结果"""

        # # 等待购物车侧边栏出现（而非固定 sleep）
        # self.wait_for_cart_sidebar(timeout=5000)
        try:
            # 更精确的选择器（优先使用 data-testid）
            modal_indicators = [
                '[data-testid="dialog-paper"]',  # 弹窗容器
                'h6:has-text("選擇系列")',  # 系列标题
                'h6:has-text("選擇規格")',  # 规格标题
                'h6:has-text("選擇口味")',  # 口味标题
                # 'button:has-text("加入購物車")',  # 加入购物车按钮
                'text=購買此商品可獲得',  # 积分提示
            ]

            start_time = time.time()
            while (time.time() - start_time) * 1000 < timeout:
                for indicator in modal_indicators:
                    locator = self.page.locator(indicator).first
                    if locator.count() > 0 and locator.is_visible():
                        logger.info(f"检测到弹窗特征: {indicator}")
                        # 获取弹窗内容并分析
                        modal_content = self.get_modal_content()  # 假设您已有此方法
                        analysis = self.analyze_modal_content(modal_content)
                        return {
                            "detected_by": indicator,
                            "content": modal_content,
                            "analysis": analysis
                        }
                time.sleep(0.5)

            # 超时后的调试信息
            logger.warning("未检测到弹窗，当前页面信息:")
            logger.warning(f"URL: {self.page.url}")
            logger.warning(f"标题: {self.page.title()}")
            return None

        except Exception as e:
            logger.exception(f"等待弹窗时出错: {e}")
            return None
    # -------------------- 款式状态判断 --------------------

    def get_cart_sidebar_product_name(self) -> Optional[str]:
        """获取弹窗的商品名称"""
        if self.is_cart_sidebar_visible():
            return self.get_text(self.selectors["cart_sidebar_product_name"])
        return None
    # -------------------- 购物栏 --------------------
    def wait_for_cart_sidebar(self, timeout: int = 10000):
        """等待购物车弹窗出现"""
        self.wait_for_selector(self.selectors["cart_sidebar"], timeout=timeout)

    def is_cart_sidebar_visible(self) -> bool:
        """检查购物车弹窗是否可见"""
        return self.is_visible(self.selectors["cart_sidebar"])

    def is_all_styles_sold_out(self) -> bool:
        """检查是否所有款式都售罄"""
        styles = self.get_cart_sidebar_styles()

        if not styles:
            return False

        all_sold_out = all(style["is_sold_out"] for style in styles)

        if all_sold_out:
            # 验证显示补货通知按钮
            has_restock_button = self.is_visible(
                self.selectors["restock_notification_button"]
            )
            return has_restock_button

        return False

    def has_available_styles(self) -> bool:
        """检查是否有可用的款式"""
        styles = self.get_cart_sidebar_styles()

        if not styles:
            return False

        has_available = any(not style["is_sold_out"] for style in styles)

        if has_available:
            # 验证显示加入购物车按钮
            has_add_to_cart_button = self.is_visible(
                self.selectors["add_to_cart_sidebar_button"]
            )
            # 验证显示库存管理
            has_quantity_input = self.is_visible(
                self.selectors["quantity_input_cart"]
            )
            return has_add_to_cart_button and has_quantity_input

        return False

    def is_series_available(self, series_name: str) -> bool:
        """
        检查指定的系列是否可用（可见）
        :param series_name: 系列名称
        """
        try:
            selector = self.selectors['series_button_template'].replace('{series_name}', series_name)
            return self.is_visible(selector)
        except:
            return False

    def get_selected_series(self):
        """
        获取当前选中的系列名称（仅在系列区域内查找）
        """
        try:
            # 定位系列容器
            series_container = self.page.locator(self.selectors['series_container'])
            # 在容器内查找 data-testid="selected" 的按钮
            selected = series_container.locator('button[data-testid="selected"]').first
            if selected.count() > 0:
                name = selected.text_content()
                logger.info(f"当前选中系列: {name}")
                return name.strip() if name else None
            return None
        except Exception as e:
            logger.exception(f"获取当前选中系列失败: {e}")
            return None
    def select_series(self, series_name: str, timeout: int = 5000) -> bool:
        """
        选择指定的系列
        :param series_name: 系列名称，如 '滴雞精'
        :param timeout: 等待按钮可见的超时时间（毫秒）
        :return: 成功返回 True，失败返回 False
        """
        try:
            # 构建选择器，例如 button:has-text("滴雞精")
            selector = self.selectors['series_button_template'].replace('{series_name}', series_name)
            button = self.page.locator(selector)
            button.wait_for(state='visible', timeout=timeout)
            button.click()
            logger.info(f"成功选择系列: {series_name}")
            # 等待可能的价格或库存更新
            self.page.wait_for_timeout(300)
            return True
        except Exception as e:
            logger.exception(f"选择系列 '{series_name}' 失败: {e}")
            return False
    def get_available_series(self) -> list:
        """
        获取所有可用的系列名称列表
        :return: 系列名称列表，例如 ['綜合', '滴雞精', '滴魚精']
        """
        try:
            # 等待系列区域可见
            self.wait_for_selector(self.selectors['series_section_title'], timeout=5000)
            buttons = self.page.locator(self.selectors['series_buttons'])
            count = buttons.count()
            series_names = []
            for i in range(count):
                # 获取按钮内的文本（通常位于 <p> 标签内）
                text = buttons.nth(i).text_content()
                if text:
                    series_names.append(text.strip())
            logger.info(f"获取到可用系列: {series_names}")
            return series_names
        except Exception as e:
            logger.exception(f"获取系列列表失败: {e}")
            return []

    def click_cart_sidebar_favorite(self):
        """点击弹窗中的收藏按钮"""
        buttons = self.page.query_selector_all("button")
        for button in buttons:
            svg = button.query_selector("svg")
            if svg:
                path = svg.query_selector("path")
                if path:
                    d = path.get_attribute("d")
                    if d and "M9.03125 16.6562" in d:
                        button.click()
                        time.sleep(1)
                        # 检查是否弹出登录窗口
                        login_modal_visible = self.page.is_visible(
                            ".login-modal, [role='dialog']"
                        )
                        return {"clicked": True, "login_modal_shown": login_modal_visible}
        return {"clicked": False, "login_modal_shown": False}



    def click_cart_sidebar_restock_notification(self):
        """点击弹窗中的补货通知按钮"""
        if self.is_visible(self.selectors["restock_notification_button"]):
            self.click(self.selectors["restock_notification_button"])
            time.sleep(1)
            return True
        return False
    def wait_for_cart_update(self):
        """点击弹窗中的加入购物车按钮"""
        try:

            if self.is_visible(self.selectors["add_to_cart_sidebar_button"]):
                self.click(self.selectors["add_to_cart_sidebar_button"])
                # 等待操作完成
                time.sleep(2)
                return True

            else:
                logger.info(f"无法点击加入购物车按钮")

        except Exception as e:
            logger.exception(e)
            return False


    def decrease_cart_sidebar_quantity(self) -> bool:
        """在弹窗中减少数量"""
        if self.is_visible(self.selectors["decrease_button_cart"]):
            current_value = self.get_cart_sidebar_quantity()

            # 找到减少按钮
            decrease_buttons = self.page.query_selector_all("button")
            for button in decrease_buttons:
                svg = button.query_selector("svg")
                if svg:
                    path = svg.query_selector("path")
                    if path:
                        d = path.get_attribute("d")
                        if d and "M15.6875 9.75" in d:
                            button.click()
                            time.sleep(0.3)
                            new_value = self.get_cart_sidebar_quantity()
                            return new_value < current_value
        return False
    def increase_cart_sidebar_quantity(self) -> bool:
        """在弹窗中增加数量"""
        if self.is_visible(self.selectors["increase_button_cart"]):
            current_value = self.get_cart_sidebar_quantity()

            # 找到增加按钮
            increase_buttons = self.page.query_selector_all("button")
            for button in increase_buttons:
                svg = button.query_selector("svg")
                if svg:
                    path = svg.query_selector("path")
                    if path:
                        d = path.get_attribute("d")
                        if d and "M10.6562 4.71875" in d:
                            button.click()
                            time.sleep(0.3)
                            new_value = self.get_cart_sidebar_quantity()
                            logger.info(f"添加数量1次，目前值是: {new_value}")
                            return new_value > current_value
        return False
    def set_cart_sidebar_quantity(self, quantity: int) -> bool:
        """在弹窗中设置数量"""
        if self.is_visible(self.selectors["quantity_input_cart"]):
            # 清空输入框
            self.page.fill(self.selectors["quantity_input_cart"], "")
            logger.info(f"清空数量输入框")
            # 输入新值
            self.page.fill(self.selectors["quantity_input_cart"], str(quantity))
            logger.info(f"手动输入数量，目前值是: {quantity}")
            time.sleep(0.3)
            return True
        return False
    def get_cart_sidebar_max_stock(self) -> Optional[int]:
        """获取弹窗中的最大库存"""
        if self.is_visible(self.selectors["stock_max_attribute"]):
            max_value = self.page.get_attribute(
                self.selectors["stock_max_attribute"], "max"
            )
            return int(max_value) if max_value and max_value != "0" else None

        # 检查是否有库存上限消息
        if self.is_visible(self.selectors["stock_limit_message"]):
            message = self.get_text(self.selectors["stock_limit_message"])
            numbers = re.findall(r"\d+", message)
            if numbers:
                return int(numbers[0])

        return None


    def get_cart_sidebar_quantity(self) -> int:
        """获取弹窗的数量值"""
        if self.is_visible(self.selectors["quantity_input_cart"]):
            value = self.page.get_attribute(
                self.selectors["quantity_input_cart"], "value"
            )
            return int(value) if value else 1
        return 1
    def select_cart_sidebar_style(self, style_name: str) -> bool:
        """在弹窗中选择款式"""
        styles = self.get_cart_sidebar_styles()

        for style in styles:
            if style["name"] == style_name:
                # 构建选择器
                selector = self.selectors["style_button_template"].replace(
                    "{style_name}", style_name
                )
                if self.is_visible(selector):
                    self.click(selector)
                    time.sleep(0.5)
                    return True
        return False
    def get_cart_sidebar_styles(self) -> List[Dict]:
        """获取弹窗中的商品款式选项"""
        styles = []

        if self.is_cart_sidebar_visible():
            style_buttons = self.page.query_selector_all(
                self.selectors["style_buttons"]
            )

            for i, button in enumerate(style_buttons):
                try:
                    style_name = button.text_content()

                    # 检查是否已售完
                    sold_out = button.query_selector(
                        self.selectors["sold_out_badge_cart"]
                    )

                    styles.append(
                        {
                            "index": i,
                            "name": style_name.strip() if style_name else f"款式{i + 1}",
                            "is_sold_out": sold_out is not None,
                        }
                    )
                except:
                    continue

        return styles
    def is_spec_available(self, spec_name: str) -> bool:
        """
        检查指定的规格是否可用（可见）
        :param spec_name: 规格名称
        """
        try:
            selector = self.selectors['specs_button_template'].replace('{spec_name}', spec_name)
            return self.is_visible(selector)
        except:
            return False

    def get_selected_spec(self):
        #获取规格
        try:
            spec_container = self.page.locator(self.selectors['specs_container'])
            selected = spec_container.locator('button[data-testid="selected"]').first
            if selected.count() > 0:
                return selected.text_content().strip()
        except Exception as e:
            logger.exception(f"获取当前选中规格失败: {e}")
            return None

    def select_spec(self, spec_name: str, timeout: int = 5000) -> bool:
        """
        选择指定的规格（在规格容器内精确匹配文本）
        :param spec_name: 规格名称，如 '55g'
        :param timeout: 等待按钮可见的超时时间（毫秒）
        :return: 成功返回 True，失败返回 False
        """
        try:
            # 定位规格容器
            specs_container = self.page.locator(self.selectors['specs_container'])
            # 在容器内查找文本完全等于 spec_name 的按钮（使用 XPath 精确匹配）
            button = specs_container.locator(f'xpath=//button[normalize-space()="{spec_name}"]')
            button.wait_for(state='visible', timeout=timeout)
            button.click()
            logger.info(f"成功选择规格: {spec_name}")
            self.page.wait_for_timeout(300)
            return True
        except Exception as e:
            logger.exception(f"选择规格 '{spec_name}' 失败: {e}")
            return False

    def click_add_to_cart_and_wait(self, timeout: int = 15000, retries: int = 3):

        for attempt in range(retries):
            try:
                sidebar = self.page.locator(self.selectors['cart_sidebar_container']).first

                # 2. 在容器内查找加入购物车按钮
                add_btn = sidebar.locator(self.selectors['add_to_cart_button_text'])
                add_btn.wait_for(state='visible', timeout=5000)

                # 4. 点击按钮
                add_btn.click()
                time.sleep(10)
                logger.info(f"第 {attempt + 1} 次点击侧边栏加入购物车按钮")
                return True
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
                self.page.wait_for_timeout(2000)

        logger.error(f"经过 {retries} 次尝试，加入购物车仍未成功")
        return False

    def get_available_specs(self) -> list:
        """
        获取所有可用的规格名称列表
        :return: 规格名称列表，例如 ['單包40g', '40g*20包一盒']
        """
        try:
            # 等待规格区域可见
            self.wait_for_selector(self.selectors['specs_section_title'], timeout=5000)
            buttons = self.page.locator(self.selectors['specs_buttons'])
            count = buttons.count()
            specs = []
            for i in range(count):
                text = buttons.nth(i).text_content()
                if text:
                    specs.append(text.strip())
            logger.info(f"获取到可用规格: {specs}")
            return specs
        except Exception as e:
            logger.exception(f"获取规格列表失败: {e}")
            return []

    def get_available_flavors(self) -> list:
        """
        获取所有可用的口味名称列表
        :return: 口味名称列表，例如 ['鮮嫩雞肉', '鱸魚雞肉']
        """
        try:
            # 等待口味区域可见
            self.wait_for_selector(self.selectors['flavor_section_title'], timeout=5000)
            buttons = self.page.locator(self.selectors['flavor_buttons'])
            count = buttons.count()
            flavors = []
            for i in range(count):
                text = buttons.nth(i).text_content()
                if text:
                    flavors.append(text.strip())
            logger.info(f"获取到可用口味: {flavors}")
            return flavors
        except Exception as e:
            logger.exception(f"获取口味列表失败: {e}")
            return []

    def select_flavor(self, flavor_name: str, timeout: int = 5000) -> bool:
        """
        选择指定的口味
        :param flavor_name: 口味名称，如 '鱸魚雞肉'
        :param timeout: 等待按钮可见的超时时间（毫秒）
        :return: 成功返回 True，失败返回 False
        """
        try:
            # 构建选择器，例如 button:has-text("鱸魚雞肉")
            selector = self.selectors['flavor_button_template'].replace('{flavor_name}', flavor_name)
            button = self.page.locator(selector)
            button.wait_for(state='visible', timeout=timeout)
            button.click()
            logger.info(f"成功选择口味: {flavor_name}")
            # 等待可能的价格或库存更新
            self.page.wait_for_timeout(300)
            return True
        except Exception as e:
            logger.exception(f"选择口味 '{flavor_name}' 失败: {e}")
            return False

    def get_selected_flavor(self):
        try:
            flavor_container = self.page.locator(self.selectors['flavor_container'])
            selected = flavor_container.locator('button[data-testid="selected"]').first
            if selected.count() > 0:
                return selected.text_content().strip()
        except Exception as e:
            logger.exception(f"获取当前选中口味失败: {e}")
            return None

    def is_flavor_available(self, flavor_name: str) -> bool:
        """
        检查指定的口味是否可用（可见）
        :param flavor_name: 口味名称
        """
        try:
            selector = self.selectors['flavor_button_template'].replace('{flavor_name}', flavor_name)
            return self.is_visible(selector)
        except:
            return False

