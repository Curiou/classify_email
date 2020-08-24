# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: jwt_auth.py
    Time: 2020/8/23 16:11
    File Intro: 自定义的 jwt 的验证
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db.models import Q
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.compat import Serializer, PasswordField, get_username_field
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler

from users.models import VerifyEmailCodeModel

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ClassifyEmailLoginSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(ClassifyEmailLoginSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    @property
    def username_field(self):
        return get_username_field()

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }
        has_reg = User.objects.filter(
            Q(username=attrs.get(self.username_field)) | Q(email=attrs.get(self.username_field))).first()
        if not has_reg:
            # fixme 用户未注册
            raise serializers.ValidationError(detail={"msg": '账号或密码错误', })

        if all(credentials.values()):
            user = authenticate(**credentials)
            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                # cache.set(user.email + settings.REDIS_TOKEN_SUFFIX, token, timeout=36800 * 7)
                return {
                    'token': token,
                    'user': user
                }
            else:
                # fixme 密码错误
                raise serializers.ValidationError(detail={"msg": '账号或密码错误', })
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)




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


def validate_code(username, code, user=True):
    if " " in username:
        receiver = username.split(" ", 1)[-1]
    else:
        return {"msg": "手机格式错误", }
        # 查询验证码记录
    verify_records = VerifyEmailCodeModel.objects.filter(send_type__in=[4, 5]).filter(
        receiver=receiver, send_method=2).order_by('-send_time')
    if verify_records:
        # 只取最后一条验证码记录进行校验
        last_records = verify_records[0]
        thirty_min_ago = datetime.now() - timedelta(hours=0, minutes=30, seconds=0)
        if last_records.token != code:
            return {"msg": "验证码错误", }
        if last_records.send_time < thirty_min_ago:
            return {"msg": "验证码已超时", }
        if not user:
            User.objects.create(
                **{"username": username.split(" ", 1)[-1], "mobile": username,
                   "user_type": 3, "is_active": True})
    else:
        return {"msg": "验证码错误", }
