from rest_framework import serializers
import urlparse
from django.conf import settings
from .models import ConvertTask, ConvertResult


class ConvertResultSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return urlparse.urljoin(settings.QINIU_CDN_DOMAIN, obj.key)

    class Meta:
        model = ConvertResult


class ConvertTaskSerializer(serializers.ModelSerializer):
    convert_results = ConvertResultSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return urlparse.urljoin(settings.QINIU_CDN_DOMAIN, obj.key)

    class Meta:
        model = ConvertTask

