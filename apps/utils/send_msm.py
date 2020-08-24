# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: send_msm.py
    Time: 2020/8/23 21:13
    File Intro:  短信验证码发送 和 邮箱发送
"""
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import smtplib
from email.mime.text import MIMEText
from rest_framework import serializers
from django.core.mail import EmailMultiAlternatives
from config.private import ALI_SMS_APP_KEY, ALI_SMS_SECRET_KEY

client = AcsClient(ALI_SMS_APP_KEY, ALI_SMS_SECRET_KEY, 'cn-hangzhou')


def send(phone_num: str, code: str):
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('http')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone_num)
    request.add_query_param('SignName', "HOTNEST")
    request.add_query_param('TemplateCode', "SMS_191470428")
    # FIXME 这个code是自己阿里的设置，必要时要改
    request.add_query_param('TemplateParam', {"code": code})

    response = client.do_action_with_exception(request)
    return json.loads(response, encoding="utf-8")


def send_email(subject, message, from_email, recipient_list):
    """
    将含图片以邮件形式发送给用户
    :param subject: 邮件标题
    :param message: 邮件内容 可以是html代码快
    :param from_email: 发送邮件的邮箱
    :param recipient_list: 接收邮件的邮箱列表
    :return:
    """
    log_content = """
    <table>
        <tr>
            {}
        </tr>
        <tr>
            <br/><br/><br/>
            <td><img width="100" src='可以各种云的网站'/></td>
        </tr>
        <tr>
            <td>-------------------------------------------------------</td>
        </tr>
        <tr>
            <td>*******</td>
        </tr>
        <tr>
            <td>*******</td>
        </tr>
        <tr>
            <td>*******</td>
        </tr>
        <tr>
            <td>*******</td>
        </tr>
    </table>
    """
    try:
        text_content = log_content.format(message)
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(text_content, "text/html")
        return msg.send()
    except Exception as e:
        raise serializers.ValidationError(detail={"receiver": {"msg_zh": "发送失败", "msg_en": "sending failure"}})
