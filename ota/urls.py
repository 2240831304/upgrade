"""ota URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from package.views import get_package_test, upload_pack, upload_pack_test
from general_user.views import get_package


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls', namespace='userview')),
    path('pack/', include('package.urls', namespace='pack')),
    path('faq/', include('faq.urls', namespace='faq')),
    path('tinymce/', include('tinymce.urls')),
    path('pack_test', get_package_test),
    path('pack', get_package),
    # 将原有的包文件同步到oss中
    path('upload_pack', upload_pack),
    path('upload_pack_test', upload_pack_test),
    # 任何其他路径都访问登录页面
    path('', include('user.urls')),
]
