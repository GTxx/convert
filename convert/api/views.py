from __future__ import absolute_import
from rest_framework.decorators import api_view, list_route
from rest_framework.response import Response
from rest_framework import viewsets, status
# from .utils import Doc, PPT
from .tasks import copy_convert, convert_to_image
from .models import ConvertTask, ConvertResult
from .serializers import ConvertTaskSerializer


class ConvertTaskViewSet(viewsets.ModelViewSet):
    queryset = ConvertTask.objects.all()
    serializer_class = ConvertTaskSerializer
    model = ConvertTask

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        object = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # start copy and convert to pdf
        copy_convert.delay(object.id)
        return Response(ConvertTaskSerializer(object).data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['POST'])
def qiniu_persist_callback(request):
    # import ipdb; ipdb.set_trace()
    convert_task = ConvertTask.objects.get(
        id=request.query_params['convert_task_id'])
    convert_result = ConvertResult.objects.create(
        key=request.data['items'][0]['key'],
        convert_task=convert_task, file_type=ConvertResult.PDF)
    convert_to_image.delay(convert_task.id, convert_result.id)
    convert_task.status = ConvertTask.STATUS_CONVERT_TO_PDF
    convert_task.save()
    return Response(data={'ok': 'ok'})


@api_view(['POST'])
def test_callback(request):
    print('test callback dataL: ', request.data)
    return Response(data={'ok': 'ok'})
