# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: adminx.py
    Time: 2020/8/23 18:04
    File Intro: 
"""
from django.contrib.auth import get_user_model
from django.utils.html import format_html

import xadmin


class UserAdmin(object):
    list_display_links = ["username", "id"]
    list_display = ["id", "username", "name", "title", "mobile", "use_languages", "date_joined", "is_review", 'brand']
    model_icon = "fa fa-user"
    readonly_fields = ['created_at', 'updated_at', "is_del", "gender",
                       'deleted_at']
    # show_detail_fields = [""]
    exclude = ['groups', "user_permissions", "password", "is_superuser", "joined_date", "is_acvtive", ]

    def name(self, obj):
        return obj.first_name + " " + obj.last_name if obj.first_name else obj.username

    # def brand(self, obj):
    #     brand = BrandModel.objects.filter(created_user=obj, is_del=1).first()
    #     return format_html('<a href="/xadmin/brand/brandmodel/{}/update/"><span>{}</span></a>', brand.id, brand.name_zh)

    # brand.short_description = "品牌"
    name.short_description = "姓名"
    add_form_template = 'create_user.html'


xadmin.site.unregister(get_user_model())
xadmin.site.register(get_user_model(), UserAdmin)
