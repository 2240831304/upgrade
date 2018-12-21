import logging
import re
from urllib.parse import urlsplit

from django.dispatch import receiver
from package.signals.signals import sync_update_signal
from general_user.models import RVersion, Package

from django.conf import settings

from utils.oss import LocalOSS

logger = logging.getLogger('ota')


@receiver(sync_update_signal, dispatch_uid='sync_update_receiver')
def sync_update_handler(sender, **kwargs):
    new_rv_obj = kwargs['rv_obj']
    pack_objs = kwargs['pack_objs']

    update_rv_obj = RVersion()

    try:
        update_rv_obj.reader_id = new_rv_obj.reader_id
        update_rv_obj.version = new_rv_obj.version
        update_rv_obj.title = new_rv_obj.title
        update_rv_obj.description = new_rv_obj.description
        update_rv_obj.state = 2
        update_rv_obj.depend_version = new_rv_obj.depend_version
        update_rv_obj.sort = new_rv_obj.sort
        update_rv_obj.save()
    except Exception as e:
        raise e

    pid = RVersion.objects.filter(reader_id=new_rv_obj.reader_id, version=new_rv_obj.version).first().id
    for pack_obj in pack_objs:
        update_pack_obj = Package()
        try:
            update_pack_obj.base_version = pack_obj.base_version
            update_pack_obj.model= pack_obj.model
            test_pack_name = urlsplit(pack_obj.pack).path[1:]
            test_md5_name = urlsplit(pack_obj.md5).path[1:]

            # 将object_key替换
            pack_name = test_pack_name.replace(settings.TEST_OBJECT_KEY, settings.OBJECT_KEY)
            md5_name = test_md5_name.replace(settings.TEST_OBJECT_KEY, settings.OBJECT_KEY)

            update_pack_obj.pack = settings.DOWNLOAD_URL_PRE + pack_name
            update_pack_obj.md5 = settings.DOWNLOAD_URL_PRE + md5_name
            update_pack_obj.pid = pid
            update_pack_obj.save()
            # 将测试包拷贝到用户包存储路径
            oss_obj = LocalOSS(settings.BUCKET_NAME)
            oss_obj.copy_object(settings.BUCKET_NAME, test_pack_name, pack_name)
        except Exception as e:
            raise e