# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: my_backend.py
    Time: 2020/8/23 15:54
    File Intro: 
"""
from datetime import datetime, timedelta
import logging
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.db.models import Q
from rest_framework import mixins, serializers

logger = logging.getLogger("django")
# Create your views here.
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义 用户验证 来替换django本身的验证 可以通过 username 或 mobile 查询出用户
    """

    def authenticate(self, request, username=None, password=None, user_type=None, login_type=None, **kwargs):
        def check_pw(user, pw):
            """校验密码"""
            if user.check_password(pw):
                user.last_login = datetime.now()
                user.save()
                return user

        user = User.objects.filter(Q(email=username) | Q(mobile=username) | Q(username=username)).first()
        if password and user:
            if user.password:
                return check_pw(user, password)
        else:
            raise serializers.ValidationError(detail={"msg": "参数错误", })
