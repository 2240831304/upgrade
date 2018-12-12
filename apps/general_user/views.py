from django.shortcuts import render
from general_user.models import RVersion, Package
from utils.func import get_pack


# 用户使用返回升级包信息
def get_package(request):
    return get_pack(request, False, RVersion, Package)

