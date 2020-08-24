import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class DatetimeOrDel(models.Model):
    is_del = models.BooleanField(default=1, verbose_name="是否删除")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class VerifyEmailCodeModel(DatetimeOrDel):
    token = models.CharField(max_length=100, verbose_name="验证码", help_text="验证码")
    receiver = models.CharField(max_length=200, verbose_name="接收人", help_text="接收人", default=None)
    send_method = models.IntegerField(choices=((1, "邮箱"), (2, "手机")), default=1)
    # choices=((1, "找回密码"), (2, "修改邮箱"), (4, "登陆"), (5, "注册"))
    send_type = models.IntegerField(verbose_name="验证码类型", help_text="验证码类型")
    send_time = models.DateTimeField(verbose_name="发送时间", default=datetime.datetime.now)

    class Meta:
        verbose_name = "邮箱token"
        verbose_name_plural = verbose_name
        db_table = "verify_token"

    def __str__(self):
        return '%s: %s' % (self.receiver, self.token)


class UserProfile(AbstractUser, DatetimeOrDel):
    """
    用户资料
    """
    user_type = models.IntegerField(verbose_name="用户类型", help_text="用户类型", default=2)
    is_staff = models.BooleanField(default=False, verbose_name="是否为后台用户", help_text='是否为后台用户')
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女"), ("female", "未知")), default="male",
                              verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=30, verbose_name="电话", unique=True)
    email = models.EmailField(max_length=50, null=True, blank=True, verbose_name="邮箱", unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "用户基本资料"
        verbose_name_plural = verbose_name
        db_table = "user_info"
        unique_together = ("email", "username",)
        ordering = ["username", ]

    def __str__(self):
        return self.username
