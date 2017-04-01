#-*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models

class articleUrl(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=100)