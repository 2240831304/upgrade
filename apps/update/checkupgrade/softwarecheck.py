
import urllib.parse
from django.db.models import Max


def checkUpdate(request,tableOperate):
    urlPath = request.get_full_path()
    print(urlPath)
    resultCode = "0"
    returnData = {
        "update":"0",
        "version":"",
        "url":"",
        "md5":"",
        "content":""
    }

    try:
        urlParse = urllib.parse.urlparse(request.get_full_path())
        queryData = urlParse.query
        list_query = urllib.parse.parse_qsl(queryData)
        dictData = dict(list_query)
    except:
        resultCode = "1"
        return resultCode,returnData

    try:
        machineType = dictData["serial"]
    except:
        resultCode = "2"
        return resultCode, returnData

    if machineType == "":
        resultCode = "2"
        return resultCode, returnData

    try:
        machineVersion = dictData["version"]
    except:
        resultCode = "3"
        return resultCode, returnData

    if machineVersion == "":
        resultCode = "3"
        return resultCode, returnData
    #print(machineType,machineVersion)

    machineType = "86m"

    try:
        recentlyDate = tableOperate.objects.filter(device=machineType).aggregate(latelyTime=Max('pubdate'))
        #print(recentlyDate['latelyTime'])
        deviceVersion = tableOperate.objects.values("version","md5","updateContent","url").\
            filter(device=machineType,pubdate=recentlyDate['latelyTime'])
        #print(deviceVersion)
    except:
        resultCode = "4"
        return resultCode, returnData

    if len(deviceVersion) == 0:
        resultCode = "0"
        return resultCode, returnData

    VersionData = deviceVersion[0]
    newestVersion = VersionData["version"]
    #print(machineVersion,newestVersion)

    if newestVersion > machineVersion :
        returnData["update"] = "1"
        returnData["version"] = VersionData["version"]
        returnData["url"] = VersionData["url"]
        returnData["md5"] = VersionData["md5"]
        returnData["content"] = VersionData["updateContent"]
    else:
        returnData["update"] = "0"

    return resultCode, returnData