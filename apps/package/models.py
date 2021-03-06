from django.db import models
from tinymce.models import HTMLField

from utils.db.base_db import BaseModel


STATE_CHOICE = (
    (0, '新增'),
    (1, '已删除'),
    (2, '已同步'),
)

IS_DELETE = (
    (0, '新增'),
    (1, '已删除')
)


class Reader(BaseModel):
    reader_name = models.CharField(max_length=64, verbose_name='阅读器号', unique=True)
    sort = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(default=0, choices=IS_DELETE, verbose_name="阅读器号状态")

    class Meta:
        db_table = 'reader'
        verbose_name = '阅读器号'
        verbose_name_plural = verbose_name


class RVersion(BaseModel):
    reader_id = models.IntegerField(verbose_name='阅读器id')
    version = models.CharField(max_length=64, verbose_name='版本')
    title = models.CharField(max_length=124, verbose_name='标题')
    description = HTMLField(verbose_name='描述', null=True, blank=True)
    state = models.IntegerField(default=0, choices=STATE_CHOICE, verbose_name='版本状态')
    depend_version = models.CharField(max_length=64, verbose_name='依赖版本', null=True, blank=True)
    sort = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'rversion'
        verbose_name = '阅读器版本号'
        verbose_name_plural = verbose_name


class Package(BaseModel):
    base_version = models.CharField(max_length=64, verbose_name='基础版本')
    model = models.CharField(max_length=64, verbose_name="硬件版本")
    pack = models.CharField(max_length=256, verbose_name='升级包下载地址')
    md5 = models.CharField(max_length=256, verbose_name='校验码下载地址')
    pid = models.IntegerField(verbose_name='阅读器版本ID')
    state = models.IntegerField(default=0, choices=IS_DELETE, verbose_name='升级包版本状态')

    class Meta:
        db_table = "package"
        verbose_name = '升级包版本号'
        verbose_name_plural = verbose_name
