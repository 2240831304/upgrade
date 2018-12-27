import logging

from multiprocessing.dummy import Pool
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction

from ota.response_code import CODE
from package.models import Reader, RVersion, Package
from utils.common_func.package import file_md5, fill_version, fill_package
from utils.decorator import is_login
from utils.oss import LocalOSS
from package.constants import RV_STATE
from package.sql import *


logger = logging.getLogger("ota")


def get_update_versions(reader_id):
    # 返回对应阅读器号的所有已同步更新版本号

    version_list = []
    version_objs = RVersion.objects.raw(test_order_update_rv, [reader_id, RV_STATE['UPDATE']])
    for version_obj in version_objs:
        version_list.append([version_obj.id, version_obj.version])
    return version_list


class IndexView(View):
    @method_decorator(login_required)
    def get(self, request):

        # 获取所有未删除的阅读器号的最新版本对象
        rv_objs = RVersion.objects.raw(test_each_newest_rvs)

        rv_list = []
        # 构建数据
        for rv_obj in rv_objs:
            reader_name = Reader.objects.filter(id=rv_obj.reader_id).first().reader_name

            dic = {'reader_id': rv_obj.reader_id,
                   'reader_name': reader_name,
                   'version': rv_obj.version,
                   'title': rv_obj.title,
                   'description': rv_obj.description,
                   'id': rv_obj.id,
                   'state': rv_obj.state,
                   'update_time': rv_obj.update_time
                   }

            rv_list.append(dic)
        return render(request, 'index.html', {'rv_list': rv_list})


class ReadersView(View):
    @method_decorator(is_login)
    def get(self, request):
        '''返回所有的阅读器号'''
        reader_list = []
        readers = Reader.objects.all()
        for i in readers:
            reader_list.append([i.id, i.reader_name])
        content = {
            "code": CODE.OK,
            "msg": 'success',
            "data": {
                "readers": reader_list
            }
        }
        return JsonResponse(content)

    @method_decorator(is_login)
    def post(self, request):
        '''添加阅读器号'''

        # 1、获取数据
        reader_name = request.POST.get('reader_name')

        # 2、校检数据完整性
        if not all([reader_name]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整",
            }
            return JsonResponse(content)

        # 校检阅读器型号是否已存在
        reader = Reader.objects.filter(reader_name=reader_name)
        if reader.exists():
            content = {
                "code": CODE.PARAMERR,
                "msg": "添加的阅读器型号已存在",
            }
            return JsonResponse(content)

        # 3、添加
        try:
            reader = Reader()
            reader.reader_name = reader_name
            reader.save()
            reader.sort = reader.id
            reader.save()
        except Exception as e:
            logger.error("{}添加失败 detail:{}".format(reader_name, e))
            content = {
                "code": CODE.DBERR,
                "msg": "添加失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": "添加成功"
        }
        return JsonResponse(content)


