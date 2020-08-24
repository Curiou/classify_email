# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: jwt_auth.py
    Time: 2020/8/23 16:11
    File Intro: 自定义的 jwt 的 登陆验证
"""

from django.conf import settings
from django.core.cache import cache


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    :token  返回的jwt
    :user   当前登录的用户信息[对象]
    :request 当前本次客户端提交过来的数据
    """
    code = 200
    if not user or not token:
        code = 400
    # TODO 保证token 唯一 测试关闭
    # if token:
    #     cache.set(user.username + settings.REDIS_TOKEN_SUFFIX, token, timeout=36800 * 7)
    return {
        "code": code,
        "msg": "ok",
        "data": {
            'token': token,
            'id': user.id,
            'username': user.username,
            'name': user.first_name + " " + user.last_name
        }
    }


def jwt_response_payload_error_handler(serializer, request=None):
    return {
        "msg_zh": "用户名或者密码错误",
        "msg_en": "username password error",
        "status": 400,
        "detail": serializer.errors
    }
