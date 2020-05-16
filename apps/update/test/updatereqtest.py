

import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(BASE_DIR)
print(BASE_DIR)
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ota.settings")
django.setup()

import requests
from update.models import softwarepackage

def insertTestData():
    print("update test insert software upgrade information")
    object = softwarepackage()
    object.device = "86m"
    object.version = "2.15"
    object.md5 = "dddddd2333333333333ddddddddd"
    object.updateContent = "和年度黑得很不愿无为i和i看i相似性你相似"
    object.url = "http://upgrade.obook.com.cn:8080/android/update?serial=86m2019&version=1.12"
    object.save()


def requestTest():
    print("update test updatereqtest this is test!!!")
    url = "http://upgrade.obook.com.cn:8080/android/update?serial=86m2019&version=1.12"
    header = {'action':'softwareupgrade'}
    req = requests.get(url=url,headers=header)
    print(req.headers)
    print(req.content)
    data = req.content
    #tempData = data.decode("GBK")
    #print(tempData)


if __name__ == '__main__':

    if True :
        requestTest()

    if False:
        insertTestData()