class RVersionAddView(View):
    @method_decorator(is_login)
    def post(self, request):
        '''添加阅读器的新版本'''

        # 获取数据
        reader_id = request.POST.get('reader_id')
        version = request.POST.get('version')
        title = request.POST.get('title')
        description = request.POST.get('description')
        depend_version = request.POST.get('depend_version')

        # 校检数据完整性
        if not all([reader_id, version]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整"
            }
            return JsonResponse(content)

        # 校检阅读器号是否存在,避免发布不存在的阅读器号的版本
        # 获取当前阅读器号未删除的所有对象
        reader = Reader.objects.filter(id=reader_id).first()
        if not reader:  # 不存在阅读器号
            content = {
                "code": CODE.PARAMERR,
                "msg": '阅读器号不存在'
            }
            return JsonResponse(content)

        # 获取当前阅读器号对应的所有对象
        rversions = RVersion.objects.filter(reader_id=reader_id)
        if rversions.exists():
            # 校验阅读器号的当前版本是否存在，避免发布阅读器号已经存在的版本
            rv_obj = rversions.filter(version=version)
            if rv_obj.exists():  # 当前阅读器的当前版本已存在
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '当前阅读器号的当前版本已存在'
                }
                return JsonResponse(content)

            # 校验阅读器版本是否低于已发布的版本，只有高版本才能发布
            max_rv_obj = RVersion.objects.raw(test_newest_rv, [reader_id])[0]
            max_vcode = max_rv_obj.vcode

            # 当前版本小于最大版本
            if fill_version(version) < max_vcode:
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '最新发布的版本不能小于已发布的版本'
                }
                return JsonResponse(content)

            if max_rv_obj.state == RV_STATE['ADD']:  # 当前版本号大于已发布但是未同步更新的版本号
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '该阅读器号存在已发布未同步更新的版本'
                }
                return JsonResponse(content)

            # 将最新的版本的所有升级包信息加入到新建版本中,如果有依赖版本,就只添加大于等于依赖版本对应基础版本的升级包信息
            # 如果有依赖版本
            if depend_version not in ('0', None):
                depend_base_version = depend_version.split('.')[0]+'.0'
                pack_objs = Package.objects.raw(test_get_rv_gte_depend_package, [max_rv_obj.id, fill_package(depend_base_version)])
            else:
                pack_objs = Package.objects.filter(pid=max_rv_obj.id)
            try:
                new_rv_obj = RVersion()
                new_rv_obj.reader_id = reader_id
                new_rv_obj.version = version
                new_rv_obj.title = title
                new_rv_obj.description = description
                new_rv_obj.depend_version = depend_version
                new_rv_obj.sort = reader.sort
                new_rv_obj.save()
                for pack_obj in pack_objs:
                    new_pack_obj = Package()
                    new_pack_obj.base_version = pack_obj.base_version
                    new_pack_obj.model = pack_obj.model
                    new_pack_obj.pack = ''
                    new_pack_obj.md5 = ''
                    new_pack_obj.pid = new_rv_obj.id
                    new_pack_obj.state = pack_obj.state
                    new_pack_obj.save()
            except Exception as e:
                logger.error('{}{}发布失败,detail:{}'.format(reader_id, version, e))
                content = {
                    "code": CODE.DBERR,
                    "msg": "发布失败"
                }
                return JsonResponse(content)

        else:
            try:
                new_rv_obj = RVersion()
                new_rv_obj.reader_id = reader_id
                new_rv_obj.version = version
                new_rv_obj.title = title
                new_rv_obj.description = description
                new_rv_obj.depend_version = depend_version
                new_rv_obj.sort = reader.sort
                new_rv_obj.save()
            except Exception as e:
                logger.error('{}{}发布失败,detail:{}'.format(reader_id, version, e))
                content = {
                    "code": CODE.DBERR,
                    "msg": "发布失败"
                }
                return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": '发布成功'
        }

        return JsonResponse(content)


class RVersionEditView(View):
    @method_decorator(login_required)
    def get(self, request, rv_id):
        '''编辑页面'''
        # 获取数据
        rv_id = rv_id

        # 校检数据
        if not all([rv_id]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整"
            }
            return JsonResponse(content)

        # 当前阅读器对应的queryset对象
        rv_obj = RVersion.objects.filter(id=rv_id).first()
        reader_id = rv_obj.reader_id
        version_list = get_update_versions(reader_id)

        rv_obj.reader_name = Reader.objects.filter(id=reader_id).first().reader_name

        # 构造数据
        context = {
            'rv_obj': rv_obj,
            'versions': version_list
        }
        return render(request, 'rversion.html', context)

    @method_decorator(is_login)
    def put(self, request, rv_id):
        '''修改操作'''
        # 获取数据
        PUT = QueryDict(request.body)
        reader_id = PUT.get("reader_id")
        version = PUT.get("version")
        title = PUT.get('title')
        description = PUT.get('description')
        depend_version = PUT.get('depend_version')

        # 校检参数完整性
        if not all([reader_id, version]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整"
            }
            return JsonResponse(content)

        # 校验阅读器号的当前版本是否存在
        rv_obj = RVersion.objects.filter(id=rv_id).first()
        if not rv_obj:
            content = {
                "code": CODE.PARAMERR,
                "msg": '当前版本不存在'
            }
            return JsonResponse(content)

        # 校验当前提交版本是否低于已同步更新最高版本
        max_rv_obj = RVersion.objects.raw(test_order_update_rv, [reader_id, RV_STATE['UPDATE']])[0]
        max_vcode = max_rv_obj.vcode

        # 当前版本小于最大版本
        if fill_version(version) < max_vcode:
            content = {
                "code": CODE.PARAMERR,
                "msg": '发布版本不能小于已同步更新的版本'
            }
            return JsonResponse(content)

        try:
            rv_obj.version = version
            rv_obj.title = title
            rv_obj.description = description
            rv_obj.depend_version = depend_version
            rv_obj.save()
        except Exception as e:
            logger.error("{}{}修改失败 detail:{}".format(reader_id, version, e))
            content = {
                "code": CODE.PARAMERR,
                "msg": "修改失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": "修改成功",
            "data": {
                "to_url": "/pack/index"
            }
        }
        return JsonResponse(content)

    # 暂时用不到，后期可能用到
    # @method_decorator(is_login)
    # def delete(sel, request):
    #     '''删除当前阅读器的当前版本'''
    #     # 获取数据
    #     DELETE = QueryDict(request.body)
    #     rv_id = DELETE.get('rv_id')
    #
    #     # 校验数据
    #
    #     # 业务处理，将rversion的state变为1，同时所有的升级包的状态也变成1
    #
    #     content = {
    #         "code": CODE.OK,
    #         "msg": "修改成功"
    #     }
    #     return JsonResponse(content)


