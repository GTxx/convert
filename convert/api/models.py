# -*- coding: utf-8 -*-
from django.db import models


class ConvertTask(models.Model):

    CONVERT_TYPE_CHOICES = (
        (0, 'doc->pdf'),
        (1, 'doc->jpg'),
        (2, 'ppt->pdf'),
        (3, 'ppt->jpg'),
    )
    CONVERT_STATUS = (
        (0, 'Begin'),
        (1, 'Copy to QINIU'),
        (2, 'Convert To PDF'),
        (3, 'Download PDF'),
        (4, 'Done'),
        (-1, 'Fail'),
        (11, 'PDF Convert To Image'),
    )

    created_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    convert_type = models.IntegerField(choices=CONVERT_TYPE_CHOICES)
    source_url = models.URLField(verbose_name=u'PPT，DOC源文件地址')
    key = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField(choices=CONVERT_STATUS, default=0)
    callback_url = models.URLField()
    fail_log = models.TextField(blank=True, null=True)


class ConvertResult(models.Model):
    # convert result in qiniu
    created_time = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=200)
    convert_task = models.ForeignKey(ConvertTask, related_name='convert_results')
