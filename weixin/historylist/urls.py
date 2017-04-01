# -*- coding:utf8 -*-

from django.conf.urls import url
from .import views

urlpatterns = [
    url(r'getmsgjson/$',views.getmsgjson,name='getmsgjson'),
]