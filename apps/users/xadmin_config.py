# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: xadmin_config.py
    Time: 2020/8/23 18:04
    File Intro: 
"""
from xadmin.views import CommAdminView, CreateAdminView
from .adminx import UserAdmin
from xadmin import site


class UserCreatePlugin(CommAdminView):
    context = super(CommAdminView).get_context()

    def init_request(self, *args, **kwargs):
        return True


site.register_plugin(UserCreatePlugin, CreateAdminView)
