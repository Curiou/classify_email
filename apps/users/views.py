from django.shortcuts import render

from datetime import datetime, timedelta
import logging
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import Q
from django_filters import rest_framework
from django_redis import get_redis_connection
from rest_framework import filters
from rest_framework import mixins, serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.views import JSONWebTokenAPIView

from classify_email.settings import REDIS_TOKEN_SUFFIX
from users.models import VerifyEmailCodeModel
from utils.copy_writing import ADD_COMPANY_EMAIL_CONTEXT, EMAIL_TITLE, PASSWORD_TITLE, PASSWORD_CONTEXT
from utils.jwt_auth import ClassifyEmailJsonTokenAuthentication, ClassifyEmailLoginSerializer
from utils.send_msm import send, send_email
from utils.utils import generate_code
from .serializers import UserSerializer, UserRegSerializer, ForgetPasswordSerializer, ChangePasswordSerializer, \
    ChangePasswordPageSerializer, UserUpdateSerializer, ResetPasswordSerializer, SmsSerializer, \
    ClassifyEmailVerifyJSONWebTokenSerializer

logger = logging.getLogger("django")
# Create your views here.
User = get_user_model()

redis_con = get_redis_connection("default")


class SmsCodeViewset(mixins.CreateModelMixin, GenericViewSet):
    """
    send_type ((1, "找回密码"), (2, "修改邮箱"),  (4, "登陆"), (5, "注册"))
    """
    serializer_class = SmsSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = generate_code()
        send_type = serializer.validated_data['send_type']
        language = serializer.validated_data['language']
        send_method = serializer.validated_data["send_method"]
        email = serializer.validated_data['receiver']
        if send_method == 1:
            email_body = ADD_COMPANY_EMAIL_CONTEXT.format(code)
            send_email(EMAIL_TITLE, email_body, settings.EMAIL_FROM, [email])
            VerifyEmailCodeModel.objects.create(receiver=email, token=code, send_type=send_type, send_method=1)
            return Response({
                'receiver': email
            }, status=status.HTTP_201_CREATED)
        elif send_method == 2:
            # 发送手机验证码
            res = send(email, code)
            if res["Code"] == "OK":
                VerifyEmailCodeModel.objects.create(receiver=email, token=code, send_type=send_type, send_method=2)
                return Response({
                    'receiver': email
                }, status=status.HTTP_201_CREATED)
            else:
                raise serializers.ValidationError(detail={"Code": res["Code"], "msg": res["Message"]})
        else:
            raise serializers.ValidationError(detail={"msg": "参数错误", })


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                  mixins.CreateModelMixin):
    """
    用户增删该查
    """
    permission_classes = []
    authentication_classes = [ClassifyEmailJsonTokenAuthentication, SessionAuthentication]
    queryset = User.objects.filter(is_del=1).all().order_by("-id")
    serializer_class = UserSerializer
    filter_backends = (rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ["email", "username", "mobile"]

    def get_permissions(self):
        if self.action == "create":
            return []
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegSerializer
        elif self.action == "update" or self.action == "partial_update":
            return UserUpdateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 拿到返回的user信息 并返回token放入
        user = self.perform_create(serializer)

        # 用jwt生成的token
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.username
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)


class ChangePassword(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    忘记密码 修改密码
    """
    serializer_class = ChangePasswordSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.data["email"]).first()
        user.set_password(serializer.data["password"])
        user.save()
        # 删除JWT TOKEN
        cache.delete(serializer.data["email"] + REDIS_TOKEN_SUFFIX)
        return Response("ok")


class ResetPasswordView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    登陆状态修改密码
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [ClassifyEmailJsonTokenAuthentication, SessionAuthentication]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_ok = user.check_password(serializer.data["old_password"])
        if not check_ok:
            raise serializers.ValidationError({"password": ["旧密码错误"]})
        user.set_password(serializer.data["password"])
        # 删除JWT TOKEN
        cache.delete(user.email + REDIS_TOKEN_SUFFIX)

        user.save()
        return Response(UserSerializer(user).data)


class ChangePasswordPage(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    修改密码token验证
    """
    permission_classes = []
    authentication_classes = [ClassifyEmailJsonTokenAuthentication, SessionAuthentication]
    serializer_class = ChangePasswordPageSerializer

    def create(self, request, *args, **kwargs):
        ser = ChangePasswordPageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return Response(status=200, data=ser.data)


class ForgetPasswordViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    忘记密码
    """
    authentication_classes = []
    serializer_class = ForgetPasswordSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        if settings.DEBUG:
            req_url = settings.TEST_APP_URL
        else:
            # TODO 修改生产地址
            req_url = settings.TEST_APP_URL

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        language = serializer.validated_data['language']
        user = User.objects.filter(is_del=1, email=email).first()
        code = generate_code()

        # 控制时间
        cache.set(email, code, timeout=3600 * 48)
        email_title = "HotNest Reset You   Password"
        target_url = req_url + "reset-p/?token=" + code + "&email=" + email
        # res = async_send_mail.delay(PASSWORD_TITLE_EN, email_body, settings.EMAIL_FROM, [email], html_message=email_body)
        email_body = PASSWORD_CONTEXT.format(user=user, url=target_url)
        send_email(PASSWORD_TITLE, email_body, settings.EMAIL_FROM, [email])

        return Response({
            'email': email
        }, status=status.HTTP_201_CREATED)


class ClassifyEmailTokenVerifyViewSet(JSONWebTokenAPIView):
    """
    自定义账号验证
    """
    serializer_class = ClassifyEmailVerifyJSONWebTokenSerializer


class ClassifyEmailLoginViewSet(JSONWebTokenAPIView):
    """
    自定义token验证
    """
    serializer_class = ClassifyEmailLoginSerializer
