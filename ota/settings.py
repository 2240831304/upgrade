"""
Django settings for ota project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-yf$^=jtt+-nc&tq1(ezz&we7c@a9@c@__7fds%#z2&-zhl37s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'faq.apps.FaqConfig',
    'package.apps.PackageConfig',
    'user.apps.UserConfig',
    'general_user.apps.GeneralUserConfig',
    "update.apps.UpdateConfig",
    'tinymce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ota.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'ota.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'upandroid',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'wechat',
        'PASSWORD': 'wechat2018@)!*',
    }
}

# 设置数据库的路由规则方法
DATABASE_ROUTERS = ['ota.database_router.DatabaseAppsRouter']

# 设置数据库和app的对应关系
DATABASE_APPS_MAPPING = {
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# 设置静态文件存放的物理目录
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATC_ROOT = os.path.join(BASE_DIR, 'static')


# 日志配置
LOGGING = {
    'version': 1,
    # 是否要禁用其他的日志功能，False表示不禁用
    'disable_existing_loggers': False,
    # 日志输出时的格式
    'formatters': {
        # 详细
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(lineno)d [%(process)d %(thread)d] %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        # 简单
        'simple': {
            'format': '%(levelname)s %(pathname)s [%(module)s %(lineno)d] %(message)s'
        },
    },
    # 日志过滤器
    'filters': {
        # 当setttings.debug为true时才启用
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 日志处理方式
    'handlers': {
        # 终端
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 文件
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "utils/logs/package.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,  # 按大小轮转
            'backupCount': 10,
            'formatter': 'verbose'
        },
        # 'file': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.TimedRotatingFileHandler',
        #     'filename': os.path.join(BASE_DIR, "utils/logs/yuewen.log"),  # 日志文件的位置
        #     'when': 'D',  # 按时间轮转,每天生成一个日志文件
        #     'interval': 1,
        #     'backupCount': 100,
        #     'formatter': 'verbose'
        # },
    },
    # 日志器[处理日志的对象配置]
    'loggers': {
        'ota': {  # 定义了一个名为ota的日志器
            'handlers': ['console', 'file'],
            # 是否要把当前日志向上一级传递
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    }
}

# 指定用户认证模型类
AUTH_USER_MODEL = 'user.User'

LOGIN_URL = '/user/login'


# oss子用户配置
ACCESS_KEY_ID = 'LTAI4qCrfAcJ56gg'
ACCESS_KEY_SECRET = 'PSHYEjut4Lr2HiGngiOwgdV3tfVVVR'
END_POINT = "oss-cn-shenzhen.aliyuncs.com"
PREFIX_URL = 'http://'
BUCKET_NAME = "szpackages"
DOWNLOAD_URL_PRE = 'http://pack.obook.com.cn/'
# 操作日志记录目录,已项目文件夹开始(ota)为根目录
LOG_FILE_PATH = "utils/logs/oss.log"
# 测试人员使用
TEST_OBJECT_KEY = 'szdownloadtest/'

# 用户使用
OBJECT_KEY = 'szdownload/'


# media目录配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# 使用富文本编辑器配置
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}