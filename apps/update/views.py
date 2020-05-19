
from django.shortcuts import render
from update.checkupgrade import softwarecheck
from django.http import HttpResponse
import json


def serverTest(request):
    print("update views serverTest!!!!!!!!!!!!")
    return render(request, 'uphtml/test.html')



def CheckVersion(request):
    print("apps update views.py checkversion!!!")

    resultCode = '0'
    returnData = ''

    if request.method == 'GET':
        requestAction = request.META.get('HTTP_ACTION', '')

        if requestAction == "softwareupgrade":
            resultCode,returnData = softwarecheck.checkUpdate(request)


        response = HttpResponse()
        response.setdefault('result-code', resultCode)
        response.content_type = 'application/json'
        response.content = json.dumps(returnData)

        return response
