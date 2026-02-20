#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : login_page.py
Time    : 2026/2/11 
Author  : xixi
File    : api/pages
#-------------------------------------------------------------
"""

import re

from playwright.sync_api import Page

from ui.pages.base_page import BasePage

import time
from ui.pages.main_page import MainPage
from utils.log import logger



class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.selectors = self.config['LOGIN_PAGE']
        self.user_account = self.param['USER']

    def goto_login_account(self, timeout: int = 30000):
        """
        :param timeout: 超时时间（毫秒）
        """

        login_account_url = "https://www.dogcatstar.com/my-account/"
        self.navigate(login_account_url)
        # 可选：等待页面加载完成
        if self.wait_for_login_modal():

            logger.info("已进入用户登录页面")


    def wait_for_login_modal(self, timeout=10000):
        """等待选择弹窗出现"""
        try:

            # 定义可能出现的弹窗特征 - 更精确的选择器
            modal_indicators = [
                # 英文标题
                "h4:has-text('Please enter phone number')",
                # 繁体中文标题
                "h5:has-text('請輸入您的手機號碼')",
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
                                # 获取元素文本内容
                                try:
                                    text_content = element.text_content()
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
                        continue

                # 短时间等待后重试
                time.sleep(0.5)

            # 如果超时，尝试截图或获取页面状态

            # # 获取当前页面状态用于调试
            # try:
            #     page_title = self.page.title()
            #     page_url = self.page.url
            #
            #
            #     # 检查页面是否有其他可能相关的元素
            #     all_h5_elements = self.page.locator("h4").all()
            #     if all_h5_elements:
            #         for idx, h4 in enumerate(all_h5_elements[:5]):  # 只显示前5个
            #             try:
            #                 h5_text = h4.text_content()
            #             except:
            #                 pass
            # except Exception as debug_e:
            #     print(f"调试时出错: {debug_e}")
            #
            # return None
        except Exception as e:
            print(f"等待弹窗时发生错误: {e}")
            return None



    def is_login_modal_visible(self):
        """检查登录弹窗是否可见"""
        return self.is_visible(self.selectors['login_modal'])


    def get_login_title(self):
        """获取登录标题"""
        return self.get_text(self.selectors['phone_login_title'])


    def click_country_code_dropdown(self):
        """点击国家代码下拉框"""
        # 检查下拉框是否被禁用
        if self.is_visible(self.selectors['country_code_dropdown_disabled']):
            print("国家代码下拉框被禁用")
            return False

        self.click(self.selectors['country_code_dropdown'])
        time.sleep(0.5)


        return True


    def get_selected_country_code(self):
        """获取当前选中的国家代码"""
        dropdown = self.page.query_selector(self.selectors['country_code_dropdown'])
        if dropdown:
            text = dropdown.text_content()
            # 提取国家代码，例如 "+886"
            match = re.search(r'\+\d+', text)
            if match:
                return match.group(0)

            # 检查是否有国旗图片
            flag = dropdown.query_selector(self.selectors['country_code_flag'])
            if flag:
                alt_text = flag.get_attribute('alt')
                return alt_text

        return None


    def get_country_code_options(self):
        """获取国家代码选项列表"""
        options = []

        if not self.click_country_code_dropdown():
            return options

            # 等待选项出现
        time.sleep(1)

        option_elements = self.page.query_selector_all(self.selectors['country_code_options'])

        for element in option_elements:
            try:
                # 获取国旗
                flag_img = element.query_selector('img')
                flag_alt = flag_img.get_attribute('alt') if flag_img else None
                flag_src = flag_img.get_attribute('src') if flag_img else None

                # 获取文本
                text = element.text_content()

                # 提取国家代码
                code_match = re.search(r'\+\d+', text)
                country_code = code_match.group(0) if code_match else None

                # 提取国家名称
                country_name = text.replace(country_code, '').strip() if country_code else text.strip()

                options.append({
                    'element': element,
                    'country_code': country_code,
                    'country_name': country_name,
                    'flag_alt': flag_alt,
                    'flag_src': flag_src,
                    'full_text': text.strip()
                })
            except:
                continue

            # 关闭下拉框
            self.page.click('body')
            time.sleep(0.5)

        return options


    def select_country_code(self, country_code: str):
        """选择国家代码"""
        options = self.get_country_code_options()

        for option in options:
            if option['country_code'] == country_code:
                option['element'].click()
                time.sleep(0.5)
            return True

        return False


    def select_country_by_name(self, country_name: str):
        """根据国家名称选择"""
        options = self.get_country_code_options()

        for option in options:
            if country_name in option['country_name'] or country_name in option['full_text']:
                option['element'].click()
                time.sleep(0.5)
            return True

        return False


    def enter_phone_number(self, phone_number: str):
        """输入手机号"""
        # 等待输入框可用
        self.wait_for_selector(self.selectors['phone_input_active'])

        # 清空输入框
        self.page.fill(self.selectors['phone_input'], '')

        # 输入手机号
        self.page.fill(self.selectors['phone_input'], phone_number)
        time.sleep(0.3)


    def get_entered_phone_number(self):
        """获取已输入的手机号"""
        return self.page.get_attribute(self.selectors['phone_input'], 'value')


    def click_login_register_button(self):
        """点击登录/注册按钮"""
        # 检查按钮是否可用
        if self.is_visible(self.selectors['login_register_button_enabled']):
            self.click(self.selectors['login_register_button'])
        return True



    def is_login_button_enabled(self):
        """检查登录/注册按钮是否可用"""
        return self.is_visible(self.selectors['login_register_button_enabled'])


    def is_phone_format_error_visible(self):
        """检查手机号格式错误提示是否可见"""
        return self.is_visible(self.selectors['phone_format_error'])


    def get_phone_format_error_text(self):
        """获取手机号格式错误提示文本"""
        if self.is_phone_format_error_visible():
            return self.get_text(self.selectors['phone_format_error'])
        return None


    def click_third_party_login(self, provider: str):
        """点击第三方登录按钮"""
        provider_selectors = {
            'line': self.selectors['line_login_button'],
            'facebook': self.selectors['facebook_login_button'],
            'google': self.selectors['google_login_button'],
            'email': self.selectors['email_login_button']
        }

        if provider in provider_selectors:
            selector = provider_selectors[provider]
            if self.is_visible(selector):
                self.click(selector)
            return True

        return False


    def click_google_login(self):
        """点击Google登录按钮"""
        return self.click_third_party_login('google')


    def click_email_login(self):
        """点击Email登录按钮"""
        return self.click_third_party_login('email')


    def click_line_login(self):
        """点击LINE登录按钮"""
        return self.click_third_party_login('line')


    def click_facebook_login(self):
        """点击Facebook登录按钮"""
        return self.click_third_party_login('facebook')


    def wait_for_verification_modal(self, timeout=10000):
        """等待验证码弹窗出现"""
        self.wait_for_selector(self.selectors['verification_modal'], timeout=timeout)


    def is_verification_modal_visible(self):
        """检查验证码弹窗是否可见"""
        return self.is_visible(self.selectors['verification_modal'])


    def get_verification_title(self):
        """获取验证标题"""
        return self.get_text(self.selectors['verification_title'])


    def get_displayed_phone_number(self):
        """获取显示的手机号"""
        if self.is_visible(self.selectors['phone_number_display']):
            return self.get_text(self.selectors['phone_number_display'])
        return None


    def click_resend_button(self):
        """点击重新发送按钮"""
        if self.is_visible(self.selectors['resend_button']):
            self.click(self.selectors['resend_button'])
        return True



    def get_verification_code_inputs(self):
        """获取验证码输入框"""
        return self.page.query_selector_all(self.selectors['verification_code_inputs'])


    def enter_verification_code(self, code: str):
        """输入验证码"""
        # 验证码应该是6位数字
        if len(code) != 6 or not code.isdigit():
            raise ValueError("验证码必须是6位数字")

        inputs = self.get_verification_code_inputs()
        if len(inputs) != 6:
            raise Exception(f"找到 {len(inputs)} 个输入框，但需要6个")

        for i, digit in enumerate(code):
            inputs[i].fill(digit)
            time.sleep(0.1)


    def click_back_to_login(self):
        """点击返回登录页按钮"""
        if self.is_visible(self.selectors['back_to_login_button']):
            self.click(self.selectors['back_to_login_button'])
        return True



    def click_customer_service(self):
        """点击客服专线"""
        if self.is_visible(self.selectors['customer_service_link']):
            self.click(self.selectors['customer_service_link'])
        return True



    def get_cart_count(self):
        """获取购物车数量"""
        try:
            # 查找购物车图标旁边的数量
            cart_icon = self.page.query_selector(self.selectors['cart_icon'])
            if cart_icon:
                # 查找最近的父元素中的数量气泡
                parent = cart_icon.query_selector('xpath=..')
                bubble = parent.query_selector(self.selectors['cart_count_bubble'])
                if bubble:
                    count_text = bubble.text_content()
                    return int(count_text) if count_text.isdigit() else 0

            # 备用方法：查找包含数字的购物车链接
            cart_links = self.page.query_selector_all('a[href*="cart"]')
            for link in cart_links:
                text = link.text_content()
                if text and text.strip().isdigit():
                    return int(text.strip())
        except:
            pass

        return 0


    def wait_for_cart_count_update(self, expected_count: int, timeout=10000):
        """等待购物车数量更新"""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_count = self.get_cart_count()
            if current_count == expected_count:

                time.sleep(0.5)

        return False


    def click_user_icon(self):
        """点击用户图标"""
        if self.is_visible(self.selectors['user_icon']):
            self.click(self.selectors['user_icon'])
        return True



    def is_user_logged_in(self):
        """检查用户是否已登录"""
        # 检查是否有已登录的用户图标
        if self.is_visible(self.selectors['user_icon_logged_in']):
            return True

        # 检查是否有userid cookie
        cookies = self.page.context.cookies()
        for cookie in cookies:
            if cookie['name'] == 'userid':
                return True

        return False


    def complete_phone_login(self, phone_number: str, verification_code = None):
        """完成手机号登录流程"""
        # 输入手机号
        self.enter_phone_number(phone_number)


        # 点击登录/注册按钮
        if self.click_login_register_button():
            # 等待验证码弹窗
            try:
                self.wait_for_verification_modal(5000)

                # 如果有验证码，输入验证码
                if verification_code:
                    self.enter_verification_code(verification_code)
                    # 等待登录完成
                    time.sleep(3)
                    return True
                else:
                    print("需要验证码，但未提供")
                    return False
            except Exception as e:
                print(f"未出现验证码弹窗: {e}")
                # 可能不需要验证码，直接登录成功
                time.sleep(3)
                return True

        return False

    # def complete_google_login_embedded(self, email: str, password: str, timeout: int = 30000) -> bool:
    #     """
    #     处理内嵌 Google 登录表单（非弹窗）。
    #     :param email: Google 账号邮箱
    #     :param password: 密码
    #     :param timeout: 超时时间
    #     :return: 成功返回 True
    #     """
    #     try:
    #         # 1. 等待邮箱输入框出现
    #         email_input = self.page.get_by_label("Email or phone").first
    #         email_input.wait_for(state='visible', timeout=timeout)
    #         email_input.fill(email)
    #
    #         # 2. 点击“下一步”按钮
    #         next_button = self.page.get_by_role("button", name="Next").first
    #         next_button.click()
    #
    #         # 3. 等待密码输入框出现
    #         password_input = self.page.get_by_label("Enter your password").first
    #         password_input.wait_for(state='visible', timeout=timeout)
    #         password_input.fill(password)
    #
    #         # 4. 点击“登录”按钮
    #         sign_in_button = self.page.get_by_role("button", name="Sign in").first
    #         sign_in_button.click()
    #
    #         # 5. 等待页面重定向或登录成功（例如回到原网站）
    #         self.page.wait_for_url("**://www.dogcatstar.com/**", timeout=timeout)
    #         logger.info("Google 内嵌登录成功")
    #         return True
    #     except Exception as e:
    #         logger.exception(f"Google 内嵌登录失败: {e}")
    #         return False


    def handle_google_login_popup(self, email: str, password: str):
        """处理Google登录弹窗"""
        # 等待新窗口打开
        with self.page.context.expect_page() as new_page_info:
            # Google登录可能会在新窗口打开
            pass

            # 实际上，我们需要监听popup事件
            popup = self.page.wait_for_event('popup')

            # 在Google登录页面输入凭据
            popup.fill('input[type="email"]', email)
            popup.click('button:has-text("Next")')
            time.sleep(1)

            popup.fill('input[type="password"]', password)
            popup.click('button:has-text("Next")')

            # 等待登录完成
            popup.wait_for_load_state()
            popup.close()

            # 等待主页面更新
            self.page.wait_for_load_state()

    def click_google_login_button(self, timeout: int = 10000) -> bool:
        """
        点击“使用 Google 帳號登入”按钮。
        如果按钮可见且可点击，则点击并返回 True；否则记录异常并返回 False。
        """
        try:
            # 定位器：基于按钮文本，并限定为按钮元素
            google_btn = self.page.locator('button:has-text("使用 Google 帳號登入")').first
            google_btn.wait_for(state='visible', timeout=timeout)
            google_btn.click()
            return True
        except Exception as e:
            return False



    def complete_google_login(self, email: str, password: str):
        """完成Google登录"""
        # 点击Google登录按钮
        if self.click_google_login_button():
            try:
                # 处理Google登录弹窗
                self.handle_google_login_popup(email, password)

                # 等待登录完成，页面重定向
                self.page.wait_for_load_state('networkidle')
                time.sleep(3)

                # 验证登录成功
                return self.is_user_logged_in()
            except Exception as e:
                print(f"Google登录失败: {e}")
                return False


        return False

    # api/pages/login_page.py

    def complete_google_login_embedded(self, email: str, password: str, timeout: int = 30000) -> bool:
        """
        处理内嵌 Google 登录表单，使用稳定属性定位，支持中英文。
        """
        try:

            # --- 第一步：输入邮箱 ---
            # 使用 id 定位邮箱输入框，非常稳定（id="identifierId"）
            email_input = self.page.locator('#identifierId').first
            email_input.wait_for(state='visible', timeout=timeout)
            email_input.fill(email)
            logger.info("已输入邮箱")
            time.sleep(5)

            # --- 第二步：点击“下一步”按钮 ---
            # 使用正则匹配中英文按钮文本
            next_button = self.page.get_by_role("button", name=re.compile("Next|下一步")).first
            next_button.wait_for(state='visible', timeout=timeout)
            next_button.click()
            logger.info("点击下一步按钮")
            time.sleep(5)

            # --- 第三步：等待并输入密码 ---
            # 使用 name 属性定位密码输入框（name="Passwd"）
            password_input = self.page.locator('input[name="Passwd"]').first
            password_input.wait_for(state='visible', timeout=timeout)
            password_input.fill(password)
            logger.info("已输入密码")
            time.sleep(5)
            # # --- 第四步：点击“下一步”按钮 ---
            next_button = self.page.get_by_role("button", name=re.compile("Next|下一步")).first
            next_button.wait_for(state='visible', timeout=timeout)
            next_button.click()
            logger.info("点击下一步按钮")
            time.sleep(3)


            # # --- 第四步：点击“登录”按钮 ---
            # # 使用正则匹配中英文登录按钮
            # sign_in_button = self.page.get_by_role("button", name=re.compile("Sign in|登录")).first
            # sign_in_button.wait_for(state='visible', timeout=timeout)
            # sign_in_button.click()
            # logger.info("点击登录按钮")

            # --- 第五步：等待登录成功并重定向到汪喵星球域名此时没有判断具体路径，具体路径判断需要到具体的测试用例中 ---
            # self.page.wait_for_url("**/my-account/**", timeout=timeout)
            self.page.wait_for_url("**www.dogcatstar.com**", timeout=timeout)

            logger.info("Google 内嵌登录成功，已重定向")
            return True

        except Exception as e:
            logger.exception(f"Google 内嵌登录失败: {e}")
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




        # 关闭浏览器
        browser.close()

