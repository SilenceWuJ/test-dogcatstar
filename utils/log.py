#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------
Name    : log.py
Time    : 2026/2/10 
Author  : xixi
File    : dogcatstar/common
#-------------------------------------------------------------
"""
import logging
# 设置日志颜色的包
import os
import time

import colorlog
from pathlib import Path

'''
Loggers：记录器，提供应用程序代码能直接使用的接口；

Handlers：处理器，将记录器产生的日志发送至目的地；

Filters：过滤器，提供更好的粒度控制，决定哪些日志会被输出；

Formatters：格式化器，设置日志内容的组成结构和消息字段。
        %(name)s Logger的名字         #也就是其中的.getLogger里的路径,或者我们用他的文件名看我们填什么
        %(levelno)s 数字形式的日志级别  #日志里面的打印的对象的级别
        %(levelname)s 文本形式的日志级别 #级别的名称
        %(pathname)s 调用日志输出函数的模块的完整路径名，可能没有
        %(filename)s 调用日志输出函数的模块的文件名
        %(module)s 调用日志输出函数的模块名
        %(funcName)s 调用日志输出函数的函数名
        %(lineno)d 调用日志输出函数的语句所在的代码行
        %(created)f 当前时间，用UNIX标准的表示时间的浮 点数表示
        %(relativeCreated)d 输出日志信息时的，自Logger创建以 来的毫秒数
        %(asctime)s 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
        %(thread)d 线程ID。可能没有
        %(threadName)s 线程名。可能没有
        %(process)d 进程ID。可能没有
        %(message)s用户输出的消息
'''

'''日志颜色配置'''
log_colors_config = {
    # 颜色支持 blue蓝，green绿色，red红色，yellow黄色，cyan青色
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

'''创建logger记录器'''
logger = logging.getLogger('pick')

# 输出到控制台
console_handler = logging.StreamHandler()

'''日志级别设置'''

# logger控制最低输出什么级别日志(优先级最高)
logger.setLevel(logging.DEBUG)

# console_handler设置控制台最低输出级别日志
console_handler.setLevel(logging.DEBUG)

# # 日志输出格式
# #保存文件的日志格式
file_formatter = logging.Formatter(
    fmt='[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S'
)
#
# 控制台的日志格式
console_formatter = colorlog.ColoredFormatter(
    # 输出那些信息，时间，文件名，函数名等等
    fmt='%(log_color)s[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
    # 时间格式
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors_config
)
# log_path = os.path.dirname(os.path.realpath(__file__)) + '/Logs/'  # 日志目录
log_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Logs/'

# log_path = Path(__file__).parent.parent / 'Logs' / ''


formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

if os.path.exists(log_path) == False:  # 目录不存在就创建
    os.makedirs(log_path)

logTime = time.strftime('%Y%m%d%H', time.localtime(time.time()))  # 当前时间到小时
log_file = log_path + logTime + '.log'  # 文件名

if os.path.exists(log_file) == False:  # 日志文件不存在就创建
    fd = open(log_file, mode="w", encoding="utf-8")
    fd.close()

file_handler = logging.FileHandler(filename=log_file, mode='a', encoding='utf8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

# console_handler设置保存到文件最低输出级别日志
file_handler.setLevel(logging.INFO)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

console_handler.close()
file_handler.close()

if __name__ == '__main__':
    # logger.debug('颜色')
    logger.info('00000')

    logger.info('绿色测试日志保存路径')
    logger.warning('颜色')
    logger.error('error')
    logger.critical('critical')
