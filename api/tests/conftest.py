#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : conftest.py
Time    : 2026/2/20 
Author  : xixi
File    : api/tests
#-------------------------------------------------------------
"""
# conftest.py
import subprocess
import time
import pytest
import requests

@pytest.fixture(scope="session")
def mock_server():
    # 启动 Flask 服务器（后台运行）
    proc = subprocess.Popen(
        ["python", "mock_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # 等待服务器启动
    try:
        requests.get("http://localhost:5000")
    except:
        pytest.fail("mock 服务器启动失败")

    time.sleep(2)
    yield
    # 测试结束后关闭服务器
    proc.terminate()
    proc.wait()