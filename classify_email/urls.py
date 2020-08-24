"""classify_email URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# import xadmin
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
# from xadmin.plugins import xversion

from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import refresh_jwt_token

from users.views import *

# xadmin.autodiscover()
# # version模块自动注册需要版本控制的 Model
# xversion.register_models()

v1 = routers.DefaultRouter()
# 系统
v1.register("users", UserViewSet, basename='users')
v1.register("forget_password", ForgetPasswordViewSet, basename='forget_password')
v1.register("change_password", ChangePassword, basename='change_password')
v1.register("change_password_validate", ChangePasswordPage, basename='change_password_validate')
v1.register("send_email_code", SmsCodeViewset, basename='send_emial_code')

urlpatterns = [
    path('admin/', admin.site.urls),
    # url(r'xadmin/', include(xadmin.site.urls)),
    # rest_framework 基本路由
    url(r'^(?P<version>(v1))/', include(v1.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # rest_framework docs 配置
    url(r'docs/', include_docs_urls(title="HotNest Docs")),
    # 自定已验证，使用redis 缓存 token，保证token唯一
    url(r'^(?P<version>(v1))/token_verify/$', ClassifyEmailTokenVerifyViewSet.as_view(), name="token_verify"),
    url(r'^(?P<version>(v1))/token-refresh/', refresh_jwt_token, name="token_refresh"),
    url(r'^(?P<version>(v1))/login/$', ClassifyEmailLoginViewSet.as_view(), name="login")

    # path('', include('apps.users.urls')),
]
