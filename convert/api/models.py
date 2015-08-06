# -*- coding: utf-8 -*-
from django.db import models


class ConvertTask(models.Model):
    TO_JPG = 0
    TO_PDF = 1

    CONVERT_TYPE_CHOICES = (
        (TO_JPG, 'to_jpg'),
        (TO_PDF, 'to_pdf'),
    )

    STATUS_BEGIN = 0
    STATUS_COPY_TO_QINIU = 1
    STATUS_CONVERT_TO_PDF = 2
    STATUS_DONE = 3
    STATUS_FAIL = -1

    CONVERT_STATUS = (
        (STATUS_BEGIN, 'Begin'),
        (STATUS_COPY_TO_QINIU, 'Copy to QINIU'),
        (STATUS_CONVERT_TO_PDF, 'Convert To PDF'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAIL, 'Fail'),

    )

    created_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    convert_type = models.IntegerField(choices=CONVERT_TYPE_CHOICES, default=TO_JPG)
    source_url = models.URLField(verbose_name=u'PPT，DOC源文件地址')
    key = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField(choices=CONVERT_STATUS, default=STATUS_BEGIN)
    callback_url = models.URLField()
    fail_log = models.TextField(blank=True, null=True)


class ConvertResult(models.Model):
    # convert result in qiniu
    JPEG = 0
    PDF = 1
    FILE_TYPE = (
        (JPEG, 'jpeg'),
        (PDF, 'pdf')
    )
    created_time = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=200)
    convert_task = models.ForeignKey(ConvertTask, related_name='convert_results')
    file_type = models.IntegerField(choices=FILE_TYPE)


from .receivers import *