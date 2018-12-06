from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间', null=True, blank=True)
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新时间', null=True, blank=True)

    class Meta:
        abstract = True