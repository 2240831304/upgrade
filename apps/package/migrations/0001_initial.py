# Generated by Django 2.0 on 2018-12-12 16:26

from django.db import migrations, models
import django.utils.timezone
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='更新时间')),
                ('base_version', models.CharField(max_length=64, verbose_name='基础版本')),
                ('model', models.CharField(max_length=64, verbose_name='硬件版本')),
                ('pack', models.CharField(max_length=256, verbose_name='升级包下载地址')),
                ('md5', models.CharField(max_length=256, verbose_name='校验码下载地址')),
                ('pid', models.IntegerField(verbose_name='阅读器版本ID')),
                ('state', models.IntegerField(choices=[(0, '新增'), (1, '已删除')], default=0, verbose_name='升级包版本状态')),
            ],
            options={
                'verbose_name': '升级包版本号',
                'verbose_name_plural': '升级包版本号',
                'db_table': 'package',
            },
        ),
        migrations.CreateModel(
            name='Reader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='更新时间')),
                ('reader_name', models.CharField(max_length=64, unique=True, verbose_name='阅读器号')),
                ('sort', models.IntegerField(blank=True, null=True)),
                ('state', models.IntegerField(choices=[(0, '新增'), (1, '已删除')], default=0, verbose_name='阅读器号状态')),
            ],
            options={
                'verbose_name': '阅读器号',
                'verbose_name_plural': '阅读器号',
                'db_table': 'reader',
            },
        ),
        migrations.CreateModel(
            name='RVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='更新时间')),
                ('reader_id', models.IntegerField(verbose_name='阅读器id')),
                ('version', models.CharField(max_length=64, verbose_name='版本')),
                ('title', models.CharField(max_length=124, verbose_name='标题')),
                ('description', tinymce.models.HTMLField(blank=True, null=True, verbose_name='描述')),
                ('state', models.IntegerField(choices=[(0, '新增'), (1, '已删除'), (2, '已同步')], default=0, verbose_name='版本状态')),
                ('depend_version', models.CharField(blank=True, max_length=64, null=True, verbose_name='依赖版本')),
                ('sort', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '阅读器版本号',
                'verbose_name_plural': '阅读器版本号',
                'db_table': 'rversion',
            },
        ),
    ]