class ReaderVersionsView(View):
    '''返回当前阅读器所有的已同步更新的版本号'''
    @method_decorator(is_login)
    def get(self, request, reader_id):
        # 校检数据
        if not all([reader_id]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "缺少参数",
            }
            return JsonResponse(content)

        version_list = get_update_versions(reader_id)
        content = {
            "code": CODE.OK,
            "msg": "success",
            "data": {
                "versions": version_list,
            }
        }
        return JsonResponse(content)


# 同步更新
class RVersionStateView(View):
    @method_decorator(is_login, transaction.atomic)
    def put(self, request):
        '''
        点击同步更新后的操作
        '''
        # 1、获取数据
        PUT = QueryDict(request.body)
        rv_id = PUT.get('rv_id')

        # 2、校检数据完整性
        if not all([rv_id]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "参数不完整",
            }
            return JsonResponse(content)

        # 3、业务逻辑处理
        try:

            rv_obj = RVersion.objects.get(id=rv_id)
            rv_obj.state = RV_STATE['UPDATE']
            pack_objs = Package.objects.filter(pid=rv_id)

            # 修改用户数据库数据
            with transaction.atomic():
                sp1 = transaction.savepoint()
                try:
                    RVersion.objects.create(
                        reader_id=rv_obj.reader_id,
                        version=rv_obj.version,
                        title=rv_obj.title,
                        description=rv_obj.description,
                        state=RV_STATE['UPDATE'],
                        depend_version=rv_obj.depend_version,
                        sort=rv_obj.sort,
                    )
                except Exception as e:
                    transaction.savepoint_rollback(sp1)
                    raise e

                # 获取用户数据库中阅读器当前版本的id
                pid = RVersion.objects.filter(reader_id=rv_obj.reader_id, version=rv_obj.version).first().id
                for pack_obj in pack_objs:

                    try:
                        test_pack_name = urlsplit(pack_obj.pack).path[1:]
                        test_md5_name = urlsplit(pack_obj.md5).path[1:]

                        # 将object_key替换
                        pack_name = test_pack_name.replace(settings.TEST_OBJECT_KEY, settings.OBJECT_KEY)
                        md5_name = test_md5_name.replace(settings.TEST_OBJECT_KEY, settings.OBJECT_KEY)

                        Package.objects.create(
                            base_version=pack_obj.base_version,
                            model=pack_obj.model,
                            pack=settings.DOWNLOAD_URL_PRE + pack_name,
                            md5=settings.DOWNLOAD_URL_PRE + md5_name,
                            pid=pid
                        )

                        # 将测试包拷贝到用户包存储路径
                        oss_obj = LocalOSS(settings.BUCKET_NAME)
                        oss_obj.copy_object(settings.BUCKET_NAME, test_pack_name, pack_name)
                        oss_obj.copy_object(settings.BUCKET_NAME, test_md5_name, md5_name)
                    except Exception as e:
                        transaction.savepoint_rollback(sp1)
                        raise e

            rv_obj.save()
        except Exception as e:
            logger.error('{}阅读器版本同步更新失败, detail:{}'.format(rv_id,e))
            content = {
                "code": CODE.DBERR,
                "msg": "同步更新失败"
            }
            return JsonResponse(content)
        # 4、修改成功返回数据
        content = {
            "code": CODE.OK,
            "msg": "修改成功"
        }

        return JsonResponse(content)


class ReaderRVersionsView(View):
    @method_decorator(login_required)
    def get(self, request, reader_id):
        '''返回当前阅读器所有的已同步更新的所有版本的所有信息'''
        rversions = RVersion.objects.filter(reader_id=reader_id, state=RV_STATE['UPDATE']).order_by('update_time')

        context = {
            "rversions": rversions
        }

        return render(request, 'history.html', context)


