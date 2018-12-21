import logging
import os
import uuid
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

from ota.response_code import CODE
from package.models import Reader, RVersion, Package
from package.signals.signals import sync_update_signal
from utils.common_func.package import file_md5
from utils.decorator import is_login
from utils.oss import LocalOSS

logger = logging.getLogger("ota")

# 判断是否上传测试数据库升级包
IS_TEST = False

STATE = {
    'ADD': 0,
    'DELETE': 1,
    'UPDATE': 2,
}


def get_update_versions(reader_id):
    # 返回对应阅读器号的所有已同步更新版本号
    version_list = []
    version_objs = RVersion.objects.filter(reader_id=reader_id, state=STATE['UPDATE']).order_by('version')
    for version_obj in version_objs:
        version_list.append([version_obj.id, version_obj.version])
    return version_list


class IndexView(View):
    @method_decorator(login_required)
    def get(self, request):

        # 获取所有未删除的阅读器号的最新版本对象
        rv_objs = RVersion.objects.raw('select * from rversion '
                                       'inner join (select reader_id,max(version) as max_v from rversion group by reader_id) as max_v_reader '
                                       'on rversion.reader_id = max_v_reader.reader_id and rversion.version = max_v_reader.max_v '
                                       'order by rversion.update_time desc;')

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

        # 校检阅读器号是否存在,避免发布不存在的阅读器号
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
            max_obj = rversions.order_by('-version').first()
            max_version = max_obj.version

            if version < max_version:
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '最新发布的版本不能小于已发布的版本'
                }
                return JsonResponse(content)

            if max_obj.state == STATE['ADD']:  # 当前版本号大于已发布但是未同步更新的版本号
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '该阅读器号存在已发布未更新的版本'
                }
                return JsonResponse(content)

            # 将最新的版本的所有升级包信息加入到新建版本中,如果有依赖版本,就只添加大于等于依赖版本对应基础版本的升级包信息
            # 如果有依赖版本
            if depend_version:
                depend_base_version = depend_version[0]+'.0'
                pack_objs = Package.objects.filter(pid=max_obj.id, base_version__gte=depend_base_version)
            else:
                pack_objs = Package.objects.filter(pid=max_obj.id)
            try:
                rv_obj = RVersion()
                rv_obj.reader_id = reader_id
                rv_obj.version = version
                rv_obj.title = title
                rv_obj.description = description
                rv_obj.depend_version = depend_version
                rv_obj.sort = reader.sort
                rv_obj.save()
                for pack_obj in pack_objs:
                    new_pack_obj = Package()
                    new_pack_obj.base_version = pack_obj.base_version
                    new_pack_obj.model = pack_obj.model
                    new_pack_obj.pack = pack_obj.pack
                    new_pack_obj.md5 = pack_obj.md5
                    new_pack_obj.pid = rv_obj.id
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
            # 存储
            try:
                rv_obj = RVersion()
                rv_obj.reader_id = reader_id
                rv_obj.version = version
                rv_obj.title = title
                rv_obj.description = description
                rv_obj.depend_version = depend_version
                rv_obj.sort = reader.sort
                rv_obj.save()
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

        # 校验阅读器号的当前版本是否存在
        is_exists = RVersion.objects.filter(reader_id=reader_id, version=version).exists()
        if not is_exists:
            content = {
                "code": CODE.PARAMERR,
                "msg": '请输入正确的阅读器号和版本号'
            }
            return JsonResponse(content)

        try:
            rv_obj = RVersion.objects.get(reader_id=reader_id, version=version)
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
    @method_decorator(is_login)
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
            rv_obj.state = 2
            pack_objs = Package.objects.filter(pid=rv_id)
            sync_update_signal.send(sender='RVersionStateView', rv_obj=rv_obj, pack_objs=pack_objs)
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
        rversions = RVersion.objects.filter(reader_id=reader_id).order_by('update_time')

        # 对描述进行处理
        for rversion in rversions:
            description = rversion.description

        context = {
            "rversions": rversions
        }

        return render(request, 'history.html', context)


class PackagesView(View):
    @method_decorator(login_required)
    def get(self, request, pid):
        '''返回当前阅读器当前版本的所有升级包展示界面'''

        # 获取对应阅读器版本的未删除的所有升级包
        pack_objs = Package.objects.filter(pid=pid, state=STATE['ADD']).order_by('base_version', 'model')

        context = {
            'pid': pid,
            'pack_objs': pack_objs
        }

        return render(request, 'packages.html', context)


