# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: jwt_auth.py
    Time: 2020/8/23 16:11
    File Intro: 自定义的 jwt 的验证
"""
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db.models import Q
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ClassifyEmailJsonTokenAuthentication(BaseJSONWebTokenAuthentication):

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            info = jwt_decode_handler(auth[1])
            return auth[1]
        except Exception as e:
            raise serializers.ValidationError(detail={"msg": "token 过期", })
        # TODO 校验 redis 数据时间的一致性
        # cache_token = cache.get(info['email'] + settings.REDIS_TOKEN_SUFFIX)
        # if cache_token == auth[1].decode("utf-8"):
        #     return auth[1]
        # else:
        #     raise serializers.ValidationError(detail=TOKEN_EXPIRED)
