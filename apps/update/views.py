
from django.shortcuts import render, redirect, reverse
from update.checkupgrade import softwarecheck
from django.http import HttpResponse
import json
from update.models import softwarepackage,upgradetest
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import JsonResponse


def serverTest(request):
    print("update views serverTest!!!!!!!!!!!!")
    return render(request, 'uphtml/test.html')


def upgradeTest(request):
    print("apps update views.py upgradeTest!!!")

    resultCode = '0'
    returnData = ''

    if request.method == 'GET':
        requestAction = request.META.get('HTTP_ACTION', '')

        if requestAction == "softwareupgrade":
            resultCode,returnData = softwarecheck.checkUpdate(request,upgradetest)


        response = HttpResponse()
        response.setdefault('result-code', resultCode)
        response.content_type = 'application/json'
        response.content = json.dumps(returnData)

        return response



def CheckVersion(request):
    print("apps update views.py checkversion!!!")

    resultCode = '0'
    returnData = ''

    if request.method == 'GET':
        requestAction = request.META.get('HTTP_ACTION', '')

        if requestAction == "softwareupgrade":
            resultCode,returnData = softwarecheck.checkUpdate(request,softwarepackage)


        response = HttpResponse()
        response.setdefault('result-code', resultCode)
        response.content_type = 'application/json'
        response.content = json.dumps(returnData)

        return response



class MainPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'mainpage.html')


class PushlisVersionTestView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_authenticated:
            #return redirect('update:pushlishtest')
            return render(request, 'publishtestpage.html')
        return render(request, 'login.html')


    def post(self, request):
        print("apps version update views PushlisVersionTestView !!!")
        context = {
            "code": "0",
            "msg": "success",
            "data": {
                "to_url": '/android/pushlishtest'
            }
        }
        response = JsonResponse(context)
        return response


class PublishVersionView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_authenticated:
            #return redirect('update:pushlishtest')
            return render(request, 'publishpage.html')
        return render(request, 'login.html')


    def post(self, request):
        context = {
            "code": "0",
            "msg": "success",
            "data": {
                "to_url": '/android/publishversion'
            }
        }
        response = JsonResponse(context)
        return response



class VersionManagerView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_authenticated:
            #return redirect('update:pushlishtest')
            return render(request, 'managepage.html')
        return render(request, 'login.html')


    def post(self, request):
        context = {
            "code": "0",
            "msg": "success",
            "data": {
                "to_url": '/android/managerversion'
            }
        }
        response = JsonResponse(context)
        return response