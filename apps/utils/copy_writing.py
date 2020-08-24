# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: copy_writing.py
    Time: 2020/8/23 20:48
    File Intro: 
"""
from config.private import HELP_EMAIL

TEST_HOST = ['127.0.0.1:8090', ]
LINE_HOST = []

EMAIL_TITLE = """欢迎您激活邮箱"""
# todo 帮助邮箱可以自己设置
ADD_COMPANY_EMAIL_CONTEXT = """
尊敬的用户： &nbsp;&nbsp;
<br/><br/>
&nbsp;&nbsp;您的验证码是：{}
<br/><br/>
&nbsp;&nbsp;本邮件30分钟内有效。
<br/><br/>
&nbsp;&nbsp;该邮件是本系统自动发出的激活邮件，请勿直接回复！
<br/><br/>
如需任何帮助，请发送邮件至%s
""" % HELP_EMAIL

PASSWORD_TITLE = """密码重置邮件"""
PASSWORD_CONTEXT = """
您好，{user}： &nbsp;&nbsp;
<br/><br/>
&nbsp;&nbsp;忘记密码了吗？请点击以下链接，我们将协助您修改密码：
<br/><br/>
&nbsp;&nbsp;<a href={url}>{url}</a>
<br/><br/>
&nbsp;&nbsp;如果并非是您申请的重置密码，请忽略
"""
