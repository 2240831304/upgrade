

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
from update.models import upgradetest

def insertTestData():
    print("update test insert software upgrade information")
    object = upgradetest()
    object.device = "86m"
    object.version = "3.0"
    object.md5 = "dddddd2333333333333ddddddddd"
    object.updateContent = "和年度黑得很不愿无为i和i看i相似性你相似"
    object.url = "http://upgrade.obook.com.cn:8080/android/update?serial=86m2019&version=1.12.1"
    object.save()


def requestTest():
    print("update test updatereqtest this is test!!!")
    url = "http://upgrade.obook.com.cn:9000/android/update?serial=OF88A202006&version=0.1"
    header = {'action':'softwareupgrade'}
    req = requests.get(url=url,headers=header)
    print(req.headers)
    print(req.content)
    data = req.content
    #tempData = data.decode("GBK")
    #print(tempData)


def comparestr():
    machineVersion = "1.2.3"
    newestVersion = "1.2"
    if newestVersion > machineVersion :
        print("4444444444444444")
    else:
        print("555555555555555555")


if __name__ == '__main__':

    if False:
        comparestr()

    if True :
        requestTest()

    if False:
        insertTestData()




