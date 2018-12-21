# -*- coding: utf-8 -*-
import oss2
import logging
import hashlib

from oss2.models import BucketLogging

from ota import settings

logger = logging.getLogger('ota')


class LocalOSS(object):
    def __new__(cls, bucket_name, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # oss2.set_file_logger(settings.LOG_FILE_PATH, 'oss2', logging.INFO)
            cls._instance = super(LocalOSS, cls).__new__(cls, *args, **kwargs)
            # 初始化
            cls._instance.auth = oss2.Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
            cls._instance.bucket = oss2.Bucket(cls._instance.auth, settings.END_POINT, bucket_name)
            cls._instance.bucket.put_bucket_logging(BucketLogging(bucket_name, 'logging/'))
        return cls._instance

    # 上传本地文件
    def put_file_object(self, obj_name, file_path):
        exists = self.obj_exists(obj_name)
        if exists:
            logger.debug('{} is exists'.format(obj_name))
            url = settings.DOWNLOAD_URL_PRE + obj_name
            return url
        else:
            result = self.bucket.put_object_from_file(obj_name, file_path)
            url = settings.DOWNLOAD_URL_PRE + obj_name
            if result.status == 200:
                return url
            else:
                return False

    # 上传网络流
    def put_object(self, obj_name, content, *args, **kwargs):
        exists = self.obj_exists(obj_name)
        if exists:
            logger.debug('{} is exists'.format(obj_name))
            url = settings.DOWNLOAD_URL_PRE + obj_name
            return url
        else:
            result = self.bucket.put_object(obj_name, content)
            url = settings.DOWNLOAD_URL_PRE + obj_name
            if result.status == 200:
                return url
            else:
                return False

    # 删除单个文件
    def del_object(self, obj_name, *args, **kwargs):
        exists = self.obj_exists(obj_name)
        if not exists:
            logger.debug('{} is not exists'.format(obj_name))
            return False
        else:
            result = self.bucket.delete_object(obj_name)
            if result.status != 200:
                return False
            return True

    # 同一oss 拷贝文件
    def copy_object(self, source_bucket_name, source_obj_name, dest_obj_name, *args, **kwargs):
        result = self.bucket.copy_object(source_bucket_name, source_obj_name, dest_obj_name)
        if result.status != 200:
            return False
        return True

    # 判断文件是否存在
    def obj_exists(self, obj_name):
        return self.bucket.object_exists(obj_name)


    # 重命名文件
    def rename_object(self, source_bucket_name, source_obj_name, dest_obj_name, *args, **kwargs):
        result1 = self.copy_object(source_bucket_name, source_obj_name, dest_obj_name)
        if not result1:
            logger.debug("{}:{}重命名为{}:{}失败".format(source_bucket_name, source_obj_name, self.bucket.bucket_name, dest_obj_name))
            return False
        result2 = self.del_object(self, source_obj_name)
        if not result2:
            logger.debug(
                "{}:{}重命名为{}:{}失败".format(source_bucket_name, source_obj_name, self.bucket.bucket_name, dest_obj_name))
            return False
        url = settings.DOWNLOAD_URL_PRE + dest_obj_name
        return url