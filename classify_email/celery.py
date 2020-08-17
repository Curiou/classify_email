# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: public_config.py
    Time: 2020/8/18 1:04
    File Intro:
"""

from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djtest1.settings')
# Specifying the settings here means the celery command line program will know where your Django project is.
# This statement must always appear before the app instance is created, which is what we do next:
from django.conf import settings

app = Celery('djtest1')

app.config_from_object('django.conf:settings')
# This means that you don’t have to use multiple configuration files, and instead configure Celery directly from the Django settings.
# You can pass the object directly here, but using a string is better since then the worker doesn’t have to serialize the object.

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
from celery import Celery, platforms

platforms.C_FORCE_ROOT = True  # 加上这一行 Celery 导入报错


# With the line above Celery will automatically discover tasks in reusable apps if you define all tasks in a separate tasks.py module.
# The tasks.py should be in dir which is added to INSTALLED_APP in settings.py.
# So you do not have to manually add the individual modules to the CELERY_IMPORT in settings.py.

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # dumps its own request information