class PackagesView(View):
    @method_decorator(login_required)
    def get(self, request, pid):
        '''返回当前阅读器当前版本的所有升级包展示界面'''

        # 获取对应阅读器版本的未删除的所有升级包
        pack_objs = Package.objects.raw(test_get_rv_packages_not_delete, [pid, RV_STATE['DELETE']])
        context = {
            'pid': pid,
            'pack_objs': pack_objs
        }

        return render(request, 'packages.html', context)


class PackageAddView(View):
    @method_decorator(login_required)
    def get(self, request, pid):
        '''点击添加时，返回添加页面'''
        context = {
            'pid': pid,
        }
        return render(request, 'packadd.html', context)

    @method_decorator(is_login)
    def post(self, request, pid):
        '''添加页面点击提交时处理'''
        # 获取数据
        pid = request.POST.get('pid')
        base_version = request.POST.get('base_version')
        model = request.POST.get('model')
        pack_con = request.FILES.get('pack_con')
        md5_con = request.FILES.get('md5_con')

        # 校验数据完整性
        if not all([base_version, model]):
            content = {
                "code": CODE.PARAMERR,
                "msg": '缺少参数'
            }
            return JsonResponse(content)

        # 获取当前pid对应的未删除的所有包
        packages = Package.objects.filter(pid=pid, state=RV_STATE['ADD'])

        # 判断当前基础版本的硬件版本是否存在
        pack_obj = packages.filter(base_version=base_version, model=model)
        if pack_obj.exists():
            content = {
                "code": CODE.PARAMERR,
                "msg": "当前基础版本的当前硬件版本已经存在"
            }
            return JsonResponse(content)

        # 判断用户是否上传了有效文件
        if not all([pack_con, md5_con]):
            pack_url = ''
            md5_url = ''
        else:
            pack_name = settings.TEST_OBJECT_KEY + base_version + model + pid + '.img'
            md5_name = settings.TEST_OBJECT_KEY + base_version + model + pid + '.img.md5'

            # 校验md5值
            right_md5 = ''
            for con in md5_con.chunks():
                try:
                    right_md5 = con.decode()
                except Exception as e:
                    logger.error("md5文件上传错误, detail:{}".format(e))
                    content = {
                        "code": CODE.PARAMERR,
                        "msg": "md5值校验失败"
                    }
                    return JsonResponse(content)

            check_md5 = file_md5(pack_con.chunks())

            if not (right_md5 == check_md5):
                content = {
                    "code": CODE.PARAMERR,
                    "msg": "md5值校验失败"
                }
                return JsonResponse(content)

            # 上传文件，保存数据库信息
            oss_obj = LocalOSS(settings.BUCKET_NAME)
            try:
                pack_url = oss_obj.put_object(pack_name, pack_con.chunks())
                md5_url = oss_obj.put_object(md5_name, md5_con.chunks())
            except Exception as e:
                logger.error(e)
                content = {
                    "code": CODE.THIRDERR,
                    "msg": "上传文件出错"
                }
                return JsonResponse(content)

            if not pack_url:
                logger.error("上传文件{}出错".format(pack_con.name))
                content = {
                    "code": CODE.THIRDERR,
                    "msg": "上传文件错误".format(pack_con.name)
                }
                return JsonResponse(content)

            if not md5_url:
                logger.error("上传文件{}出错".format(md5_con.name))
                content = {
                    "code": CODE.THIRDERR,
                    "msg": "上传文件{}错误".format(md5_con.name)
                }
                return JsonResponse(content)

        # 保存数据库信息
        try:
            Package.objects.create(pid=pid, base_version=base_version, model=model, pack=pack_url, md5=md5_url)
        except Exception as e:
            logger.error('保存失败 detail：{}'.format(e))
            content = {
                "code": CODE.DBERR,
                "msg": '上传失败'
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": '上传成功'
        }
        return JsonResponse(content)


