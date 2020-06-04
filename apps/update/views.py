
from django.shortcuts import render, redirect, reverse
from update.checkupgrade import softwarecheck
from django.http import HttpResponse
import json
from update.models import softwarepackage,upgradetest
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import JsonResponse
import os
import urllib.parse
from django.http import FileResponse
import hashlib


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


def HandlePublishNewsTest(request):
    InsertPublishData(request,upgradetest)
    context = {
        "code": "0",
        "msg": "success",
        "data": {
            "to_url": '/android/pushlishtest'
        }
    }
    response = JsonResponse(context)
    return response


def HandlePublishNews(request):
    InsertPublishData(request, softwarepackage)
    context = {
        "code": "0",
        "msg": "success",
        "data": {
            "to_url": '/android/publishversion'
        }
    }
    response = JsonResponse(context)
    return response



def InsertPublishData(request,tableoperate):
    pass



def HandlePackage(request):
    returncode = "0"
    msg = "success"
    context = {
        "returncode": returncode,
        "msg": msg,
        "to_url": '/android/pushlishtest'
    }

    #实现表单上传
    if request.method == "POST":
        devicetype = request.POST.get("device")
        #print(devicetype)
        if devicetype == "":
            context["returncode"] = "1"
            context["msg"] = "服务器获取不到设备类型,发布失败"
            response = JsonResponse(context)
            return response

        obj = request.FILES.get('packet')
        name = str(obj)
        #print(name)
        sysUserPath = os.path.expanduser('~')
        filename = sysUserPath + "/package"

        typetm = request.POST.get("type")
        if typetm == "test":
            filename = filename + "/test/" + name
        elif typetm == "official":
            filename = filename + "/official/" + name
            context["to_url"] = "/android/publishversion"

        #print(obj, filename)
        if os.path.exists(filename):
            os.remove(filename)

        fobj = open(filename, 'wb')
        for chrunk in obj.chunks():
            fobj.write(chrunk)
        fobj.close()

        uploadMd5 = request.POST.get("md5")
        localMd5 = hashlib.md5(open(filename,'rb').read()).hexdigest()
        #print(uploadMd5,localMd5)
        if uploadMd5 != localMd5 :
            context["returncode"] = "1"
            context["msg"] = "软件包上传失败,请检查MD5,重新发布"
            response = JsonResponse(context)
            return response

        returncodetm,msgtm = insertVersionData(request,name)
        context["returncode"] = returncodetm
        context["msg"] = msgtm
        response = JsonResponse(context)
        return response


    #文件下载
    if request.method == "GET":
        urlParse = urllib.parse.urlparse(request.get_full_path())
        filedir = urlParse.query

        sysUserPath = os.path.expanduser('~')
        filename = sysUserPath + "/package/" + filedir
        print(filename)

        file = open(filename, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;'
        return response



def insertVersionData(request,filename):
    returncode = "0"
    msg = "success"

    typetm = request.POST.get("type")
    devicetype = request.POST.get("device")
    versionnum = request.POST.get("version")
    md5 = request.POST.get("md5")
    content = request.POST.get("content")
    # print(request.path_info)
    # print(request.scheme)
    # print(request.get_host())

    url = request.scheme + "://" + request.get_host() + request.path_info + "?"
    #print(url)

    if typetm == "test":
        url = url + "test/" + filename
        #print(url)
        try:
            object = upgradetest()
            object.device = devicetype
            object.version = versionnum
            object.md5 = md5
            object.updateContent = content
            object.url = url
            object.save()
        except:
            returncode = "1"
            msg = "发布数据写入数据库出错,请重新发布"

    elif typetm == "official":
        url = url + "official/" + filename
        #print(url)
        try:
            object = softwarepackage()
            object.device = devicetype
            object.version = versionnum
            object.md5 = md5
            object.updateContent = content
            object.url = url
            object.save()
        except:
            returncode = "1"
            msg = "发布数据写入数据库出错,请重新发布"

    return returncode,msg


def VersionManageSys(request):
    print("apps update views.py VersionManageSys handle!")
    returndata = {
        "code":"0",
        "msg":"",
        "data":""
    }

    if request.method == "GET":
        typetm = request.GET.get("type")
        devicetype = request.GET.get("device")
        if (typetm == "") or (devicetype == ""):
            returndata["code"] = "1"
            returndata["msg"] = "服务器未获取到查询类型,请重新查询"
            response = JsonResponse(returndata)
            return response

        datalist = None
        if typetm == "test":
            try:
                datalist = upgradetest.objects.values("version","pubdate").filter(device=devicetype).order_by("-pubdate")
            except:
                returndata["code"] = "1"
                returndata["msg"] = "服务器查询数据库出现异常"
                response = JsonResponse(returndata)
                return response
        elif typetm == "official":
            try:
                datalist = softwarepackage.objects.values("version", "pubdate").filter(device=devicetype).order_by("-pubdate")
            except:
                returndata["code"] = "1"
                returndata["msg"] = "服务器查询数据库出现异常"
                response = JsonResponse(returndata)
                return response
        #print(datalist)
        if datalist :
            datatm = dataHandle(datalist,devicetype)
            returndata["code"] = "0"
            returndata["data"] = datatm
            response = JsonResponse(returndata)
            return response

        else:
            returndata["code"] = "0"
            returndata["msg"] = "此设备类型暂无发布版本"
            response = JsonResponse(returndata)
            return response


    if request.method == "POST":
        typetm = request.POST.get("type")
        devicetype = request.POST.get("device")
        deviceversion = request.POST.get("version")
        print(typetm,devicetype,deviceversion)
        if (typetm == "") or (devicetype == "") or (deviceversion == ""):
            returndata["code"] = "1"
            response = JsonResponse(returndata)
            return response

        if typetm == "test":
            try:
                upgradetest.objects.filter(device=devicetype,version=deviceversion).delete()
            except:
                returndata["code"] = "1"
                response = JsonResponse(returndata)
                return response
        elif typetm == "official":
            try:
                softwarepackage.objects.filter(device=devicetype,version=deviceversion).delete()
            except:
                returndata["code"] = "1"
                response = JsonResponse(returndata)
                return response

        response = JsonResponse(returndata)
        return response



def dataHandle(data,devicetype):
    datalist = []
    for value in data:
        dictdata = dict()
        dictdata["device"] = devicetype
        dictdata["version"] = value["version"]
        dictdata["publishtime"] = value["pubdate"]

        datalist.append(dictdata)

    return datalist