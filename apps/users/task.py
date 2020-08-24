# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: task.py
    Time: 2020/8/23 18:07
    File Intro: 
"""

import time

from celery import shared_task
from celery import Celery, platforms

from utils.send_msm import send_email

platforms.C_FORCE_ROOT = True  # 加上这一行
from django.core.mail import send_mail


@shared_task
def add(a, b):
    return a + b


@shared_task
def async_send_mail(*args, **kwargs):
    send_email(*args, **kwargs)
    return args
