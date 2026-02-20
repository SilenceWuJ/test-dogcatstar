# 设置环境变量（可选）
export ENV=DEV  # 或 PROD
export API_TOKEN=your_token
export X_PLATFORM_TOKEN=your_token

# 运行单个测试文件
pytest tests/test_api_cart_calculate.py -v