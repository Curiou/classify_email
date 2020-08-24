# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: utils.py
    Time: 2020/8/23 22:03
    File Intro: 
"""
import hashlib
import random
import string


def get_ip(request) -> str:
    """
    获取当前请求的ip地址
    :param request:
    :return:
    """
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    return ip


def get_md5(s: str):
    """
    将字符串生成md5形式返回
    :param s: 字符串
    :return:
    """
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def generate_str(num=6):
    """
    随机从0-9，a-z，A-Z 中取值组成字符串
    默认6字符
    :param num:
    :return:
    """
    ss = string.ascii_letters + string.digits
    if not isinstance(num, int):
        num = 6
    return "".join(random.sample(ss, num))


def generate_code(num=6):
    """
    随机从0-9，中取值组成字符串
    默认6字符
    :param num:
    :return:
    """
    seeds = string.digits
    if not isinstance(num, int):
        num = 6
    return "".join(random.sample(seeds, num))
