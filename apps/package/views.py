import logging
import re
import requests
from multiprocessing.dummy import Pool

from django.conf import settings
from django.db.models import F
from django.shortcuts import render
from django.http.response import JsonResponse
from django.views import View
from django.http import QueryDict
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from utils.decorator import is_login
from package.models import Reader, RVersion, Package
from ota.response_code import CODE, RET

logger = logging.getLogger("ota")


def get_update_versions(reader_id):
    # 返回对应阅读器号的所有已同步更新版本号
    version_list = []
    version_objs = RVersion.objects.filter(reader_id=reader_id, state=2).order_by('version')
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

        # 获取当前阅读器号未删除的所有对象
        rversions = RVersion.objects.filter(reader_id=reader_id)
        if rversions.exists():
            # 校验阅读器号的当前版本是否存在，避免发布阅读器号已经存在的版本
            rv_obj = rversions.filter(version=version)
            if rv_obj.exists():  # 当前阅读器的当前版本已存在
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '当前阅读器的当前版本已存在'
                }
                return JsonResponse(content)

            # 校验阅读器版本是否低于已发布的版本，只有高版本才能发布
            max_obj = rversions.order_by('-version')[0]
            max_version = max_obj.version

            if version < max_version:
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '最新发布的版本不能小于已发布的版本'
                }
                return JsonResponse(content)

            if max_obj.state == 0:  # 当前版本号大于已发布但是未同步更新的版本号
                content = {
                    "code": CODE.PARAMERR,
                    "msg": '该阅读器号存在已发布未更新的版本'
                }
                return JsonResponse(content)

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
            rv_obj.save()
        except:
            logger.error('{}阅读器版本同步更新失败'.format(rv_obj))
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
        rversions = RVersion.objects.filter(reader_id=reader_id)

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
        pack_objs = Package.objects.filter(pid=pid, state=0).order_by('base_version', 'model')

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
            'pid': pid
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

        # 判断用户是否上传了有效文件
        if not all([pack_con, md5_con]):
            content = {
                "code": CODE.PARAMERR,
                "msg": "请上传有效文件"
            }
            return JsonResponse(content)

        # 获取当前pid对应的未删除的所有包
        packages = Package.objects.filter(pid=pid, state=0)

        # 判断当前基础版本的硬件版本是否存在
        package = packages.filter(base_version=base_version, model=model)
        if package.exists():
            content = {
                "code": CODE.PARAMERR,
                "msg": "当前基础版本的当前硬件版本已经存在"
            }
            return JsonResponse(content)

        # 上传文件，保存数据库信息
        from utils.oss import put_alios
        pack_url = put_alios(pack_con.name, pack_con.chunks())
        md5_url = put_alios(md5_con.name, md5_con.chunks())

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

        try:
            Package.objects.create(pid=pid, base_version=base_version, model=model, pack=pack_url, md5=md5_url)
        except Exception as e:
            logging.error('保存失败 detail：{}'.format(e))
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
        pack_id = pack_id
        base_version = request.POST.get('base_version')
        model = request.POST.get('model')
        pack_con = request.FILES.get('pack_con')
        md5_con = request.FILES.get('md5_con')

        if not all([base_version, model]):
            content = {
                "code": CODE.PARAMERR,
                "msg": '缺少参数'
            }
            return JsonResponse(content)

        # 未修改文件
        if (not pack_con) and (not md5_con):
            try:
                package = Package.objects.get(id=pack_id)
                package.base_version=base_version
                package.model = model
            except Exception as e:
                logger.error('id为{}的升级包更新失败，detail：{}'.format(pack_id, e))
                content = {
                    "code": CODE.DBERR,
                    "msg": "升级包信息更新失败"
                }
                return JsonResponse(content)
        else:
            # 修改了文件
            from utils.oss import put_alios, del_alios
            # 删除之前的包文件
            package = Package.objects.filter(id=pack_id).first()
            pack_name = re.search(r'^.*/(.*)?$', package.pack).group(1)
            md5_name = package.md5_name

            result = del_alios([pack_name, md5_name])

            if not result:
                content = {
                    "code": CODE.THIRDERR,
                    "msg": "升级包信息更新失败"
                }
                return JsonResponse(content)

            # 保存新的包文件
            pack_url = put_alios(pack_con.name, pack_con.chunks())
            md5_url = put_alios(md5_con.name, md5_con.chunks())

            try:
                Package.objects.create(pid=pid, base_version=base_version, model=model, pack=pack_url, md5=md5_url)
            except Exception as e:
                logging.error('保存失败 detail：{}'.format(e))
                content = {
                    "code": CODE.DBERR,
                    "msg": '文件上传失败'
                }
                return JsonResponse(content)

        content = {
            "code": CODE.OK,
            "msg": '修改成功',
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
            pack.state = 1
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
        pack_objs = Package.objects.filter(pid=rv_id, state=0).order_by('base_version', 'model')

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


def upgrade_version(cu_version, reader_id, p_rv_obj):
    depend_version = p_rv_obj.depend_version
    # 检验最新版本是否有依赖版本
    if depend_version:
        if cu_version < depend_version:  # 比依赖版本小
            rv_obj = RVersion.objects.filter(reader_name=reader_id, version=depend_version).first()
            upgrade_version(cu_version, reader_id, rv_obj)
    return p_rv_obj


def get_pack(request, is_test):
    version = request.GET.get('version', '')
    model = request.GET.get('model', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING')
    action = request.META.get("HTTP_ACTION")
    device = request.META.get("HTTP_DEVICE")
    version = version.strip("V")

    # 校验参数
    if accept_encoding.strip() != "":
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.ENCODINGERR
        return response

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
        max_obj = RVersion.objects.filter(reader_id=reader_id).order_by('-version').first()
    else:
        max_obj = RVersion.objects.filter(reader_id=reader_id, state=2).order_by('-version').first()

    if not max_obj:  # 没有最大版本
        response = render(request, 'xml/default.xml', content_type="application/xml")
        response['result-code'] = RET.MODELERR
        return response

    # 返回要升级的版本
    up_obj = upgrade_version(version, reader_id, max_obj)

    # 获取要升级版本的基础版本号
    base_version = re.search(r'(\d+?)\.', up_obj.version).group(1) + '.0'

    # 过滤富文本html标签
    des = up_obj.description
    pattern = re.compile('>(.*?)<')
    # 取html标签中的数据
    des = pattern.findall(des)
    # 去除列表空字符串
    des = filter(None, des)
    # 拼接
    description = "&lt;br&gt;".join(des)

    pack_obj = Package.objects.filter(base_version=base_version, model=model).first()

    context = {
        "title": up_obj.title,
        "description": description,
        "base_version": pack_obj.base_version,
        "pack": pack_obj.pack,
        "md5": pack_obj.md5,
    }

    response = render(request, 'xml/upgrade.xml', context=context, content_type="application/xml")
    response['result-code'] = RET.OK
    return response


# 测试使用返回升级包信息
def get_package_test(request):
    return get_pack(request, True)


# 用户使用返回升级包信息
def get_package(request):
    return get_pack(request, False)


def upload(pack_obj):
    pack = pack_obj.pack
    md5 = pack_obj.md5

    if not (pack or md5):
        logger.debug("没有包")
        return
    # 获取升级包名
    pack_pattern = re.search(r'^.*/(.*)$', pack)
    md5_pattern = re.search(r'^.*/(.*)$', md5)

    if not (pack_pattern or md5_pattern):
        logger.debug("已经上传")
        return
    pack_name = re.search(r'^.*/(.*)$', pack).group(1)
    md5_name = re.search(r'^.*/(.*)$', md5).group(1)

    # 根据url请求包内容
    pack_res = requests.get(pack)
    md5_res = requests.get(md5)
    logger.debug("{}下载完成".format(pack_name))
    logger.debug("{}下载完成".format(md5_name))

    # 上传oss
    from utils.oss import put_alios
    put_alios(pack_name, pack_res.content)
    put_alios(md5_name, md5_res.content)
    logger.debug("{}上传完成".format(pack_name))
    logger.debug("{}上传完成".format(md5_name))

    # 修改域名
    try:
        pack_obj.pack = settings.DOWNLOAD_URL_PRE + pack_name
        pack_obj.md5 = settings.DOWNLOAD_URL_PRE + md5_name
        pack_obj.save()
    except Exception as e:
        return


def upload_pack(request):
    pack_objs = Package.objects.all()
    pool = Pool(4)

    results2 = pool.map(upload, pack_objs)
    pool.close()
    pool.join()

    return JsonResponse({"code": CODE.OK, "msg":"修改成功"})





