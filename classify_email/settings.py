"""
Django settings for classify_email project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import datetime
import os
import sys

import djcelery

from config.private import *

djcelery.setup_loader()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
# 加载 所有 app 目录
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# 加载 测试 extra_apps 目录
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=uwvetsgcyqynw2a5csiwym*yi1@u&w11v8my9msg0x+%h_s$9'

# SECURITY WARNING: don't run with debug turned on in production!
# debug 模式，上线时关了
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
AUTH_USER_MODEL = 'users.UserProfile'
# 自定义用户验证
AUTHENTICATION_BACKENDS = (
    'users.my_backend.CustomBackend',
)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ⽤户权限处理 依赖的应⽤
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 下面注册的均为插件注册
    # 注册跨越问题的应用
    'corsheaders',
    # rest_framework 注册
    'rest_framework',
    # # xadmin 注册
    # 'xadmin',
    # 'crispy_forms',
    # 'reversion',
    # 下面注册的均为自定义app注册
    # 用户信息注册
    'users.apps.UsersConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 会话⽀持中间件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 认证⽀持中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 跨越问题的中间件
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'classify_email.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 添加模板文件夹路径
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'classify_email.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# 配置 REDIS 缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': NAME,
        'USER': USER,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': PORT,
        'OPTIONS': {
            'autocommit': True,
            "init_command": "SET foreign_key_checks = 0;",
            'charset': 'utf8mb4'
        }
    }
}
# 配置 REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # 验证是否登陆
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 返回数据校验 和 数据结构配置
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 自定义校验
        'utils.jwt_auth.ClassifyEmailJsonTokenAuthentication',
    ),
    # rest_framework 翻页配置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    # 版本配置
    "DEFAULT_VERSION": "v1",
    'VERSION_PARAM': 'version',
    'ALLOWED_VERSIONS': ['v1'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

}

JWT_AUTH = {
    # 有效期设置
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
    'JWT_RESPONSE_PAYLOAD_ERROR_HANDLER': 'users.utils.jwt_response_payload_error_handler',
}
# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True
# 世界时间设置
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# 设置跨域

# # CORS 设置跨域域名 白名单
# CORS_ORIGIN_WHITELIST = (
#     '127.0.0.1:8080',
#     'localhost:8080',
# )
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie
# 前端需要携带cookies访问后端时,需要设置
withCredentials = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ('DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'VIEW',)
CORS_ALLOW_HEADERS = ('x-requested-with', 'content-type', 'accept', 'origin', 'authorization', 'x-csrftoken')
STATIC_URL = '/static/'
# 媒体文件存储路径
MEDIA_ROOT = os.path.join(BASE_DIR, "files")
MEDIA_URL = "/files/"
CELERY_BEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
BROKER_URL = BROKER_URL
REDIS_TOKEN_SUFFIX = "-token"
# 上传文件大小，改成20M
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
# TEST_URL = "http://"
# PRO_URL = "http://"

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

# # todo 静态文件存储路径 ,在写完log日志配置后报错，没有查到原因
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
# ]

# 定义上传文件夹的路径
UPLOAD_ROOT = os.path.join(BASE_DIR, 'static/upload')
# 邮件 发送配置
EMAIL_HOST = "smtp.mxhichina.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = "duxiansh300@qq.com"
EMAIL_HOST_PASSWORD = EMAIL_PASSWORD
# EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_FROM = "XianSheng Du 300 <duxiansh300@qq.com>"
DEFAULT_FROM_EMAIL = EMAIL_FROM
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
ANALYZEBANNER_DIRS = os.path.join(BASE_DIR, 'static/analyzebanner')
CHANNEL_PPT_DIRS = os.path.join(BASE_DIR, 'static/channel_ppt')
LOGGING_DIR = os.path.join(BASE_DIR, 'log')

# 翻页设置
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 20,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}

# log日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d][%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
        },

        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d][%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
        }

    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/classify_email.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'error': {
        'level': 'ERROR',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs/error_classify_email.log'),
        'maxBytes': 1024 * 1024 * 5,
        'backupCount': 5,
        'formatter': 'standard',
    },
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'standard'
    },
    'loggers': {
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}
