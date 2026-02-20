#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : product_list_page.py
Time    : 2026/2/11
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import re
import time
from typing import List, Optional, Dict
from playwright.sync_api import Page
from ui.pages.base_page import BasePage
from utils.log import logger


class ProductListPage(BasePage):
    """商品列表页操作类"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config["PRODUCT_LIST_PAGE"]

    # -------------------- 页面加载 --------------------
    def wait_for_product_list_load(self, timeout: int = 15000):
        """等待商品列表页加载完成"""
        self.wait_for_selector(self.selectors["product_list_container"], timeout=timeout)
        self.wait_for_load_state("networkidle")

    # -------------------- 商品信息获取 --------------------
    def get_product_count(self) -> int:
        """获取商品数量"""
        product_cards = self.selectors["product_card"]
        count = self.page.locator(product_cards).count()
        return count

    def get_product_info(self, index: int = 0) -> Optional[Dict]:
        """获取指定商品的详细信息"""
        product_cards = self.selectors["product_card"]
        cards = self.page.locator(product_cards).all()

        if index < len(cards):
            card = cards[index]

            try:
                # 获取商品名称
                title_element = card.locator(self.selectors["product_title"]).first
                title = title_element.text_content() if title_element else None

                # 获取商品链接
                link = title_element.get_attribute("href") if title_element else None

                # 获取商品价格
                price_element = card.locator(self.selectors["product_price"]).first
                price_text = price_element.text_content() if price_element else None

                # 获取原价和折扣价
                original_price_element = card.locator(
                    self.selectors["product_price_original"]
                ).first
                original_price = (
                    original_price_element.text_content()
                    if original_price_element
                    else None
                )

                sale_price_element = card.locator(
                    self.selectors["product_price_sale"]
                ).first
                sale_price = (
                    sale_price_element.text_content() if sale_price_element else None
                )

                # 获取商品图片
                image_element = card.locator(self.selectors["product_image"]).first
                image_src = (
                    image_element.get_attribute("src") if image_element else None
                )
                image_alt = (
                    image_element.get_attribute("alt") if image_element else None
                )

                # 获取加入购物车按钮状态
                add_to_cart_button = card.locator(
                    self.selectors["add_to_cart_button_list"]
                ).first
                has_add_to_cart_button = add_to_cart_button is not None

                return {
                    "index": index,
                    "title": title.strip() if title else None,
                    "link": link,
                    "price": price_text.strip() if price_text else None,
                    "original_price": original_price.strip() if original_price else None,
                    "sale_price": sale_price.strip() if sale_price else None,
                    "image_src": image_src,
                    "image_alt": image_alt,
                    "has_add_to_cart_button": has_add_to_cart_button,
                }
            except Exception as e:
                print(f"获取商品信息失败 (索引 {index}): {e}")
                return None

        return None

    def get_all_products_info(self, max_count: int = 20) -> List[Dict]:
        """获取所有商品信息"""
        products = []
        count = self.get_product_count()
        limit = min(count, max_count)

        for i in range(limit):
            product_info = self.get_product_info(i)
            if product_info:
                products.append(product_info)

        return products

    # -------------------- 商品导航 --------------------
    def click_product(self, index: int = 0):
        """点击商品（进入详情页）"""
        product_cards = self.selectors["product_card"]
        self.page.locator(product_cards).nth(index).click()
        self.wait_for_load_state()

    def click_product_image(self, index: int = 0):
        """点击商品图片（进入详情页）"""
        product_images = self.selectors["product_image"]
        self.page.locator(product_images).nth(index).click()
        self.wait_for_load_state()

    def click_product_title(self, index: int = 0):
        """点击商品标题（进入详情页）"""
        product_titles = self.selectors["product_title"]
        self.page.locator(product_titles).nth(index).click()
        self.wait_for_load_state()

    # -------------------- 列表页加入购物车 --------------------
    def click_add_to_cart_from_list(self, index: int = 0):
        """从列表页点击加入购物车按钮"""
        add_to_cart_buttons = self.selectors["add_to_cart_button_list"]
        self.page.locator(add_to_cart_buttons).nth(index).click()



    def close_cart_sidebar(self):
        """关闭购物车弹窗"""
        if self.is_visible(self.selectors["cart_sidebar_close"]):
            self.click(self.selectors["cart_sidebar_close"])
        elif self.is_visible(self.selectors["cart_sidebar_backdrop"]):
            # 点击背景关闭
            self.click(self.selectors["cart_sidebar_backdrop"])
        else:
            # 按 ESC 键关闭
            self.page.keyboard.press("Escape")

        time.sleep(1)



    # -------------------- 会员积分 --------------------
    def get_member_points_info_cart(self) -> Dict:
        """获取侧边栏中的会员积分信息"""
        points_info = {}

        if self.is_visible(self.selectors["member_login_text"]):
            points_info["login_text"] = self.get_text(
                self.selectors["member_login_text"]
            )

        if self.is_visible(self.selectors["member_points_text"]):
            points_text = self.get_text(self.selectors["member_points_text"])
            points_info["points_text"] = points_text

            # 从文本中提取积分数量
            numbers = re.findall(r"\d+", points_text)
            if numbers:
                points_info["points"] = int(numbers[0])

        return points_info

    # -------------------- 页面滚动 --------------------
    def scroll_product_list(self, direction: str = "down", pixels: int = 500):
        """滚动商品列表"""
        if direction == "down":
            self.page.evaluate(f"window.scrollBy(0, {pixels})")
        elif direction == "up":
            self.page.evaluate(f"window.scrollBy(0, -{pixels})")
        elif direction == "to_top":
            self.page.evaluate("window.scrollTo(0, 0)")
        elif direction == "to_bottom":
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        time.sleep(1)

    # -------------------- 分页与排序 --------------------
    def get_pagination_info(self) -> Dict:
        """获取分页信息"""
        pagination_info = {}

        if self.is_visible(self.selectors["pagination"]):
            pagination_info["exists"] = True

            # 获取当前页码
            if self.is_visible(self.selectors["current_page"]):
                current_page = self.get_text(self.selectors["current_page"])
                pagination_info["current_page"] = (
                    int(current_page) if current_page.isdigit() else current_page
                )

            # 检查上一页和下一页按钮
            pagination_info["has_prev"] = self.is_visible(self.selectors["prev_page"])
            pagination_info["has_next"] = self.is_visible(self.selectors["next_page"])

        return pagination_info

    def go_to_next_page(self) -> bool:
        """前往下一页"""
        if self.is_visible(self.selectors["next_page"]):
            self.click(self.selectors["next_page"])
            self.wait_for_product_list_load()
            return True
        return False

    def go_to_previous_page(self) -> bool:
        """前往上一页"""
        if self.is_visible(self.selectors["prev_page"]):
            self.click(self.selectors["prev_page"])
            self.wait_for_product_list_load()
            return True
        return False

    def sort_products(self, sort_option: str) -> bool:
        """排序商品"""
        if self.is_visible(self.selectors["sort_dropdown"]):
            self.page.select_option(self.selectors["sort_dropdown"], sort_option)
            self.wait_for_product_list_load()
            return True
        return False

    # -------------------- 面包屑导航 --------------------
    def get_breadcrumb_info(self) -> List[Dict]:
        """获取面包屑导航信息"""
        breadcrumbs = []

        if self.is_visible(self.selectors["breadcrumb"]):
            # 获取所有面包屑链接
            links = self.page.locator(f'{self.selectors["breadcrumb"]} a').all()

            for link in links:
                text = link.text_content()
                href = link.get_attribute("href")
                breadcrumbs.append({"text": text.strip(), "href": href})

        return breadcrumbs

    # -------------------- 筛选 --------------------
    def filter_by_category(self, category_name: str) -> bool:
        """按分类筛选"""
        category_elements = self.page.query_selector_all(
            self.selectors["category_filter"]
        )

        for element in category_elements:
            text = element.text_content()
            if category_name in text:
                element.click()
                self.wait_for_product_list_load()
                return True

        return False

    def filter_by_price_range(
        self, min_price: Optional[int] = None, max_price: Optional[int] = None
    ) -> bool:
        """按价格范围筛选"""
        if self.is_visible(self.selectors["price_filter"]):
            # 这里需要根据实际的价格筛选器实现
            # 可能是滑块或输入框
            pass
        return False





    # ---------- 基于索引的加购 ----------
    def add_to_cart_by_index(self, index: int = 0, timeout: int = 10000) -> bool:
        """
        根据商品卡片索引点击「加入购物车」按钮
        :param index: 商品卡片索引（从 0 开始）
        :param timeout: 等待元素可见的超时时间（毫秒）
        :return: 成功返回 True，失败返回 False
        """
        try:
            # 定位所有商品卡片
            product_cards = self.page.locator(self.selectors['product_card'])
            # 选取指定卡片
            target_card = product_cards.nth(index)
            # 等待卡片可见
            target_card.wait_for(state='visible', timeout=timeout)
            # 在卡片内定位加入购物车按钮
            add_btn = target_card.locator('.btn-quick-view')
            add_btn.wait_for(state='visible', timeout=timeout)
            add_btn.click()
            logger.info(f"已点击第 {index + 1} 个商品的「加入购物车」")
            return True
        except Exception as e:
            logger.exception(f"点击第 {index + 1} 个商品失败: {e}")
            return False

    # ---------- 批量加购（按索引列表）----------
    def add_products_to_cart_by_indices(self, indices: list[int]) -> list[bool]:
        """
        批量将指定索引的商品加入购物车
        :param indices: 索引列表，如 [0, 2, 5]
        :return: 每个操作是否成功的布尔值列表
        """
        results = []
        for idx in indices:
            results.append(self.add_to_cart_by_index(idx))
            # 可根据需要等待侧边栏关闭或短暂间隔
            self.page.wait_for_timeout(500)
        return results

    # ---------- 基于商品标题模糊匹配加购 ----------
    def add_to_cart_by_title(self, title_substring: str, timeout: int = 10000) -> bool:
        """
        根据商品标题包含的文本定位商品并点击加入购物车
        :param title_substring: 商品标题中包含的文本（如“迪士尼貓狗”）
        :return: 成功返回 True，失败返回 False
        """
        try:
            # 定位标题元素
            title_locator = self.page.locator(
                f'.product-title a:has-text("{title_substring}"), '
                f'.woocommerce-loop-product__link:has-text("{title_substring}")'
            )
            # 获取标题所在的商品卡片（标题的最近祖先 product-card）
            product_card = title_locator.locator('xpath=ancestor::li[contains(@class,"product")]')
            product_card.wait_for(state='visible', timeout=timeout)
            # 在卡片内点击加入购物车按钮
            add_btn = product_card.locator('.btn-quick-view')
            add_btn.wait_for(state='visible', timeout=timeout)
            add_btn.click()
            logger.info(f"已点击标题包含「{title_substring}」的商品的加入购物车")
            return True
        except Exception as e:
            logger.exception(f"按标题「{title_substring}」加购失败: {e}")
            return False

    def add_to_cart_by_prod_id(self, prod_id: str) -> bool:
        """根据商品 data-prod 属性点击加入购物车"""
        try:
            btn = self.page.locator(f'button.btn-quick-view[data-prod="{prod_id}"]')
            btn.wait_for(state='visible', timeout=10000)
            btn.click()
            return True
        except:
            return False


    def get_all_products(self) -> list:
        """
        获取页面中所有商品的列表
        返回商品元素列表，可用于后续操作
        """
        try:
            products = self.page.locator(self.selectors['product_cards']).all()
            logger.info(f"获取到 {len(products)} 个商品")
            return products
        except Exception as e:
            logger.exception(f"获取商品列表失败: {e}")
            return []

    def get_products_count(self) -> int:
        """
        获取页面中商品总数
        """
        try:
            count = self.page.locator(self.selectors['product_cards']).count()
            logger.info(f"商品总数: {count}")
            return count
        except Exception as e:
            logger.exception(f"获取商品数量失败: {e}")
            return 0

    def add_to_cart_by_index(self, index: int, timeout: int = 10000) -> bool:
        """
        根据索引将指定商品加入购物车
        :param index: 商品索引（从0开始）
        :param timeout: 超时时间（毫秒）
        """
        try:
            # 获取所有商品卡片
            products = self.page.locator(self.selectors['product_cards'])

            # 检查索引是否有效
            count = products.count()
            if index >= count:
                logger.error(f"索引 {index} 超出商品总数 {count}")
                return False

            # 定位指定商品
            target_product = products.nth(index)

            # 在商品卡片内定位加入购物车按钮
            add_btn = target_product.locator(self.selectors['product_card_add_to_cart'])

            # 等待按钮可见并点击
            add_btn.wait_for(state='visible', timeout=timeout)

            # 获取点击前的购物车数量
            cart_count_before = self._get_cart_count()

            # 点击加入购物车
            add_btn.click()
            logger.info(f"已将第 {index + 1} 个商品加入购物车")

            # 等待购物车侧边栏出现
            self.wait_for_cart_sidebar(timeout=timeout)

            return True

        except Exception as e:
            logger.exception(f"加入第 {index + 1} 个商品到购物车失败: {e}")
            return False

    def add_first_two_products_to_cart(self) -> bool:
        """
        将页面中前两个商品加入购物车
        成功返回 True，失败返回 False
        """
        try:
            # 获取商品数量
            count = self.get_products_count()
            if count < 2:
                logger.error(f"商品数量不足2个，当前只有 {count} 个")
                return False

            # 加入第一个商品
            logger.info("开始加入第1个商品...")
            if not self.add_to_cart_by_index(0):
                logger.error("第1个商品加入失败")
                return False

            # 关闭购物车侧边栏
            self.close_cart_sidebar()
            self.page.wait_for_timeout(500)  # 短暂等待

            # 加入第二个商品
            logger.info("开始加入第2个商品...")
            if not self.add_to_cart_by_index(1):
                logger.error("第2个商品加入失败")
                return False

            # 再次关闭侧边栏
            self.close_cart_sidebar()

            logger.info("成功将前两个商品加入购物车")
            return True

        except Exception as e:
            logger.exception(f"加入前两个商品失败: {e}")
            return False

    def add_products_by_indices(self, indices: list[int]) -> dict:
        """
        根据索引列表批量加入购物车
        :param indices: 索引列表，如 [0, 2, 5]
        :return: 每个商品的加入结果字典 {index: success}
        """
        results = {}

        for idx in indices:
            try:
                success = self.add_to_cart_by_index(idx)
                results[idx] = success

                if success:
                    self.close_cart_sidebar()
                    self.page.wait_for_timeout(500)

            except Exception as e:
                logger.exception(f"加入索引 {idx} 商品异常: {e}")
                results[idx] = False

        return results

    def _get_cart_count(self) -> int:
        """
        获取当前购物车数量（私有方法）
        """
        try:
            from ui.pages.main_page import MainPage
            main_page = MainPage(self.page)
            return main_page.get_cart_bubble_count()
        except:
            return 0

    def get_product_info_by_index(self, index: int) -> dict:
        """
        获取指定索引商品的详细信息
        :param index: 商品索引
        :return: 商品信息字典
        """
        try:
            products = self.page.locator(self.selectors['product_cards'])
            if index >= products.count():
                return {}

            product = products.nth(index)

            # 获取商品标题
            title_elem = product.locator(self.selectors['product_card_title']).first
            title = title_elem.text_content() or ""

            # 获取商品价格
            price_elem = product.locator(self.selectors['product_card_price']).first
            price = price_elem.text_content() or ""

            # 获取商品链接
            link_elem = product.locator(self.selectors['product_card_link']).first
            link = link_elem.get_attribute('href') or ""

            return {
                'index': index,
                'title': title.strip(),
                'price': price.strip(),
                'link': link,
                'has_add_button': product.locator(self.selectors['product_card_add_to_cart']).count() > 0
            }

        except Exception as e:
            logger.exception(f"获取商品信息失败 (索引 {index}): {e}")
            return {}

    # ---------- 基于商品名称的加购 ----------

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
        locator_s = self.page.locator('p:has-text("今日不再顯示")')
        if locator_s.count() > 0 and locator_s.first.is_visible():
            locator_s.first.click()
            self.page.wait_for_timeout(300)
        logger.info(f"关闭春节公告弹窗,{locator_s}")
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

    def add_to_cart_by_product_name(self, product_name: str, timeout: int = 10000) -> bool:

        locator_s = self.page.locator('p:has-text("今日不再顯示")')
        if locator_s.count() > 0 and locator_s.first.is_visible():
            locator_s.first.click()
            self.page.wait_for_timeout(300)
        logger.info(f"关闭春节公告弹窗,{locator_s}")
        try:
            # 定位商品卡片（使用之前稳定的 XPath）
            self.close_known_popups()
            xpath = (
                f'//a[contains(@class, "woocommerce-LoopProduct-link") and '
                f'(contains(@aria-label, "{product_name}") or contains(text(), "{product_name}"))]'
                f'/ancestor::div[contains(@class, "product-small")][1]'
            )
            card = self.page.locator(f'xpath={xpath}').first
            card.wait_for(state='visible', timeout=timeout)
            # 悬停卡片
            card.hover()



            # 等待“加入购物车”按钮出现
            add_btn = card.locator('button:has-text("ADD TO CART"), button:has-text("加入購物車")')
            add_btn.wait_for(state='visible', timeout=timeout)
            print(f"按钮可见: {add_btn.is_visible()}")
            print(f"按钮启用: {add_btn.is_enabled()}")
            print(f"按钮disabled属性: {add_btn.get_attribute('disabled')}")
            print(f"按钮HTML: {add_btn.first.inner_html()}")
            add_btn.click()
            self.page.wait_for_timeout(1000)  # 等待1秒，观察变化
            # 截图保存现场
            # self.page.screenshot(path="debug_after_click.png")
            # 打印所有可能的弹窗元素
            dialogs = self.page.locator(
                '[role="dialog"], .modal, [data-testid="dialog-paper"], .quick-view-wrapper').all()
            print(f"点击后，页面上找到 {len(dialogs)} 个可能的弹窗元素")
            for d in dialogs:
                print(f"  弹窗可见: {d.is_visible()}, 内容: {d.text_content()}")


            logger.info(f"成功点击商品「{product_name}」的加入购物车按钮")
            return True
        except Exception as e:
            logger.exception(f"点击商品「{product_name}」失败: {e}")
            return False

    def add_to_cart_by_product_name_partial(self, name_part: str, timeout: int = 10000) -> bool:
        """
        根据商品名称的部分文本匹配并加入购物车（更宽松的匹配）。
        例如，传入 "早餐罐" 可以匹配标题包含 "早餐罐｜汪喵星球迷你無膠早餐罐" 的商品。
        增强版：增加了对商品列表容器的等待，并检查匹配元素数量。
        """
        try:
            # 1. 等待商品列表容器出现（确保页面已加载）
            self.wait_for_selector(self.selectors['product_list_container'], timeout=timeout)

            # 2. 构建 XPath 定位器
            xpath = f'//a[contains(@class, "woocommerce-LoopProduct-link") and contains(text(), "{name_part}")]' \
                    f'/ancestor::div[contains(@class, "product-small")][1]'
            product_card_locator = self.page.locator(f'xpath={xpath}')

            # 3. 检查匹配的元素数量，如果为0则提前失败并记录调试信息
            count = product_card_locator.count()
            if count == 0:
                # 输出当前页面的部分 HTML 以便调试
                page_html = self.page.content()[:2000]  # 取前2000字符
                logger.error(f"未找到包含文本「{name_part}」的商品。当前页面 HTML 片段: {page_html}")
                return False

            logger.info(f"找到 {count} 个匹配的商品，将点击第一个")

            # 4. 等待第一个元素可见并点击
            first_card = product_card_locator.first
            first_card.wait_for(state='visible', timeout=timeout)

            # 5. 在卡片内定位加入购物车按钮
            add_button_locator = first_card.locator('button.btn-quick-view')
            add_button_locator.wait_for(state='visible', timeout=timeout)
            add_button_locator.click()

            logger.info(f"成功点击名称包含「{name_part}」的商品的加入购物车按钮")
            return True

        except Exception as e:
            logger.exception(f"根据名称部分「{name_part}」加入购物车失败: {e}")
            return False
    def add_to_cart_by_product_name_exact(self, exact_name: str, timeout: int = 10000) -> bool:
        """
        根据**精确**的商品名称进行匹配并加入购物车（更严格）。
        例如，传入 "早餐罐｜汪喵星球迷你無膠早餐罐" 进行完全匹配。
        """
        try:
            # 使用精确文本匹配
            product_card_locator = self.page.locator(
                f'xpath=//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link" and text()="{exact_name}"]'
                f'/ancestor::div[contains(@class, "product-small")][1]'
            )
            product_card_locator.first.wait_for(state='visible', timeout=timeout)
            add_button_locator = product_card_locator.first.locator('button.btn-quick-view')
            add_button_locator.wait_for(state='visible', timeout=timeout)
            add_button_locator.click()
            logger.info(f"成功点击精确名称「{exact_name}」的加入购物车按钮")
            return True
        except Exception as e:
            logger.exception(f"根据精确名称「{exact_name}」加入购物车失败: {e}")
            return False

    def add_to_cart_and_wait_for_modal(self, product_name: str, max_retries: int = 3,
                                       wait_timeout: int = 10000) -> bool:
        """
        点击指定商品的“加入购物车”按钮，并等待购物车弹窗出现。
        支持重试：如果弹窗未出现，会重新尝试点击（最多 max_retries 次）。
        """
        for attempt in range(max_retries):
            try:
                # 1. 定位商品卡片（每次重试时重新定位，避免元素失效）
                xpath = (
                    f'//a[contains(@class, "woocommerce-LoopProduct-link") and '
                    f'(contains(@aria-label, "{product_name}") or contains(text(), "{product_name}"))]'
                    f'/ancestor::div[contains(@class, "product-small")][1]'
                )
                card = self.page.locator(f'xpath={xpath}').first
                card.wait_for(state='visible', timeout=5000)

                # 2. 悬停并等待加入购物车按钮
                card.hover()
                add_btn = card.locator('button:has-text("ADD TO CART"), button:has-text("加入購物車")')
                add_btn.wait_for(state='visible', timeout=5000)

                # 3. 点击按钮
                add_btn.click()
                logger.info(f"第 {attempt + 1} 次点击商品「{product_name}」的加入购物车按钮")

                # 4. 等待弹窗出现（使用您的 wait_for_cart_modal 方法）
                modal_info = self.wait_for_cart_modal(timeout=wait_timeout)
                if modal_info:
                    logger.info(f"第 {attempt + 1} 次成功检测到购物车弹窗")
                    return True
                else:
                    logger.warning(f"第 {attempt + 1} 次点击后未检测到弹窗，准备重试...")
                    # 等待短暂时间后重试，让页面有时间响应
                    self.page.wait_for_timeout(1000)

            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试时发生异常: {e}")
                self.page.wait_for_timeout(1000)

        logger.error(f"经过 {max_retries} 次尝试后，仍未出现购物车弹窗")
        return False