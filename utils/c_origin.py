#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : c_origin.py
Time    : 2026/2/10 
Author  : xixi
File    : 
#-------------------------------------------------------------
"""


def handle_language_region_modal(self):
    """处理语言和地区选择弹窗"""
    try:
        # 等待弹窗出现，这里用可能包含的文本作为选择器，实际需要根据网站调整
        # 假设弹窗包含“选择语言”或“选择地区”等文字
        modal_selectors = [
            "div:has-text('选择语言')",
            "div:has-text('选择地区')",
            "div:has-text('语言和地区')",
            ".language-region-modal",
            "#language-region-modal"
        ]

        modal = None
        for selector in modal_selectors:
            try:
                # 等待最多5秒
                modal = self.page.wait_for_selector(selector, timeout=5000)
                if modal:
                    break
            except:
                continue

        if modal:
            print("检测到语言地区选择弹窗")

            # 选择语言，假设有下拉框或者按钮，这里需要根据实际情况调整
            # 例如，点击语言选择下拉框，选择中文
            # 这里假设语言选择是一个下拉框，id为language-select
            language_select = self.page.locator("#language-select")
            if language_select.count() > 0:
                language_select.select_option("zh-TW")  # 假设值为zh-TW

            # 选择地区，假设地区选择下拉框，id为region-select
            region_select = self.page.locator("#region-select")
            if region_select.count() > 0:
                region_select.select_option("TW")  # 假设值为TW

            # 点击确认按钮，假设按钮文字为“确认”或“确定”
            confirm_button = self.page.locator("button:has-text('确认'), button:has-text('确定')").first
            if confirm_button.count() > 0:
                confirm_button.click()

            # 等待弹窗消失
            self.page.wait_for_timeout(1000)

            # 验证session storage是否设置
            session_storage = self.page.evaluate("""() => {
                return {
                    has_user_confirmed_country_code: sessionStorage.getItem('has_user_confirmed_country_code'),
                    has_user_confirmed_locale: sessionStorage.getItem('has_user_confirmed_locale')
                };
            }""")

            print(f"Session storage设置: {session_storage}")

            return True
        else:
            print("未检测到语言地区选择弹窗")
            return False
    except Exception as e:
        print(f"处理语言地区选择弹窗时出错: {e}")
        return False
