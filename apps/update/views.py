
from django.shortcuts import render


def updateTest(request):
    print("update views updateTest!!!!!!!!!!!!")
    return render(request, 'uphtml/test.html')

