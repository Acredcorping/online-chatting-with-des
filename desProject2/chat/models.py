from django.db import models

# Create your models here.
from django.db import models


class User(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=20, unique=True)
    password = models.CharField(verbose_name='密码', max_length=100)
    email = models.EmailField(verbose_name='邮箱')


class Message(models.Model):
    content = models.CharField(verbose_name='消息内容', max_length=255)
    sender = models.ForeignKey(verbose_name='发送者', to='User', on_delete=models.CASCADE, related_name='send')
    receiver = models.ForeignKey(verbose_name='接收者', to='User', on_delete=models.CASCADE, related_name='recv')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class SecretKey(models.Model):
    user = models.ForeignKey(verbose_name='用户', to='User', on_delete=models.CASCADE, related_name='user')
    obj = models.ForeignKey(verbose_name='对象', to='User', on_delete=models.CASCADE, related_name='obj')
    key = models.CharField(verbose_name='密钥', max_length=100, null=False, blank=False)


class Application(models.Model):
    user = models.ForeignKey(verbose_name='用户', to='User', on_delete=models.CASCADE, related_name='app_user')
    obj = models.ForeignKey(verbose_name='对象', to='User', on_delete=models.CASCADE, related_name='app_obj')
    remark = models.CharField(verbose_name='备注', max_length=100, null=True, blank=True)
    status = models.IntegerField(verbose_name='状态', choices=((0, '未处理'), (1, '已同意'), (2, '已拒绝')), default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
