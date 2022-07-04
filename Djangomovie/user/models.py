from django.db import models


class users(models.Model):
    userid = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=32)
    userpasswd = models.CharField(max_length=32)
    register_time = models.CharField(max_length=225)
    class Meta:
        db_table = 'users'


# Create your models here.
