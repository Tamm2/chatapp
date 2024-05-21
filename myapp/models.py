from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    image = models.ImageField(upload_to="uploads",default="images/noimage.png",verbose_name="プロフィール画像",)

class Talk(models.Model):
    talk_from  = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='from_name')
    talk_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='to_name')
    talk = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)


class Inquiry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="ユーザー")
    name = models.CharField("お名前", max_length=100)
    message = models.TextField("お問い合わせ内容")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    def __str__(self):
        return self.name