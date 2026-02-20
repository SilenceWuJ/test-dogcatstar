#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : mock_server.py
Time    : 2026/2/20 
Author  : xixi
File    : api
#-------------------------------------------------------------
"""
from xxlimited import Null

# mock_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

MOCK_RESPONSE = {
    "data": {
        "data": {
            "data": {
                "cart_uuid": "mocked-uuid-123",
                "subtotal": 699,
                "total_without_addon_v2": 699,
                "total_after_discount": 699,
                "total_after_shipping": 699,
                "tax": 0,
                "notice_info": None,          # 原 Null → None
                "total": 699,
                "order_items": [
                    {
                        "sku": "純泥G",
                        "quantity": 1,
                        "id": 2292109,
                        "sale_price": 49,
                        "parent_product_id": 2292104,
                        "delivery_class": "normal",
                        "applied_coupon_ids": [4034, 4559, 1292],
                        "subship_info": None,  # 原 Null
                        "is_addon_v2": False,
                        "addon_v2_price": None,
                        "addon_setting_id": None,
                        "addon_scope": None,
                        "addon_main_product_id": None
                    },
                    {
                        "sku": "四季被藍綠米",
                        "quantity": 1,
                        "id": 2336030,
                        "sale_price": 650,
                        "parent_product_id": 2336028,
                        "delivery_class": "normal",
                        "applied_coupon_ids": [4034, 4559, 1292],
                        "subship_info": None,
                        "is_addon_v2": False,
                        "addon_v2_price": None,
                        "addon_setting_id": None,
                        "addon_scope": None,
                        "addon_main_product_id": None
                    }
                ],
                "discount_items": [],
                "applied_coupons": [
                    {
                        "coupon_id": 4034,
                        "criterions": [
                            {
                                "id": 23008,
                                "coupon_id": 4034,
                                "criterion_quantity": 0,
                                "criterion_amount": 0,
                                "applied_status": "invisible",
                                "left_quantity": 0,
                                "left_amount": 0,
                                "count": 0
                            }
                        ]
                    },
                    {
                        "coupon_id": 4559,
                        "criterions": [
                            {
                                "id": 25290,
                                "coupon_id": 4559,
                                "criterion_quantity": 0,
                                "criterion_amount": 0,
                                "applied_status": "invisible",
                                "left_quantity": 0,
                                "left_amount": 0,
                                "count": 0
                            }
                        ]
                    },
                    {
                        "coupon_id": 1292,
                        "criterions": []  # 原为空列表，无 Null
                    }
                ],
                "giveaways": [],
                "applied_shipping_method_id": 2,
                "shipping_methods": [
                    {
                        "shipping_method_id": 2,
                        "shipping_method_type": "home_delivery",
                        "shipping_method_code": "DOD",
                        "name": "宅配",
                        "supported_payment_option_types": [],
                        "total_fee": 0,
                        "shipping_rules": {
                            "normal": [
                                {
                                    "shipping_rule_id": 90,
                                    "delivery_class": "normal",
                                    "excluded_shipping_class": [],
                                    "name": "home_delivery_normal",
                                    "applied_shipping_fee": {
                                        "id": 2049,
                                        "name": "台灣常溫宅配滿 $499 免運",
                                        "min_amount": 499,
                                        "max_amount": None,  # 原 Null
                                        "fee": 0
                                    },
                                    "shipping_fees": [
                                        {
                                            "id": 2048,
                                            "name": "台灣常溫宅配未滿 $499，運費$80",
                                            "min_amount": 0,
                                            "max_amount": 498,
                                            "fee": 80
                                        },
                                        {
                                            "id": 2049,
                                            "name": "台灣常溫宅配滿 $499 免運",
                                            "min_amount": 499,
                                            "max_amount": None,  # 原 Null
                                            "fee": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "discount_rules": {"normal": []}
                    }
                ],
                "cart_validation_messages": [],
                "addon_v2_total": 0,
                "addon_v2_total_before_discount": 0,
                "total_before_tax": 699
            }
        },
        "status": 200,  # 修正为 status（与真实响应一致），而不是 status_code
        "statusText": "",
        "headers": {
            "cache-control": "no-cache, private, no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0",
            "content-type": "application/json"
        }
    },
    "isValidating": True,
    "isLoading": False
}

@app.route('/api/ec/v2/TW/cart/calculate', methods=['POST', 'OPTIONS'])
def mock_cart_calculate():
    # 处理预检请求
    if request.method == 'OPTIONS':
        if 'api-token' not in request.headers or request.headers['api-token'] == "":
            return 'Missing Token', 403
        if 'x-platform-token' not in request.headers or request.headers['x-platform-token'] == "":
            return 'Missing Token', 403
        response = app.response_class()
        response.headers.add('Access-Control-Allow-Origin', 'https://www.dogcatstar.com')
        response.headers.add('Access-Control-Allow-Headers', 'content-type, api-token, x-platform-token')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 204
    if request.method not in ['POST', 'OPTIONS']:
        return 'Method Not Allowed', 405

    if request.method == 'POST':

        if 'api-token' not in request.headers or request.headers['api-token'] == "":
            return 'Missing Token', 401
        if 'x-platform-token' not in request.headers or request.headers['x-platform-token'] == "":
            return 'Missing Token', 403

        # 可基于请求体返回不同响应（例如不同商品数量导致不同总价）
        data = request.get_json()
        total = 0
        mock_response = MOCK_RESPONSE.copy()
        response = jsonify(mock_response)
        response.headers.add('Access-Control-Allow-Origin', 'https://www.dogcatstar.com')
        return response

if __name__ == '__main__':
    app.run(port=5000, debug=True)