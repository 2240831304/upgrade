# -*- coding: utf-8 -*-
import oss2
import logging
from oss2.models import BucketLogging

from django.conf import settings

logger = logging.getLogger('ota')

auth = oss2.Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, settings.END_POINT, settings.BUCKET_NAME)


def put_alios(obj_name, content):
    result = bucket.put_object(obj_name, content)
    url = settings.DOWNLOAD_URL_PRE + obj_name
    if result.status == 200:
        return url
    else:
        return False


def del_alios(obj_name_list):
    result = bucket.batch_delete_objects(obj_name_list)
    if result.status != 200:
        return False
    return True

