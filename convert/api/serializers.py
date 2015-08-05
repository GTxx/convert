from rest_framework import serializers
from .models import ConvertTask, ConvertResult


class ConvertResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConvertResult


class ConvertTaskSerializer(serializers.ModelSerializer):
    convert_results = ConvertResultSerializer(many=True, read_only=True)

    class Meta:
        model = ConvertTask

