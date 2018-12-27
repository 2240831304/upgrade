import re
import hashlib
import logging

from django.shortcuts import render

from ota.response_code import RET
from package.sql import test_newest_rv
from general_user.sql import newest_rv


logger = logging.getLogger('ota')


def _upgrade_version(cu_version, reader_id, p_rv_obj, RVersion):
    depend_version = p_rv_obj.depend_version

    # 检验最新版本是否有依赖版本
    if depend_version not in ('0', None):
        if fill_version(cu_version) < fill_version(depend_version):  # 比依赖版本小
            rv_obj = RVersion.objects.filter(reader_id=reader_id, version=depend_version).first()
            return _upgrade_version(cu_version, reader_id, rv_obj, RVersion)
    return p_rv_obj


def get_pack(request, is_test, RVersion, Package):
    version = request.GET.get('version', '')
    model = request.GET.get('model', '')
    # accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING')
    action = request.META.get("HTTP_ACTION")
    device = request.META.get("HTTP_DEVICE")
    version = version.strip("V")

    # 校验参数
    # if accept_encoding.strip() != "":
    #     response = render(request, 'xml/default.xml', content_type="application/xml")
    #     response['result-code'] = RET.ENCODINGERR
    #     return response

    if action != 'getReaderPackage':
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.ACTIONERR
        return response

    if not device:
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.DEVICEERR
        return response

    if not version:
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.VERSIONERR
        return response

    if not model:
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.MODELERR
        return response

    # 获取硬件版本对应的pid
    pid = Package.objects.filter(model=model, state=0).first().pid

    if not pid:  # 没有当前硬件版本
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.MODELERR
        return response

    # 阅读器版本id
    rv_id = pid
    # 阅读器号
    reader_id = RVersion.objects.filter(id=rv_id).first().reader_id

    # 获取当前阅读器版本对应阅读器号的最新版本对象
    if is_test:
        max_obj = RVersion.objects.raw(test_newest_rv, [reader_id])[0]
    else:
        max_obj = RVersion.objects.raw(newest_rv, [reader_id])[0]

    if not max_obj:  # 没有最大版本
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.MODELERR
        return response

    # 返回要升级的版本
    up_obj = _upgrade_version(version, reader_id, max_obj, RVersion)

    # 获取要升级版本的基础版本号
    base_version = re.search(r'(\d+?)\.', version).group(1) + '.0'

    # 过滤富文本html标签
    description = up_obj.description
    if "<" in description:
        pattern = re.compile('>(.*?)<')
        # 取html标签中的数据
        des = pattern.findall(description)
        # 去除列表空字符串
        des = filter(None, des)
        # 拼接
        description = "&lt;br&gt;".join(des)

    pack_obj = Package.objects.filter(base_version=base_version, model=model).first()

    context = {
        "title": up_obj.title,
        "description": description,
        "version": up_obj.version,
        "pack": pack_obj.pack,
        "md5": pack_obj.md5,
    }

    response = render(request, 'xml/upgrade.xml', context=context, content_type="application/xml")
    response['result-code'] = RET.OK
    return response


def file_md5(file_con):
    '''返回文件md5值'''
    md5_obj = hashlib.md5()
    for data in file_con:
        md5_obj.update(data)
    ret = md5_obj.hexdigest()
    return ret


def fill_version(version):
    split_list = version.split('.')
    if len(split_list) == 2:
        split_list.append("0")
    fill_str = '{0:0>5}{1:0>5}{2:0>5}'.format(*split_list)
    return fill_str


def fill_package(base_version):
    split_list = base_version.split('.')
    fill_str = '{0:0>5}{1:0>5}'.format(*split_list)
    return fill_str























