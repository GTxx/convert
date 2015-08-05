# -*- coding: utf-8 -*-
# from win32com import client
from cStringIO import StringIO
import pythoncom
import comtypes.client
from wand.image import Image
import os
import requests
import contextlib
from uuid import uuid4
import tempfile
import urlparse
from boto.s3.connection import S3Connection
from boto.s3.key import Key



conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)


def store_file_to_s3(file_path):
    path, filename = os.path.split(file_path)
    key = Key(bucket)
    key.key = str(uuid4()) + '/' + filename
    res = key.set_contents_from_filename(file_path)
    return res, urlparse.urljoin(AWS_HTTP_URL, key.key)


def store_string_to_s3(name, string):
    key = Key(bucket)
    key.key = str(uuid4()) + '/' + name
    res = key.set_contents_from_string(string)
    return res, urlparse.urljoin(AWS_HTTP_URL, key.key)


@contextlib.contextmanager
def create_temp_file(suffix):
    try:
        fh, filename = tempfile.mkstemp(suffix, prefix=str(uuid4()), dir='d:\\temp\\')
        os.close(fh)
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


def local_pdf_2_jpg(pdf_file_name):
    with Image(filename=pdf_file_name) as origin:
        with origin.convert('jpeg') as image:
            image_url_list = []
            for single_image in image.sequence:
                with create_temp_file('.jpeg') as (_, image_file_name):
                    with Image(image=single_image) as _img:
                        _img.save(filename=image_file_name)
                    length, image_url = store_file_to_s3(image_file_name)
                    image_url_list.append(image_url)
            return image_url_list

class Doc(object):

    def __init__(self, file_url):
        self.file_url = file_url
        # pythoncom.CoInitialize()
        self.word = comtypes.client.CreateObject('Word.Application')
        self.word.Visible = True
        self.word.DisplayAlerts = False

    def get_jpg(self):
        with create_temp_file('.doc') as (_, doc_file_name), create_temp_file('.pdf') as (_, pdf_file_name):
            with open(doc_file_name, 'wb') as doc_file:
                down_file(self.file_url, doc_file)

            # 用win32com api时，文件不能被其他程序打开

            import ipdb; ipdb.set_trace()
            word_handle = self.word.Documents.Open(doc_file_name)
            word_handle.SaveAs(pdf_file_name, 17)
            # import ipdb; ipdb.set_trace()
            word_handle.Close()

            length, pdf_url = store_file_to_s3(pdf_file_name)
            # print(length, pdf_url)
            # import ipdb; ipdb.set_trace()
            image_url_list = local_pdf_2_jpg(pdf_file_name)

            return image_url_list

    def get_pdf(self):
        with create_temp_file('.doc') as (_, doc_file_name), create_temp_file('.pdf') as (_, pdf_file_name):
            with open(doc_file_name, 'wb') as doc_file:
                down_file(self.file_url, doc_file)

            # 用win32com api时，文件不能被其他程序打开
            word_handle = self.word.Documents.Open(doc_file_name)
            word_handle.SaveAs(pdf_file_name, 17)
            # import ipdb; ipdb.set_trace()
            word_handle.Close()

            length, pdf_url = store_file_to_s3(pdf_file_name)

            return [pdf_url, ]


class PPT(object):
    def __init__(self, file_url):
        self.file_url = file_url
        # pythoncom.CoInitialize()
        self.ppt = comtypes.client.CreateObject('Powerpoint.Application')
        self.ppt.Visible = True
        self.ppt.DisplayAlerts = False

    def get_pdf(self):
        with create_temp_file('.ppt') as (_, ppt_file_name), create_temp_file('.pdf') as (_, pdf_file_name):
            with open(ppt_file_name, 'wb') as ppt_file:
                down_file(self.file_url, ppt_file)

            # 用win32com api时，文件不能被其他程序打开
            import ipdb; ipdb.set_trace()
            ppt_handle = self.ppt.Presentations.Open(ppt_file_name)
            ppt_handle.SaveAs(pdf_file_name, 32)
            ppt_handle.Close()

            length, pdf_url = store_file_to_s3(pdf_file_name)
            return [pdf_url, ]

    def get_jpg(self):
        result_url_list = []
        with create_temp_file('.ppt') as (_, ppt_file_name), create_temp_file('.pdf') as (_, pdf_file_name):
            with open(ppt_file_name, 'wb') as ppt_file:
                down_file(self.file_url, ppt_file)

            # 用win32com api时，文件不能被其他程序打开
            ppt_handle = self.ppt.Presentations.Open(ppt_file_name)
            ppt_handle.SaveAs(pdf_file_name, 32)
            ppt_handle.Close()

            length, pdf_url = store_file_to_s3(pdf_file_name)
            # result_url_list.append(pdf_url)
            image_url_list = local_pdf_2_jpg(pdf_file_name)
            result_url_list += image_url_list

            return result_url_list
