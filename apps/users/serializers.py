# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: serializers.py
    Time: 2020/8/23 18:58
    File Intro: 
"""
import re
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_jwt.serializers import VerificationBaseSerializer, RefreshJSONWebTokenSerializer

from config.public_config import REGEX_EMAIL, PASSWORD_REGEX, REGEX_MOBILE
from users.models import VerifyEmailCodeModel

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """
    验证码发送校验
    """
    receiver = serializers.CharField(max_length=200, required=True)
    # choices = ((1, "找回密码"), (2, "修改邮箱"), (4, "登陆"), (5, "注册"))
    send_type = serializers.IntegerField(required=True)

    def validate(self, attrs):
        if "@" in attrs["receiver"]:
            attrs["send_method"] = 1
        else:
            attrs["send_method"] = 2
        return attrs

    def validate_receiver(self, receiver):
        """
        验证账号是否合法
        """
        if not receiver.isdigit():
            if " " not in receiver:
                method = 1
                if not re.match(REGEX_EMAIL, receiver):
                    raise serializers.ValidationError(detail={"msg": "邮箱格式错误", })
            else:
                method = 2
                receiver = receiver.split(" ", 1)[-1]
        else:
            method = 2
        # 验证码发送频率
        one_min_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=30)
        if VerifyEmailCodeModel.objects.filter(send_time__gt=one_min_ago, receiver=receiver, send_method=method):
            raise serializers.ValidationError(detail={"msg": "发送频率过高", })
        return receiver


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # # 联合校验
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=User.objects.all(),
        #         # fields=['mobile', ],
        #         fields=[],
        #         # message="已经存在"
        #     )
        # ]
        # 显示字段
        fields = "__all__"
        # 自读字段
        read_only_fields = ['created_at', ]


class ResetPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, max_length=20, min_length=6)
    password = serializers.CharField(required=True, max_length=20, min_length=6)

    class Meta:
        model = User
        fields = ["password", 'old_password']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_type", "first_name", "last_name", "mobile", "username"]


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册
    """
    username = serializers.CharField(required=True, max_length=100, help_text="用户名")
    email = serializers.CharField(required=True, allow_blank=False, label="邮箱", max_length=100)
    password = serializers.CharField(help_text="密码",
                                     style={'input_type': 'password'}, label='密码', write_only=True, )
    mobile = serializers.CharField(required=True, max_length=20, help_text="电话")

    def validate_password(self, password):
        # 验证密码
        if re.match(PASSWORD_REGEX, password):
            return password
        else:
            raise serializers.ValidationError(detail={"msg": "密码格式错误", })

    def validate_email(self, email):
        # 格式
        if not re.match(REGEX_EMAIL, email):
            raise serializers.ValidationError(detail={"msg": "邮箱格式错误", })
        # 是否注册
        if User.objects.filter(Q(email=email)):
            raise serializers.ValidationError(detail={"msg": "邮箱已存在，请登录", })
        return email

    def validate_mobile(self, mobile):
        # 格式
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError(detail={"msg": "手机格式错误", })
        # 是否注册
        if User.objects.filter(Q(mobile=mobile)):
            raise serializers.ValidationError(detail={"msg": "手机号已存在，请登录", })
        return mobile

    def create(self, validated_data):
        # 拿到创建后的用户

        # 默认不激活，方便后期添加邮件激活，现阶段后台审核
        # validated_data['is_active'] = True
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ["id", "email", "password", "mobile", "username"]


class ChangePasswordPageSerializer(serializers.Serializer):
    """
    修改密码页面验证
    """
    token = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        cache_token = cache.get(attrs["email"])

        if attrs["token"] != cache_token:
            raise serializers.ValidationError(detail={"msg": "token 过期", })
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码
    """
    token = serializers.CharField(max_length=200, required=True)

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=20, min_length=4)

    def validate(self, attrs):
        cache_token = cache.get(attrs["email"])

        if attrs["token"] != cache_token:
            raise serializers.ValidationError(detail={"msg": "token 过期", })
        if not re.match(PASSWORD_REGEX, attrs["password"]):
            raise serializers.ValidationError(detail={"msg": '密码错误', })
        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    """
    忘记密码
    """
    email = serializers.EmailField(required=True)
    language = serializers.IntegerField(required=False)

    def validate_email(self, email):

        if not re.match(REGEX_EMAIL, email):
            raise serializers.ValidationError(detail={"msg": "邮箱格式错误", })

        # 是否注册
        if not User.objects.filter(Q(email=email)):
            raise serializers.ValidationError(detail={"msg": "用户未注册", })
        return email

    def create(self, validated_data):
        validated_data["token"] = 123456
        validated_data["created_at"] = datetime.now()
        instance = VerifyEmailCodeModel.objects.create(**validated_data)
        instance.save()
        return instance


class ClassifyEmailVerifyJSONWebTokenSerializer(VerificationBaseSerializer):
    """
    自定义token验证，增加缓存数据验证
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        # cache_token = cache.get(payload["email"] + settings.REDIS_TOKEN_SUFFIX)
        # TODO login 唯一性
        if token:
            return {
                'token': token,
                'user': self._check_user(payload=payload)

            }
        else:
            raise serializers.ValidationError(detail={"msg": "token 过期", })
