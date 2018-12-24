import logging

from django.shortcuts import render, redirect, reverse
from django.http.response import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from constants import SESSION_EXPIRE_TIME

from ota.response_code import CODE

logger = logging.getLogger('ota')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('pack:index')
        return render(request, 'login.html')

    def post(self, request):
        # 获取数据
        username = request.POST.get('username')
        password = request.POST.get('passwd')

        # 设置session过期时间
        request.session.set_expiry(SESSION_EXPIRE_TIME)

        # 校检参数完整性
        if not all([username, password]):
            context = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整",
            }
            return JsonResponse(context)

        user = authenticate(username=username, password=password)

        if user is not None:  # 用户名密码正确
            context = {
                "code": CODE.OK,
                "msg": "success",
                "data": {
                    "to_url": '/pack/index'
                }
            }
            login(request, user)
            response = JsonResponse(context)
            return response
        else:
            context = {
                "code": CODE.VERIFICATIONERR,
                "msg": "用户名或密码错误",
            }
            return JsonResponse(context)


class LogoutView(View):
    """
    登出
    """
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return redirect(reverse("userview:login"))



