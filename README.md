# DogCatStar 自动化测试项目

基于 `pytest` + `Playwright` 的 UI 自动化测试框架，用于测试汪喵星球（dogcatstar.com）网站的会员登录、商品加购等核心业务流程。

## 📋 环境要求

- Python 3.9 或更高版本
- 操作系统：Windows / macOS / Linux
- 已安装 Git

## 🚀 快速开始

### 1克隆项目
```bash
git clone <你的仓库地址>
cd test-dogcatstar

### 2.创建并激活虚拟环境（推荐）
```bash

python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

### 3.安装依赖
pip install -r requirements.txt
playwright install chromium     # 安装 Chromium 浏览器驱动

### 4.配置测试账号

config下的config.ini配置账号
.env配置账号和环境变量


### 5.运行测试
# 运行所有测试
pytest

# 按标记运行（例如只运行登录加购用例）
pytest  -m "ui or api"

#直接执行 生成 Allure 报告
pytest  -m "ui or api" -n auto --dist loadscope -v --alluredir=./allure-results
#启动allure服务 查看报告
allure serve ./allure-results

bash
# 使用默认文件名（auth.json 或 auth_{LOGIN_METHOD}.json）
pytest tests/

# 指定自定义文件
pytest --storage-state=my_auth.json tests/



项目结构
test-dogcatstar/
├── api/                                # API 测试模块
│   └── tests/                          # API 测试用例
│       ├── conftest.py                 # API 测试专属 fixture
│       ├── test_cart_calculate.py       # 购物车计算接口测试
│       └── ...                          # 其他 API 测试文件
├── config/                             # 配置文件
│   ├── locators.ini                     # 页面元素定位器
│   └── config.ini                       # 其他环境配置
├── ui/                                 # UI 测试模块
│   ├── pages/                          # 页面对象模型
│   │   ├── base_page.py
│   │   ├── main_page.py
│   │   ├── login_page.py
│   │   └── ...
│   └── tests/                          # UI 测试用例
│       ├── conftest.py                  # UI 测试专属 fixture
│       ├── test_login_cart.py           # 登录加购测试
│       ├── test_region_pop.py           # 地区弹窗测试
│       └── ...
├── utils/                              # 通用工具模块
│   ├── helpers.py
│   ├── log.py
│   └── login_helper.py                  # Google 登录辅助函数
├── .env                                 # 环境变量（不提交）
├── .gitignore
├── pytest.ini                           # pytest 全局配置
├── requirements.txt
├── README.md
├── mock_server.py                       # API mock 服务（可选）
├── Logs/                                # 日志输出目录
└── outputs/                             # 测试报告/截图输出




