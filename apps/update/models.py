
from django.db import models



class softwarepackage(models.Model):
    device = models.CharField(max_length=20, db_index=True)
    version = models.CharField(max_length=20)
    md5 = models.TextField()
    updateContent = models.TextField()
    url = models.URLField()
    pubdate = models.DateTimeField(auto_now=True)

    class Meta:
        #app_label = 'update'
        db_table = 'softwarepackage'
        verbose_name = '软件包信息'
        verbose_name_plural = verbose_name



class hardwarepackage(models.Model):
    device = models.CharField(max_length=20, db_index=True)
    version = models.CharField(max_length=20)
    md5 = models.TextField()
    updateContent = models.TextField()
    url = models.URLField()
    pubdate = models.DateTimeField(auto_now=True)


    class Meta:
        # app_label = 'update'
        db_table = 'hardwarepackage'
        verbose_name = '硬件包信息'
        verbose_name_plural = verbose_name
