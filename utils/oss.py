# -*- coding: utf-8 -*-
import oss2
import logging
import hashlib

from oss2.models import BucketLogging

from ota import settings

logger = logging.getLogger('ota')


class LocalOSS(object):
    def __init__(self, bucket_name, *args, **kwargs):
        # 开启oss2操作日志
        # oss2.set_file_logger(settings.LOG_FILE_PATH, 'oss2', logging.INFO)
        self.auth = oss2.Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
        # 创建bucket对象
        self.bucket = oss2.Bucket(self.auth, settings.END_POINT, bucket_name)
        # 开启访问日志记录
        self.bucket.put_bucket_logging(BucketLogging(self.bucket.bucket_name, 'logging/'))

    # 上传网络流
    def put_object(self, obj_name, content, obj_key="", *args, **kwargs):
        result = self.bucket.put_object(obj_key+obj_name, content)
        url = settings.DOWNLOAD_URL_PRE + obj_key + obj_name
        if result.status == 200:
            return url
        else:
            return False

    # 删除多个object
    def del_objects(self, obj_name_list, obj_key="", *args, **kwargs):
        obj_name_list = map(lambda n: obj_key+n, obj_name_list)
        result = self.bucket.batch_delete_objects(obj_name_list)
        if result.status != 200:
            return False
        return True

    def copy_object(self, source_bucket_name, source_obj_name, dest_obj_name, *args, **kwargs):
        result = self.bucket.copy_object(source_bucket_name, source_obj_name, dest_obj_name)
        if result.status != 200:
            return False
        return True

    def obj_exists(self, obj_name, obj_key=""):
        exists = self.bucket.object_exists(obj_key + obj_name)
        if exists:
            logger.debug('{} is exists'.format(obj_key + obj_name))
            return True
        return False
