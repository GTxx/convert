# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
import os
import urlparse
from qiniu import Auth, BucketManager, PersistentFop, op_save, put_data, put_data, put_data, put_data, put_data
import contextlib
import tempfile
import requests
from uuid import uuid4
from wand.image import Image
import cStringIO
from .models import ConvertTask, ConvertResult
from django.conf import settings


QINIU_CALLBACK_URL = settings.QINIU_CALLBACK_URL

QINIU_CDN_DOMAIN = settings.QINIU_CDN_DOMAIN
QINIU_BUCKET_NAME = settings.QINIU_BUCKET_NAME
qiniu_auth = Auth(settings.QINIU_AK, settings.QINIU_SK)
bucket = BucketManager(qiniu_auth)
PPT_URL = 'http://taidiiv2-static.s3.amazonaws.com/lessonplanv3/materials/i%20love%20you%20benny%20jaya%20hehehe_good%20xx_96583f32-413b-4175-944d-24ecdd5766ad.pptx'


@contextlib.contextmanager
def create_temp_file(suffix):
    try:
        fh, filename = tempfile.mkstemp(suffix, prefix=str(uuid4()))
        # os.close(fh)
        yield (fh, filename)
    except Exception as e:
        print('in create temp file error ', e)
        raise e
    finally:
        os.remove(filename)


def down_file(file_url, dst_file):
    r = requests.get(file_url, stream=True)
    for line in r.iter_content(1024):
        dst_file.write(line)


def copy_to_qiniu(source_url):
    key = str(uuid4()) + os.path.splitext(urlparse.urlparse(source_url).path)[1]
    ret, info = bucket.fetch(source_url, QINIU_BUCKET_NAME, key)
    return ret, info


def convert_to_pdf(source_key, convert_task_id=None):
    dest_key = source_key + '.pdf'
    op = op_save('yifangyun_preview', QINIU_BUCKET_NAME, dest_key)
    pfop = PersistentFop(
        qiniu_auth, QINIU_BUCKET_NAME,
        notify_url=urlparse.urljoin(
            QINIU_CALLBACK_URL,
            '/api/qiniu_persist_callback?convert_task_id={}'.format(convert_task_id)))
    ret, info = pfop.execute(source_key, [op, ])
    import ipdb; ipdb.set_trace()
    return ret, info


def download_pdf_convert_image_save_qiniu(key):
    # 1 pdf下载到本地的临时文件中
    # 2 pdf转成jpeg
    # 3 jpeg保存到qiniu
    pdf_file = tempfile.TemporaryFile(suffix='.pdf')
    down_file(urlparse.urljoin(QINIU_CDN_DOMAIN, key), pdf_file)
    pdf_file.seek(0)
    with Image(file=pdf_file, format='pdf') as origin:
        with origin.convert('jpeg') as image:
            key_list = []
            for idx, single_image in enumerate(image.sequence):
                with Image(image=single_image) as _img:
                    output = cStringIO.StringIO()
                    _img.save(file=output)
                    content = output.getvalue()
                    img_key = '{}-{}.jpeg'.format(key, idx)
                    token = qiniu_auth.upload_token(QINIU_BUCKET_NAME, img_key)
                    res = put_data(up_token=token, key=img_key, data=content, mime_type='image/jpeg')
                    print(res)
                    key_list.append(img_key)

            return key_list

@shared_task()
def copy_convert(convert_task_id):
    convert_task = ConvertTask.objects.get(id=convert_task_id)

    response, info = copy_to_qiniu(convert_task.source_url)
    if not info.ok():
        convert_task.status = -1
        convert_task.fail_log = str(info)
        convert_task.save()

        # TODO: send fail message to v2
        return

    convert_task.status = 1
    convert_task.key = response['key']
    convert_task.save()

    response, info = convert_to_pdf(response['key'], convert_task_id)
    if not info.ok():
        convert_task.status = -1
        convert_task.fail_log = str(info)
        convert_task.save()
        # TODO: send fail message to v2
        return

    convert_task.status = 2
    convert_task.save()


@shared_task()
def convert_to_image(convert_task_id, convert_result_id):
    convert_task = ConvertTask.objects.get(id=convert_task_id)
    convert_result_pdf = ConvertResult.objects.get(id=convert_result_id)
    key_list = download_pdf_convert_image_save_qiniu(convert_result_pdf.key)

    for key in key_list:
        ConvertResult.objects.create(key=key, convert_task=convert_task)

    # TODO: callback to v2
    return key_list

