from __future__ import absolute_import
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from .serializers import ConvertTaskSerializer
from .models import ConvertTask


@receiver(post_save, sender=ConvertTask)
def success_convert_to_image(sender, instance, **kwargs):
    if instance.status == ConvertTask.STATUS_CONVERT_TO_IMG:
        data = ConvertTaskSerializer(instance).data
        try:
            response = requests.post(instance.callback_url, json=data)
            instance.status = ConvertTask.STATUS_DONE
            instance.save()
        except Exception as e:
            instance.fail_log = str(e)
            instance.status = ConvertTask.STATUS_FAIL
            instance.save()


@receiver(post_save, sender=ConvertTask)
def fail_push(sender, instance, **kwargs):
    if instance.status == ConvertTask.STATUS_FAIL:
        data = ConvertTaskSerializer(instance).data
        response = requests.post(instance.callback_url, json=data)
