# tests/test_api_cart_calculate.py
"""
API 自动化测试：购物车计算接口
基于实际抓包信息分析
"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
import requests
import os
import json
import pytest
from dotenv import load_dotenv
from utils.log import logger
import allure

load_dotenv()

API_PATH = "/api/ec/v2/TW/cart/calculate"
TIMEOUT = 10

# ---------- Fixtures ----------
@pytest.fixture(scope="function")
def get_base_url():
    """根据 ENV 环境变量返回对应的 base URL"""
    env = os.getenv("ENV", "DEV")
    base_url = os.getenv("API_BASE_URL", "https://fortune-api.moneynet.tw")
    if env == "DEV":
        base_url = os.getenv("DEV_BASE_URL", "http://localhost:5000")
    logger.info(f"当前环境: {env}, 使用 BASE_URL: {base_url}")
    return base_url

@pytest.fixture(scope="function")
def cart_calculate_url(get_base_url):
    """返回完整的 API URL"""
    return get_base_url + API_PATH

# ---------- 测试数据 ----------
VALID_ORDER_ITEMS = [
    {"sku": "純泥G", "project_code": "DCS", "quantity": 1, "is_addon": False, "is_addon_v2": False, "addon_setting_id": None},
    {"sku": "四季被藍綠米", "project_code": "DCS", "quantity": 1, "is_addon": True, "is_addon_v2": False, "addon_setting_id": None}
]

VALID_CART_VALUES = {
    "cart": {
        "items": [
            {"cartItemId": 2292109, "product_id": 2292104, "variation_id": 2292109, "quantity": 1, "sku": "純泥G",
             "delivery_class": "normal", "project_code": "DCS", "sale_price": 49, "is_addon_v2": False, "parent_product_id": 2292104},
            {"cartItemId": 2336030, "product_id": 2336028, "variation_id": 2336030, "quantity": 1, "sku": "四季被藍綠米",
             "delivery_class": "normal", "project_code": "DCS", "sale_price": 650, "is_addon": True, "is_addon_v2": False, "parent_product_id": 2336028}
        ],
        "addonItems": []
    },
    "rewardPoints": {"userInputRewardPoints": 0, "isUserAppliedRewardPoints": False},
    "coupon": {"manualInputCouponIds": [], "selectedGiveaways": [], "redeemedCodes": []},
    "billing": {"billingCountry": "TW"},
    "shipping": {"appliedShippingMethodId": 2},
    "payment": {},
    "invoice": {"refundStatement": True, "receiptType": "non_business_einvoice"}
}

def build_payload():
    import copy
    return {
        "billing_country": "TW",
        "project_code": "DCS",
        "country_code": "TW",
        "order_items": copy.deepcopy(VALID_ORDER_ITEMS),
        "manual_input_coupon_ids": [],
        "applied_shipping_method_id": 2,
        "language": "zh_TW",
        "cart_values": copy.deepcopy(VALID_CART_VALUES),
        "coupon_code": "",
        "shipping_method": "standard",
        "test_s": "s0"
    }

# ---------- 辅助函数：构造请求头 ----------
def get_headers(with_auth=True):
    """返回请求头字典"""
    headers = {
        "Origin": "https://www.dogcatstar.com",
        "Content-Type": "application/json",
        "Accept-Language": "zh-TW"
    }
    if with_auth:
        token = os.getenv("API_TOKEN")
        x_token = os.getenv("X_PLATFORM_TOKEN")
        if not token or not x_token:
            pytest.skip("API_TOKEN 或 X_PLATFORM_TOKEN 未设置，跳过需要认证的测试")
        headers["api-token"] = token
        headers["x-platform-token"] = x_token
    return headers

# ---------- 测试用例 ----------
@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例")  # Allure 特性标记
@allure.story("测试 OPTIONS 预检请求，验证 CORS 头是否正确")  # Allure 用户故事标记
def test_cart_calculate_options_notoken(cart_calculate_url):
    """
    测试 OPTIONS 预检请求，验证 CORS 头是否正确。
    预期状态码 204，并包含 Access-Control-Allow-Origin 等头。
    """
    with allure.step("构造 OPTIONS 请求所需的头（模拟浏览器预检）"):
        # 构造 OPTIONS 请求所需的头（模拟浏览器预检）
        headers = get_headers(with_auth=True)
    with allure.step("请求到mock服务"):
        response = requests.options(cart_calculate_url, headers=headers, timeout=TIMEOUT)
        # 记录日志
        logger.info(f"OPTIONS 请求 URL: {cart_calculate_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")

    with allure.step("验证返回 204"):

        assert response.status_code == 204, f"期望 204，实际 {response.status_code}"

        # 验证必要的 CORS 头
        assert response.headers.get("Access-Control-Allow-Origin") == "https://www.dogcatstar.com"
        assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "content-type" in response.headers.get("Access-Control-Allow-Headers", "").lower()
        # 可选：检查是否允许携带凭证
        # assert response.headers.get("Access-Control-Allow-Credentials") == "true"

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-正常场景：购物车计算成功---用例中没有任何优惠和折扣")  # Allure 特性标记
@allure.story("正常场景：购物车计算成功---用例中没有任何优惠和折扣")  # Allure 用户故事标记
def test_cart_calculate_success(cart_calculate_url):
    """
    正常场景：购物车计算成功---用例中没有任何优惠和折扣
    """
    with allure.step("构造请求体"):

        payload = build_payload()
    with allure.step("构造headers"):
        headers = get_headers(with_auth=True)
    with allure.step("请求到mock服务"):
        response = requests.post(cart_calculate_url, json=payload, headers=headers, timeout=TIMEOUT)
        data = response.json()
        # 记录日志
        logger.info(f"OPTIONS 请求 URL: {cart_calculate_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
    with allure.step("验证状态码"):
        assert response.status_code == 200, f"状态码错误: {response.status_code}"
    with allure.step("验证总额:subtotal｜total｜order_items"):
        result = data["data"]["data"]["data"]
        assert "subtotal" in result
        assert "total" in result
        assert "order_items" in result
    # 验证小计（49 + 650 = 699）
        assert result["subtotal"] == 699, f"小计错误: {result['subtotal']}"
    with allure.step("验证购物车每个商品的价格和数量"):

        for item in result["order_items"]:
            if item['id'] == 2292109:
                assert item['sale_price'] == 49
                assert item['quantity'] == 1
            elif item['id'] == 2336030:
                assert item['sale_price'] == 650
                assert item['quantity'] == 1

# ---------- 其他测试用例（示例）----------
@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-未提供认证 token")  # Allure 特性标记
@allure.story("未提供认证 token")  # Allure 用户故事标记
def test_cart_calculate_missing_token(cart_calculate_url):
    """未提供认证 token"""
    with allure.step("构造无token请求"):
        headers = get_headers(with_auth=False)
        payload = {"items": []}
    with allure.step("请求到mock服务"):

        response = requests.post(cart_calculate_url, json=payload, headers=headers, timeout=TIMEOUT)
    # 记录日志
        logger.info(f"OPTIONS 请求 URL: {cart_calculate_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
    with allure.step("验证返回status_code"):
        assert response.status_code in (401, 403)
@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-错误的 HTTP 方法")  # Allure 特性标记
@allure.story("错误的 HTTP 方法")  # Allure 用户故事标记
def test_cart_calculate_invalid_method(cart_calculate_url):
    """错误的 HTTP 方法"""
    with allure.step("不支持的请求方式请求到mock服务"):
        response = requests.get(cart_calculate_url, timeout=TIMEOUT)
        # 记录日志
        logger.info(f"OPTIONS 请求 URL: {cart_calculate_url}")
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
    with allure.step("验证状态码"):

        assert response.status_code == 405

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-数据篡改：修改价格,返回值正确")  # Allure 特性标记
@allure.story(" 数据篡改：修改价格")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):
    """
    数据篡改：修改价格,返回值正确
    """
    with allure.step("构造请求体：修改价格=0.01"):
        payload = build_payload()
        headers = get_headers(with_auth=True)
        for item in payload['cart_values']['cart']['items']:
            if item['cartItemId']==2292109:
                item['sale_price'] = 0.001
    with allure.step("请求到mock服务"):

        response = requests.post(cart_calculate_url, json=payload, headers=headers, timeout=TIMEOUT)
        # 记录日志
        logger.info(f"OPTIONS 请求 URL: {cart_calculate_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
    with allure.step("验证状态码"):

        data = response.json()
        assert response.status_code == 200, f"状态码错误: {response.status_code}"

    with allure.step("验证总计：subtotal｜total｜order_items"):

        result = data["data"]["data"]["data"]
        assert "subtotal" in result
        assert "total" in result
        assert "order_items" in result
        # 验证小计（49 + 650 = 699）
        assert result["subtotal"] == 699, f"小计错误: {result['subtotal']}"
    with allure.step("验证order_items中的商品价格和数量"):
        for item in result["order_items"]:
            if item['id'] == 2292109:
                assert item['sale_price'] == 49
                assert item['quantity'] == 1
            elif item['id'] == 2336030:
                assert item['sale_price'] == 650
                assert item['quantity'] == 1

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-白名单验证")  # Allure 特性标记
@allure.story("白名单验证")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):

    pass

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-边界值验证")  # Allure 特性标记
@allure.story("边界值验证")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):
    pass

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-优惠券验证coupon")  # Allure 特性标记
@allure.story("优惠券验证coupon")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):
    pass

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-其他折扣验证")  # Allure 特性标记
@allure.story("其他折扣验证")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):
    pass

@pytest.mark.api
@pytest.mark.caculate
@allure.feature("route:api/ec/v2/TW/cart/calculate测试用例-接口负载")  # Allure 特性标记
@allure.story("接口负载")  # Allure 用户故事标记
def test_cart_calculate_errprice(cart_calculate_url):
    pass