class PackageEditView(View):
    @method_decorator(login_required)
    def get(self, request, pid, pack_id):
        '''点击编辑按钮跳转页面'''
        pack_obj = Package.objects.filter(id=pack_id).first()

        context = {
            "pack_obj": pack_obj,
        }

        return render(request, 'packedit.html', context)

    @method_decorator(is_login)
    def post(self, request, pid, pack_id):
        '''编辑后提交'''
        # 获取数据
        pid = pid
        pack_id = pack_id
        base_version = request.POST.get('base_version')
        model = request.POST.get('model')
        pack_con = request.FILES.get('pack_con')
        md5_con = request.FILES.get('md5_con')

        # 校验数据完整性
        if not all([base_version, model]):
            content = {
                "code": CODE.PARAMERR,
                "msg": '缺少参数'
            }
            return JsonResponse(content)

        # 获取当前pack_id对应的对象
        package = Package.objects.filter(id=pack_id).first()

        old_pack = package.pack
        old_md5 = package.md5
        old_pack_name = urlsplit(old_pack).path[1:]
        old_md5_name = urlsplit(old_md5).path[1:]

        if all([pack_con, md5_con]):
            # 校验md5值
            right_md5 = ''
            for con in md5_con.chunks():
                try:
                    right_md5 = con.decode()
                except Exception as e:
                    logger.error("md5文件上传错误, detail:{}".format(e))
                    content = {
                        "code": CODE.PARAMERR,
                        "msg": "md5值校验失败"
                    }
                    return JsonResponse(content)

            check_md5 = file_md5(pack_con.chunks())

            if not (right_md5 == check_md5):
                content = {
                    "code": CODE.PARAMERR,
                    "msg": "md5值校验失败"
                }
                return JsonResponse(content)

        # 生成oss对象
        oss_obj = LocalOSS(settings.BUCKET_NAME)

        # 生成新文件名
        new_pack_name = settings.TEST_OBJECT_KEY + base_version + model + pid + '.img'
        new_md5_name = settings.TEST_OBJECT_KEY + base_version + model + pid + '.img.md5'

        if (package.base_version + package.model) != (base_version + model):  # 修改文件名
            if (not pack_con) and (not md5_con):  # 未修改文件
                # 重命名文件
                try:
                    new_pack_url = oss_obj.rename_object(settings.BUCKET_NAME, old_pack_name, new_pack_name)
                    new_md5_url = oss_obj.rename_object(settings.BUCKET_NAME, old_md5_name, new_md5_name)
                except Exception as e:
                    logger.error("拷贝对象失败 detail:{}".format(e))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                if not (new_pack_url and new_md5_url):  # 包为空
                    content = {
                        "code": CODE.OK,
                        "msg": '操作成功',
                        "data": {
                            "to_url": '/pack/pid_' + pid + '/packages'
                        }
                    }
                    return JsonResponse(content)
                # 更新数据库

            else:  # 修改了文件
                # 删除之前的pack
                try:
                    del_pack_res = oss_obj.del_object(old_pack_name)
                    del_md5_res = oss_obj.del_object(old_md5_name)
                except Exception as e:
                    logger.error("删除对象失败 detail:{}".format(e))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                if not (del_pack_res and del_md5_res):
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                # 保存新的包文件
                try:
                    new_pack_url = oss_obj.put_object(new_pack_name, pack_con.chunks())
                    new_md5_url = oss_obj.put_object(new_md5_name, md5_con.chunks())
                except Exception as e:
                    logger.error("上传文件失败 detail:{}".format(e))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)
                # 更新数据库
        else:  # 不修改文件名
            if (not pack_con) and (not md5_con):  # 未修改文件
                new_pack_url = old_pack
                new_md5_url = old_md5
            else:  # 修改了文件
                # 删除之前的pack
                try:
                    del_pack_res = oss_obj.del_object(old_pack_name)
                    del_md5_res = oss_obj.del_object(old_md5_name)
                except Exception as e:
                    logger.error("删除对象失败 detail:{}".format(e))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                if not (del_pack_res and del_md5_res):
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                # 保存新的包文件
                try:
                    new_pack_url = oss_obj.put_object(new_pack_name, pack_con.chunks())
                    new_md5_url = oss_obj.put_object(new_md5_name, md5_con.chunks())
                except Exception as e:
                    logger.error("上传文件失败 detail:{}".format(e))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)
                # 保存数据库信息

        # 保存数据库信息
        try:
            package.base_version = base_version
            package.model = model
            package.pack = new_pack_url
            package.md5 = new_md5_url
            package.save()
        except Exception as e:
            logger.error('保存失败 detail：{}'.format(e))
            content = {
                "code": CODE.DBERR,
                "msg": '文件上传失败'
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": '操作成功',
            "data": {
                "to_url": '/pack/pid_' + pid + '/packages'
            }
        }
        return JsonResponse(content)

    @method_decorator(is_login)
    def delete(self, request, pid, pack_id):
        pack_id = pack_id

        # 校检pack_id是否存在
        pack = Package.objects.filter(id=pack_id).first()
        if not pack:
            content = {
                "code": CODE.REQERR,
                "msg": "非法请求",
            }
            return JsonResponse(content)

        # 修改包状态
        try:
            pack.state = RV_STATE['DELETE']
            pack.save()
        except Exception as e:
            logger.error("packid_{}删除失败，detail：{}".format(pack_id, e))
            content = {
                "code": CODE.DBERR,
                "msg": "删除失败"
            }
            return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": "删除成功"
        }
        return JsonResponse(content)


