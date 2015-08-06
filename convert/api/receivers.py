from __future__ import absolute_import
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from .serializers import ConvertTaskSerializer
from .models import ConvertTask


@receiver(post_save, sender=ConvertTask)
def success_push(sender, instance, **kwargs):
    print('success push')
    if instance.status == ConvertTask.STATUS_DONE:
        data = ConvertTaskSerializer(instance).data
        response = requests.post(instance.callback_url, json=data)

@receiver(post_save, sender=ConvertTask)
def fail_push(sender, instance, **kwargs):
    print('fail push')
    if instance.status == ConvertTask.STATUS_FAIL:
        data = ConvertTaskSerializer(instance).data
        response = requests.post(instance.callback_url, json=data)
