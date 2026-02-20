#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : main_page.py
Time    : 2026/2/11 
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""
import time
import re

from playwright.sync_api import Page

from utils.log import logger
from ui.pages.base_page import BasePage


class MainPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config['MAIN_PAGE']
        self.region_selectors = self.config['REGION_MODAL']
        self.login_selectors = self.config['LOGIN_MODAL']


    def wait_for_region_language_modal(self, timeout=10000):
        """等待地区语言选择弹窗出现"""
        try:
            print(f"等待地区语言选择弹窗（超时: {timeout / 1000}秒）...")

            # 定义可能出现的弹窗特征 - 更精确的选择器
            modal_indicators = [
                # 英文标题
                "h5:has-text('Switching Website and Language Settings')",
                # 繁体中文标题
                "h5:has-text('切換網站及語系')",
                # 备用文本选择器
                "text=國家 / 地區",
                "text=Country / Region",
            ]

            # 等待任何一个特征出现
            start_time = time.time()
            while (time.time() - start_time) * 1000 < timeout:
                for indicator in modal_indicators:
                    try:
                        # 尝试定位元素
                        element = self.page.locator(indicator).first

                        # 检查元素是否存在且可见
                        if element.count() > 0:
                            # 检查元素是否可见
                            if element.is_visible():
                                print(f"检测到弹窗特征: {indicator}")

                                # 获取元素文本内容
                                try:
                                    text_content = element.text_content()
                                    print(f"弹窗标题: {text_content}")
                                except:
                                    pass

                                # 获取弹窗内容
                                modal_content = self.get_modal_content()

                                # 分析弹窗内容
                                modal_analysis = self.analyze_modal_content(modal_content)

                                return {
                                    "detected_by": indicator,
                                    "title": text_content if 'text_content' in locals() else "未知",
                                    "content": modal_content,
                                    "analysis": modal_analysis
                                }
                            return True
                    except Exception as e:
                        # 调试信息
                        logger.debug("主页面地区语言弹窗获取失败:%s", e)
                        continue

                # 短时间等待后重试
                time.sleep(0.5)

            # 如果超时，尝试截图或获取页面状态
            print("等待地区语言弹窗超时")

            # 获取当前页面状态用于调试
            try:
                page_title = self.page.title()
                page_url = self.page.url
                print(f"当前页面标题: {page_title}")
                print(f"当前页面URL: {page_url}")

                # 检查页面是否有其他可能相关的元素
                all_h5_elements = self.page.locator("h5").all()
                if all_h5_elements:
                    print("页面中所有h5元素:")
                    for idx, h5 in enumerate(all_h5_elements[:5]):  # 只显示前5个
                        try:
                            h5_text = h5.text_content()
                            print(f"  h5[{idx}]: {h5_text}")
                        except:
                            pass
            except Exception as debug_e:
                print(f"调试时出错: {debug_e}")

            return None
        except Exception as e:
            print(f"等待弹窗时发生错误: {e}")
            return None

    def check_region_modal(self):
        """获取检查弹窗默认语言"""
        try:
            title_en = self.region_selectors['title_en'].split(', ')[0]
            title_tw = self.region_selectors['title_tw'].split(', ')[0]

            # 检查英文标题
            try:
                self.page.wait_for_selector(title_en, timeout=5000)
                logger.info("语言弹窗内默认语言:%s", title_en)
                return True
            except:
                # 检查繁体标题
                try:
                    self.page.wait_for_selector(title_tw, timeout=5000)
                    logger.info("语言弹窗内默认语言：%s", title_tw)
                    return True
                except:
                    logger.debug("语言弹窗获取异常1")
                    return False
        except Exception as e:
            logger.info("获取检查弹窗默认语言异常: %s", e)
            return False

    def get_default_region(self):
        """获取默认地区（直接读取 select 的当前值）"""
        try:
            # 方式1：使用 Playwright 的 input_value() 方法
            select_locator = 'select[data-testid="select-change-country"]'
            selected = self.page.locator(select_locator).input_value()
            logger.info("获取默认地区: %s", selected)
            return selected
        except Exception as e:
            logger.exception("获取弹窗默认地区异常: %s", e)
            return None  # 失败返回 None，避免与字符串混淆

    def get_default_language(self):
        """获取默认语言（直接读取 select 的当前值）"""
        try:
            select_locator = 'select[data-testid="select-change-locale"]'
            selected = self.page.locator(select_locator).input_value()
            logger.info("获取默认语言: %s", selected)
            return selected
        except Exception as e:
            logger.exception("获取弹窗默认语言异常: %s", e)
            return None

    def select_region(self, region_code):
        """选择地区，成功返回 True，失败返回 False"""
        try:
            select_locator = 'select[data-testid="select-change-country"]'
            self.page.select_option(select_locator, value=region_code)
            logger.info("选择地区成功: %s", region_code)
            return True
        except Exception as e:
            logger.exception("弹窗内选择地区失败: %s", e)
            return False

    def select_language(self, language_code):
        """选择语言，成功返回 True，失败返回 False"""
        try:
            select_locator = 'select[data-testid="select-change-locale"]'
            self.page.select_option(select_locator, value=language_code)
            logger.info("选择语言成功: %s", language_code)
            return True
        except Exception as e:
            logger.exception("弹窗内选择语言失败: %s", e)
            return False


    def close_region_modal(self):
        """关闭地区选择弹窗"""
        close_btn = self.region_selectors['close_button']
        if self.is_visible(close_btn):
            self.click(close_btn)

    def click_cancel_region(self):
        """点击取消按钮"""
        cancel_selectors = self.region_selectors['cancel_button'].split(', ')
        for selector in cancel_selectors:
            if self.is_visible(selector):
                self.click(selector)
                break

    def click_proceed_region(self):
        """
        点击确定前往按钮，等待弹窗消失，返回 True/False
        """
        try:
            proceed_selectors = self.region_selectors['proceed_button'].split(', ')
            for selector in proceed_selectors:
                if self.is_visible(selector):
                    self.click(selector)
                    # 等待弹窗关闭（弹窗标题消失）
                    self.page.wait_for_selector(
                        'h5:has-text("切換網站及語系"), h5:has-text("Switching Website and Language Settings")',
                        state='hidden',
                        timeout=15000
                    )
                    logger.info("弹窗已关闭，确定前往成功")
                    return True
            logger.warning("未找到可见的确定前往按钮")
            return False
        except Exception as e:
            logger.exception("点击确定前往按钮异常: %s", e)
            return False
    def check_login_button_highlight(self):
        """检查登录按钮是否高亮"""
        login_btn = self.login_selectors['login_button_highlighted']
        return self.is_enabled(login_btn)

    def click_login_button(self):
        """点击立即登录按钮"""
        login_btn = self.login_selectors['login_button_highlighted']
        self.click(login_btn)

    def click_hot_products(self, timeout=10000):
        """
        点击热门商品入口
        成功返回 True，元素不可见或点击失败返回 False
        """
        hot_link = self.page.locator(self.selectors['hot_products'])
        try:
            # 等待元素可见
            hot_link.first.wait_for(state='visible', timeout=timeout)
            hot_link.first.click()
            self.wait_for_load_state('networkidle')
            logger.info("点击热门商品成功")
            return True
        except Exception as e:
            logger.warning(f"点击热门商品失败: {e}")
            return False

    def click_cart_icon(self):
        """点击购物车图标"""
        self.click(self.selectors['cart_icon'])
        self.wait_for_load_state()


    def click_user_icon(self):
        """点击用户图标"""
        self.click(self.selectors['user_icon'])
        self.wait_for_load_state()


    def scroll_up(self):
        """向上滑动"""
        self.page.evaluate('window.scrollTo(0, 0)')
        time.sleep(1)


    def scroll_down(self):
        """向下滑动"""
        self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)



    # def get_cart_bubble_count(self, timeout=5000) -> int:
    #     # 获取气泡数量
    #     self.navigate("https://www.dogcatstar.com/")
    #     time.sleep(10)
    #     try:
    #         # 尝试直接定位数字气泡
    #         bubble = self.page.locator('.cart-count, .badge, .bubble').first
    #         bubble.wait_for(state='visible', timeout=timeout)
    #         text = bubble.text_content()
    #         logger.info(f"text: {text}")
    #         if text and text.strip().isdigit():
    #             return int(text.strip())
    #         return 0
    #     except Exception:
    #         # 如果找不到独立气泡，退回到链接内提取数字
    #         return self._extract_number_from_cart_link(timeout)
    #
    # def _extract_number_from_cart_link(self, timeout=5000) -> int:
    #     try:
    #         cart_link = self.page.locator('a[href*="/cart"]').first
    #         cart_link.wait_for(state='visible', timeout=timeout)
    #         text = cart_link.text_content()
    #         logger.info(f"text2: {text}")
    #         match = re.search(r'\d+', text)
    #         if match:
    #             return int(match.group())
    #         return 0
    #     except Exception as e:
    #         logger.warning(f"从购物车链接提取数字失败: {e}")
    #         return 0

    # def get_cart_bubble_count(self, timeout=5000) -> int:
    #
    #     try:
    #
    #         self.navigate(url="https://www.dogcatstar.com/", timeout=timeout)
    #         print("===== 调试：所有包含 /cart 的链接 =====")
    #         cart_links = self.page.locator('a[href*="/cart"]').all()
    #         for i, link in enumerate(cart_links):
    #             visible = link.is_visible()
    #             text = link.text_content()
    #             print(f"链接 {i}: visible={visible}, text={text}")
    #
    #         print("===== 调试：所有可能显示数字的元素 =====")
    #         # 尝试常见的数字气泡类名
    #         candidates = self.page.locator(
    #             '.cart-count, .badge, .bubble, .count, [class*="cart"] span, [class*="Cart"] span').all()
    #         for i, el in enumerate(candidates):
    #             visible = el.is_visible()
    #             text = el.text_content()
    #             print(f"元素 {i}: visible={visible}, text={text}, tag={el.evaluate('e => e.tagName')}")
    #         cart_link = self.page.locator('a[href*="/cart"]').first
    #         cart_link.wait_for(state='visible', timeout=timeout)
    #         text = cart_link.text_content()
    #         match = re.search(r'\d+', text)
    #         if match:
    #             return int(match.group())
    #         return 0
    #     except Exception as e:
    #         logger.warning(f"获取购物车数量失败: {e}")
    #         return 0


    def get_cart_bubble_count(self, timeout=5000, debug=False) -> int:
        """
        获取购物车数量，支持调试模式打印所有候选元素。
        """
        self.page.wait_for_timeout(2000)
        start_time = time.time()
        candidates = []

        try:
            # 1. 收集所有可能的购物车链接
            cart_links = self.page.locator('a[href*="/cart"]').all()
            for i, link in enumerate(cart_links):
                candidates.append({
                    'type': 'link',
                    'index': i,
                    'visible': link.is_visible(),
                    'text': link.text_content() or '',
                    'html': link.inner_html() if debug else ''
                })

            # 2. 收集常见数字气泡类名的元素
            count_selectors = [
                '.cart-count', '.badge', '.bubble', '.count',
                '[class*="cart"] span', '[class*="Cart"] span',
                'span:has-text("0")', 'span:has-text("1")', 'span:has-text("2")',  # 直接匹配数字文本
                'span[class*="count"]', 'div[class*="count"]',
            ]
            for selector in count_selectors:
                elements = self.page.locator(selector).all()
                for j, el in enumerate(elements):
                    candidates.append({
                        'type': 'bubble',
                        'selector': selector,
                        'index': j,
                        'visible': el.is_visible(),
                        'text': el.text_content() or '',
                        'html': el.inner_html() if debug else ''
                    })

            # 调试输出
            if debug:
                print("\n===== 购物车数量候选元素 =====")
                for cand in candidates:
                    print(f"类型: {cand['type']}, 可见: {cand['visible']}, 文本: {repr(cand['text'])}")
                    if cand.get('html'):
                        print(f"  HTML: {cand['html']}")
                print("============================\n")

            # 3. 遍历候选，优先选可见且包含数字的
            for cand in candidates:
                if cand['visible'] and cand['text']:
                    match = re.search(r'\d+', cand['text'])
                    if match:
                        count = int(match.group())
                        logger.info(f"从{cand['type']}获取到购物车数量: {count}")
                        return count

            # 如果超时仍未找到，返回0
            logger.warning("未找到可见的购物车数字元素")
            return 0

        except Exception as e:
            logger.exception(f"获取购物车数量异常: {e}")
            return 0
    def click_mobile_menu_button(self, timeout: int = 10000, auto_switch_viewport: bool = True) -> bool:
        """
        点击移动端菜单按钮，如果按钮不可见且 auto_switch_viewport=True，则尝试切换到移动视口
        """
        try:
            button = self.page.locator('button.react-mobile-menu-button')
            if button.count() == 0:
                button = self.page.locator('button:has(img[alt="mobile-menu"])')

            if button.count() == 0:
                logger.error("未找到移动菜单按钮")
                return False

            if not button.first.is_visible() and auto_switch_viewport:
                logger.info("移动菜单按钮不可见，尝试切换为移动视口")
                self.set_mobile_viewport()
                # 重新等待按钮可见
                button.first.wait_for(state='visible', timeout=timeout)
            else:
                button.first.wait_for(state='visible', timeout=timeout)

            button.first.click()
            logger.info("点击移动端菜单按钮成功")
            return True
        except Exception as e:
            logger.exception(f"点击移动端菜单按钮失败: {e}")
            return False

    def set_mobile_viewport(self):
        """设置为移动视口"""
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.wait_for_timeout(500)  # 等待响应式布局调整

    def set_desktop_viewport(self):
        """恢复桌面视口"""
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.wait_for_timeout(500)

    def wait_for_mobile_menu_sidebar(self, timeout: int = 10000) -> bool:
        """
        等待移动端侧边栏菜单出现
        成功返回 True，失败返回 False
        """
        try:
            # 侧边栏通常会有特定的 class 或 role
            sidebar = self.page.locator('[role="dialog"], .mobile-menu-sidebar, .drawer')
            sidebar.wait_for(state='visible', timeout=timeout)
            logger.info("移动端侧边栏菜单已显示")
            return True
        except Exception as e:
            logger.exception(f"移动端侧边栏菜单未出现: {e}")
            return False

    def close_mobile_menu_sidebar(self, timeout: int = 10000) -> bool:
        """
        关闭移动端侧边栏菜单
        成功返回 True，失败返回 False
        """
        try:
            # 尝试点击关闭按钮或背景遮罩
            close_button = self.page.locator(
                'button:has-text("關閉"), '
                'button:has-text("Close"), '
                '.drawer-close, '
                '[aria-label="Close"]'
            ).first
            if close_button.is_visible():
                close_button.click()
            else:
                # 按 ESC 键关闭
                self.page.keyboard.press('Escape')
            logger.info("关闭移动端侧边栏菜单成功")
            return True
        except Exception as e:
            logger.exception(f"关闭移动端侧边栏菜单失败: {e}")
            return False


    def expand_cat_section(self, timeout: int = 10000) -> bool:
        """
        展开侧边栏中的「貓咪專區」分类
        成功返回 True，失败返回 False
        """
        try:
            # 检查分类标题是否存在
            cat_title = self.page.locator('.main-menu .title:has-text("貓咪專區")')
            cat_title.wait_for(state='visible', timeout=timeout)

            # 查找展开按钮（icon_add）
            expand_btn = self.page.locator(
                '.main-menu .icon:not([style*="display: none"]) svg title:has-text("icon_add")').locator(
                'xpath=../../..')

            if expand_btn.count() > 0 and expand_btn.first.is_visible():
                expand_btn.first.click()
                logger.info("展开「貓咪專區」成功")
                self.page.wait_for_timeout(500)  # 等待动画完成
                return True
            else:
                logger.info("「貓咪專區」已处于展开状态")
                return True
        except Exception as e:
            logger.exception(f"展开「貓咪專區」失败: {e}")
            return False

    def collapse_cat_section(self, timeout: int = 10000) -> bool:
        """
        折叠侧边栏中的「貓咪專區」分类
        成功返回 True，失败返回 False
        """
        try:
            # 查找折叠按钮（icon_collapse）
            collapse_btn = self.page.locator('.main-menu .icon svg title:has-text("icon_collapse")').locator(
                'xpath=../../..')

            if collapse_btn.count() > 0 and collapse_btn.first.is_visible():
                collapse_btn.first.click()
                logger.info("折叠「貓咪專區」成功")
                self.page.wait_for_timeout(500)
                return True
            else:
                logger.info("「貓咪專區」已处于折叠状态")
                return True
        except Exception as e:
            logger.exception(f"折叠「貓咪專區」失败: {e}")
            return False

    def click_cat_subcategory(self, subcategory_name: str, timeout: int = 10000) -> bool:
        """
        点击「貓咪專區」下的子分类
        :param subcategory_name: 子分类名称，如 "貓乾糧", "貓罐頭"
        """
        try:
            # 确保分类已展开
            self.expand_cat_section(timeout)

            # 点击指定子分类
            subcategory = self.page.locator(f'.main-menu .sub-menu a:has-text("{subcategory_name}")')
            subcategory.wait_for(state='visible', timeout=timeout)
            subcategory.click()
            logger.info(f"点击子分类「{subcategory_name}」成功")
            self.wait_for_load_state()
            return True
        except Exception as e:
            logger.exception(f"点击子分类「{subcategory_name}」失败: {e}")
            return False

    def get_all_cat_subcategories(self) -> list[str]:
        """
        获取「貓咪專區」下所有子分类名称
        """
        try:
            self.expand_cat_section()
            subcategories = self.page.locator('.main-menu .sub-menu a')
            count = subcategories.count()
            names = []
            for i in range(count):
                name = subcategories.nth(i).text_content()
                if name:
                    names.append(name.strip())
            logger.info(f"获取到 {len(names)} 个子分类: {names}")
            return names
        except Exception as e:
            logger.exception(f"获取子分类列表失败: {e}")
            return []



    def click_cat_staple_food(self, timeout: int = 10000) -> bool:
        """
        在侧边栏中点击「貓咪主食」菜单
        前提：已打开侧边栏且已展开貓咪專區
        成功返回 True，失败返回 False
        """
        try:
            # 定位包含「貓咪主食」的子菜单项
            staple_food = self.page.locator(
                '.sub-menu:has(.sub-menu-title:has-text("貓咪主食")) '
                '>> .sub-menu-title:has-text("貓咪主食")'
            )

            # 等待元素可见并点击
            staple_food.wait_for(state='visible', timeout=timeout)
            staple_food.click()

            logger.info("点击侧边栏「貓咪主食」成功")
            self.wait_for_load_state()
            return True

        except Exception as e:
            logger.exception(f"点击「貓咪主食」失败: {e}")
            return False

    def click_cat_submenu_by_name(self, menu_name: str, timeout: int = 10000) -> bool:
        """
        根据菜单名称点击貓咪專區下的子菜单
        :param menu_name: 菜单名称，如 "貓咪主食", "保健食品", "貓砂系列" 等
        """
        try:
            menu_item = self.page.locator(
                f'.sub-menu:has(.sub-menu-title:has-text("{menu_name}")) '
                f'>> .sub-menu-title:has-text("{menu_name}")'
            )
            menu_item.wait_for(state='visible', timeout=timeout)
            menu_item.click()
            logger.info(f"点击侧边栏「{menu_name}」成功")
            self.wait_for_load_state()
            return True
        except Exception as e:
            logger.exception(f"点击「{menu_name}」失败: {e}")
            return False

    def get_all_cat_submenu_names(self) -> list[str]:
        """
        获取貓咪專區下所有子菜单名称
        """
        try:
            # 等待子菜单区域可见
            submenu_box = self.page.locator('.sub-menu-box.menu__sub-menu--show')
            submenu_box.wait_for(state='visible', timeout=5000)

            # 获取所有子菜单标题
            titles = submenu_box.locator('.sub-menu-title')
            count = titles.count()

            menu_names = []
            for i in range(count):
                name = titles.nth(i).text_content()
                if name:
                    menu_names.append(name.strip())

            logger.info(f"获取到 {len(menu_names)} 个子菜单: {menu_names}")
            return menu_names

        except Exception as e:
            logger.exception(f"获取子菜单列表失败: {e}")
            return []




    def click_category_view_all(self, category_name: str, timeout: int = 10000) -> bool:
        """
        点击指定分类下的「查看全部」链接
        :param category_name: 分类名称，如 "貓咪主食", "保健食品"
        """
        try:
            # 定位对应分类下的查看全部链接
            view_all = self.page.locator(
                f'.sub-menu:has(.sub-menu-title:has-text("{category_name}")) '
                f'>> a.all-product.second:has-text("查看全部")'
            )
            view_all.wait_for(state='visible', timeout=timeout)
            view_all.click()
            logger.info(f"点击「{category_name}-查看全部」成功")
            self.wait_for_load_state()
            return True
        except Exception as e:
            logger.exception(f"点击「{category_name}-查看全部」失败: {e}")
            return False

    def is_cat_staple_view_all_visible(self, timeout: int = 5000) -> bool:
        """
        检查猫咪主食的「查看全部」链接是否可见
        """
        try:
            view_all = self.page.locator('a.all-product.second:has-text("查看全部")')
            return view_all.is_visible(timeout=timeout)
        except:
            return False

    def click_cat_staple_view_all(self):
        try:
            # 方式1：通过文本和class定位
            self.click(self.selectors['sidebar_cat_staple_view_all'])
            logger.info("点击「猫咪主食-查看全部」成功")
            self.wait_for_load_state()
            return True
        except Exception as e:
            logger.exception(f"点击「猫咪主食-查看全部」失败: {e}")
            return False


    # def click_cat_staple_view_all(self, timeout: int = 10000) -> bool:
    #     """
    #     点击猫咪主食分类下的「查看全部」链接
    #     前提：已展开猫咪主食分类
    #     成功返回 True，失败返回 False
    #     """
    #     try:
    #         # 方式1：通过文本和class定位
    #         view_all = self.page.locator('a.all-product.second:has-text("查看全部")')
    #
    #         # 方式2：通过href包含猫咪主食编码定位（更稳定）
    #         # view_all = self.page.locator('a.all-product.second[href*="%e8%b2%93%e5%92%aa%e4%b8%bb%e9%a3%9f"]')
    #
    #         view_all.wait_for(state='visible', timeout=timeout)
    #         view_all.click()
    #
    #         logger.info("点击「猫咪主食-查看全部」成功")
    #         self.wait_for_load_state()
    #         return True
    #
    #     except Exception as e:
    #         logger.exception(f"点击「猫咪主食-查看全部」失败: {e}")
    #         return False
# ---------------切换成主页面顶部点击-------------
    def click_cat_zone_image(self, timeout: int = 10000) -> bool:
        """
        打开移动菜单后点击「貓咪專區」图片
        成功返回 True，失败返回 False
        """
        try:
            # 1. 先点击移动菜单按钮（如果菜单未打开）
            self.click_mobile_menu_button(timeout=timeout)

            # 2. 等待菜单完全展开（等待特定元素出现）
            self.page.wait_for_selector('.main-menu', state='visible', timeout=timeout)

            # 3. 点击图片（使用 alt 定位）
            cat_img = self.page.locator('img[alt="貓咪專區"]')
            cat_img.wait_for(state='visible', timeout=timeout)
            cat_img.click()

            logger.info("成功点击「貓咪專區」图片")
            self.wait_for_load_state()
            return True
        except Exception as e:
            logger.exception(f"点击「貓咪專區」图片失败: {e}")
            return False

    def log_out(self):
        # 登出
        try:
            self.navigate(url="https://www.dogcatstar.com/my-account/")


        except Exception as e:
            logger.exception(f": {e}")
            return False