class PackagesInfoView(View):
    @method_decorator(is_login)
    def get(self, request):
        '''返回当前阅读器当前版本的所有升级包信息'''
        rv_id = request.GET.get('rv_id')

        # 获取对应阅读器版本的未删除的所有升级包
        pack_objs = Package.objects.raw(test_get_rv_packages_not_delete, [rv_id, RV_STATE['DELETE']])

        content = {
            "code": CODE.OK,
            "msg": 'success',
            "data": []
        }

        for pack_obj in pack_objs:
            content["data"].append({
                "base_version": pack_obj.base_version,
                "model": pack_obj.model,
                "pack": pack_obj.pack,
                "md5": pack_obj.md5
            })

        return JsonResponse(content)



'''
没有model时返回一个特定型号
没有version，没有model和当前版本，没有action 返回xml头
没有device、没有accptencodig、三个头都没有、参数都没用 返回空文件
对device不做校验 但是不为空，修改返回正确的
action要做校验, 修改返回xml头
accptencoding 修改后返回空文件

返回最高的版本信息
根据状态码来返回正常返回0 result-code: 1001
'''
from utils.common_func.package import get_pack


# 测试人员使用,返回升级包信息
def get_package_test(request):
    return get_pack(request, True, RVersion, Package)


# 上传升级包
def _upload_pack(pack_obj, oss_obj, url, is_pack=True):
    obj_name = urlsplit(url).path[1:]
    try:
        obj_exists = oss_obj.obj_exists(obj_name)
    except Exception as e:
        logger.error("oss error detail{}".format(e))
        return False
    if obj_exists:
        logger.debug("{} is exists".format(obj_name))
        try:
            if is_pack:
                pack_obj.pack = settings.DOWNLOAD_URL_PRE + obj_name
            else:
                pack_obj.md5 = settings.DOWNLOAD_URL_PRE + obj_name
            pack_obj.save()
            logger.debug("{}修改完成".format(obj_name))
            return True
        except Exception as e:
            logger.error("修改域名失败 detail{}".format(e))
            return False

    obj_res = requests.get(url)
    logger.debug("{}下载完成".format(obj_name))

    result = oss_obj.put_object(obj_name, obj_res.content)
    if not result:
        logger.error("{}上传失败".format(obj_name))
        return False
    logger.debug("{}上传完成".format(obj_name))
    try:
        if is_pack:
            pack_obj.pack = settings.DOWNLOAD_URL_PRE + obj_name
        else:
            pack_obj.md5 = settings.DOWNLOAD_URL_PRE + obj_name
        pack_obj.save()
        logger.debug("{}修改完成".format(obj_name))
    except Exception as e:
        logger.error("修改域名失败 detail{}".format(e))
        return False
    return True


# 上传原有升级包到oss
def _upload(pack_obj):
    pack = pack_obj.pack
    md5 = pack_obj.md5

    if not (pack or md5):
        logger.debug("没有包")
        return
    # 上传文件到oss
    oss_obj = LocalOSS(settings.BUCKET_NAME)
    res_pack = _upload_pack(pack_obj, oss_obj, pack, is_pack=True)
    if not res_pack:
        return
    res_md5 = _upload_pack(pack_obj, oss_obj, md5, is_pack=False)
    if not res_md5:
        return
    return


def upload_pack(request):
    from general_user.models import Package
    pack_objs = Package.objects.all()

    pool = Pool(5)

    result = pool.map(_upload, pack_objs)
    pool.close()
    pool.join()
    return JsonResponse({"code": CODE.OK, "msg": "修改成功"})


def upload_pack_test(request):
    pack_objs = Package.objects.all()
    pool = Pool(5)

    result = pool.map(_upload, pack_objs)

    pool.close()
    pool.join()
    return JsonResponse({"code": CODE.OK, "msg": "修改成功"})




