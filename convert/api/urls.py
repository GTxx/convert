from rest_framework import routers
from django.conf.urls import patterns, url
from .views import ConvertTaskViewSet, qiniu_persist_callback

router = routers.SimpleRouter()

router.register(r'convert_task', ConvertTaskViewSet)

urlpatterns = router.urls
urlpatterns += patterns(
    '',
    url(r'^qiniu_persist_callback$', qiniu_persist_callback, name='qiniu_persist_callback')
)
