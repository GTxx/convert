# 依赖
image处理需要安装imagemagic和build基础库，请参考[docker build file](https://github.com/docker-library/buildpack-deps/blob/1f3d93c27c45732774639eff8ade2b75cf13bbea/jessie/Dockerfile）
pdf转换成image需要安装ghostscript：
```
sudo apt-get install ghostscript
```
# 配置
在local_settings.py中加入
```
# QINIU
QINIU_CALLBACK_URL = '服务器地址'
QINIU_CDN_DOMAIN = '七牛bucket地址'
QINIU_BUCKET_NAME = 'bucket name'
QINIU_AK = 'your ak'
QINIU_SK = 'your sk'

# celery
BROKER_URL = 'celery broker url' # redis://localhost:6380//0
```

# 启动
```
python manage.py runserver
celery worker --app=convert --loglevel=info
```

# 使用
```
method: post 
{
    "convert_type": 0, # convert type, 
    "source_url": "http://abc.com/ccc.ppt",
    "callback_url": "http://server.com" // will post results to this url 
}
```
