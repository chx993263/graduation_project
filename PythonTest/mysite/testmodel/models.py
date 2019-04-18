from django.db import models
class Acct(models.Model):
    adminName = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    status = models.IntegerField()
    createDate = models.CharField(max_length=20)
    modifyDate = models.CharField(max_length=20)