class PackUpload(View):
    @method_decorator(is_login)
    def post(self, request):
        folder = request.POST.get('folder')
        file_obj = request.FILES.get('Filedata', None)

        # 判断用户是否上传了有效文件
        if not file_obj:
            content = {
                "code": CODE.PARAMERR,
                "msg": "请上传有效文件"
            }
            return JsonResponse(content)
        file_uuid_name = ''
        # 删除旧文件,生成新文件
        dir_list = os.listdir(settings.TMP_UPLOAD_DIR)

        if folder == 'md5':
            file_uuid_name = str(uuid.uuid4()) + '.img.md5'
            for dir in dir_list:
                if dir.endswith('.img.md5'):
                    os.remove(settings.TMP_UPLOAD_DIR + dir)
            tmp_file_path = settings.TMP_UPLOAD_DIR + file_uuid_name
            with open(tmp_file_path, 'wb') as f:
                for con in file_obj.chunks():
                    f.write(con)
        elif folder == 'pack':
            file_uuid_name = str(uuid.uuid4())+'.img'
            for dir in dir_list:
                if dir.endswith('.img'):
                    os.remove(settings.TMP_UPLOAD_DIR + dir)

            tmp_file_path = settings.TMP_UPLOAD_DIR + file_uuid_name
            with open(tmp_file_path, 'wb') as f:
                for con in file_obj.chunks():
                    f.write(con)
        else:
            content = {
                "code": CODE.PARAMERR,
                "msg": "无效的请求"
            }
            return JsonResponse(content)
        content = {
            "code": CODE.OK,
            "msg": '上传成功',
            "data": {
                "file_uuid_name": file_uuid_name,
            },
        }
        return JsonResponse(content)


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
        pack_uuid_name = request.POST.get('pack_uuid_name')
        md5_uuid_name = request.POST.get('md5_uuid_name')

        # 判断用户是否上传了有效文件
        if not all([pack_uuid_name, md5_uuid_name]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "请上传有效文件"
            }
            return JsonResponse(content)

        # 获取当前pid对应的未删除的所有包
        packages = Package.objects.filter(pid=pid, state=STATE['ADD'])

        # 判断当前基础版本的硬件版本是否存在
        pack_obj = packages.filter(base_version=base_version, model=model)
        if pack_obj.exists():
            content = {
                "code": CODE.PARAMERR,
                "msg": "当前基础版本的当前硬件版本已经存在"
            }
            return JsonResponse(content)

        # 生成文件名
        pack_file_name = base_version+model+pid+'.img'
        md5_file_name = base_version+model+pid+'.img.md5'

        new_pack_name = settings.TEST_OBJECT_KEY + pack_file_name
        new_md5_name = settings.TEST_OBJECT_KEY + md5_file_name

        tmp_pack_path = settings.TMP_UPLOAD_DIR + pack_uuid_name
        tmp_md5_path = settings.TMP_UPLOAD_DIR + md5_uuid_name

        # 校验md5值
        with open(tmp_md5_path, 'r') as f:
            right_md5 = f.read(1024)

        check_md5 = file_md5(tmp_pack_path)

        if not (right_md5 == check_md5):
            content = {
                "code": CODE.PARAMERR,
                "msg": "md5值校验失败"
            }
            return JsonResponse(content)

        # 上传文件，保存数据库信息
        oss_obj = LocalOSS(settings.BUCKET_NAME)
        new_pack_url = oss_obj.put_file_object(new_pack_name, tmp_pack_path)
        new_md5_url = oss_obj.put_object(new_md5_name, tmp_md5_path)

        if not new_pack_url:
            logger.error("上传文件{}出错".format(new_pack_name))
            content = {
                "code": CODE.THIRDERR,
                "msg": "上传文件错误".format(new_pack_name)
            }
            return JsonResponse(content)

        if not new_md5_url:
            logger.error("上传文件{}出错".format(new_md5_name))
            content = {
                "code": CODE.THIRDERR,
                "msg": "上传文件{}错误".format(new_md5_name)
            }
            return JsonResponse(content)

        try:
            Package.objects.create(pid=pid, base_version=base_version, model=model, pack=new_pack_url, md5=new_md5_url)
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
        pack_uuid_name = request.POST.get('pack_uuid_name')
        md5_uuid_name = request.POST.get('md5_uuid_name')

        if not all([base_version, model]):
            content = {
                "code": CODE.PARAMERR,
                "msg": '缺少参数'
            }
            return JsonResponse(content)

        # 获取当前pack_id对应的对象
        package = Package.objects.filter(id=pack_id).first()

        # 生成新文件名
        new_pack_file_name = base_version + model + pid + '.img'
        new_md5_file_name = base_version + model + pid + '.img.md5'
        new_pack_name = settings.TEST_OBJECT_KEY + new_pack_file_name
        new_md5_name = settings.TEST_OBJECT_KEY + new_md5_file_name

        # 旧文件名
        old_pack_name = urlsplit(package.pack).path[1:]
        old_md5_name = urlsplit(package.md5).path[1:]

        # 生成升级包临时文件的路径
        tmp_pack_path = settings.TMP_UPLOAD_DIR + pack_uuid_name
        tmp_md5_path = settings.TMP_UPLOAD_DIR + md5_uuid_name

        # 生成oss对象
        oss_obj = LocalOSS(settings.BUCKET_NAME)

        if not (new_pack_name == old_pack_name and new_md5_name == old_md5_name):  # 已改名
            if pack_uuid_name or md5_uuid_name:  # 已修改文件
                # 删除老文件,上传新文件
                del_res1 = oss_obj.del_object(old_pack_name)
                del_res2 = oss_obj.del_object(old_pack_name)
                if not del_res1:
                    logger.error("删除{}失败".format(old_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                if not del_res2:
                    logger.error("删除{}失败".format(old_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                # 上传文件,保存数据库信息

                new_pack_url = oss_obj.put_file_object(new_pack_name, tmp_pack_path)
                new_md5_url = oss_obj.put_file_object(new_md5_name, tmp_md5_path)

                if not new_pack_url:
                    logger.error("上传文件{}出错".format(new_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "上传文件错误".format(new_pack_name)
                    }
                    return JsonResponse(content)
                if not new_md5_url:
                    logger.error("上传文件{}出错".format(new_md5_url))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "上传文件错误".format(new_md5_url)
                    }
                    return JsonResponse(content)
            else:
                # 重命名
                new_pack_url = oss_obj.rename_object(settings.BUCKET_NAME, old_pack_name, new_pack_name)
                new_md5_url = oss_obj.rename_object(settings.BUCKET_NAME, old_md5_name, new_md5_name)

                if not new_pack_url:
                    logger.error("重命名文件{}to{}出错".format(old_pack_name, new_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "修改文件{}错误".format(old_md5_name)
                    }
                    return JsonResponse(content)

                if not new_md5_url:
                    logger.error("重命名文件{}to{}出错".format(old_md5_name, new_md5_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "修改文件{}错误".format(old_md5_name)
                    }
                    return JsonResponse(content)
            # 更新数据库
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
                    "msg": '上传失败'
                }
                return JsonResponse(content)
        else:
            if pack_uuid_name or md5_uuid_name:
                # 删除老文件,上传新文件
                del_res1 = oss_obj.del_object(old_pack_name)
                del_res2 = oss_obj.del_object(old_pack_name)
                if not del_res1:
                    logger.error("删除{}失败".format(old_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                if not del_res2:
                    logger.error("删除{}失败".format(old_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "升级包信息更新失败"
                    }
                    return JsonResponse(content)

                # 上传文件,保存数据库信息
                new_pack_url = oss_obj.put_file_object(new_pack_name, tmp_pack_path)
                new_md5_url = oss_obj.put_file_object(new_md5_name, tmp_md5_path)

                if not new_pack_url:
                    logger.error("上传文件{}出错".format(new_pack_name))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "上传文件错误".format(new_pack_name)
                    }
                    return JsonResponse(content)
                if not new_md5_url:
                    logger.error("上传文件{}出错".format(new_md5_url))
                    content = {
                        "code": CODE.THIRDERR,
                        "msg": "上传文件错误".format(new_md5_url)
                    }
                    return JsonResponse(content)

                try:
                    package.pack = new_pack_url
                    package.md5 = new_md5_url
                    package.save()
                except Exception as e:
                    logger.error('保存失败 detail：{}'.format(e))
                    content = {
                        "code": CODE.DBERR,
                        "msg": '上传失败'
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
            pack.state = STATE['DELETE']
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
        pack_objs = Package.objects.filter(pid=rv_id, state=STATE['ADD']).order_by('base_version', 'model')

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


# 测试使用返回升级包信息
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




