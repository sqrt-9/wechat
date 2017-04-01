# -*- coding: utf-8 -*-
from django.http import HttpResponse
import json
import os
from .models import articleUrl

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


def getmsgjson(request):
    Str = request.POST.get('str')
    Str = Str.replace('&quot;','\'').replace('\'\'','\"null\"').replace('\',\'','\",\"').replace('\':\'','\":\"').replace('\':','\":').replace(',\'',',\"').replace('\'{','\"{').replace('{\'','{\"').replace('\'}','\"}').replace('{\'','{\"')

    Str = json.loads(Str)
    #except:
    #    a = ''.join(Str[i] for i in range(0,20))
    #    print a


    article = {}
    #print len(Str['list'])
    #print(len(Str['list'][0]))
    #print Str['list'][0]
    if Str['list']:
        article_list = Str['list']
        #print article_list
        for i in article_list:
            title_parent = i['app_msg_ext_info']['title']
            url_parent = i['app_msg_ext_info']['content_url'].replace(r'\/',r'/')
            if title_parent and url_parent:
                article[url_parent] = title_parent
            child_list = i['app_msg_ext_info']['multi_app_msg_item_list']
            if child_list:
                for j in child_list:
                    title = j['title']
                    url = j['content_url'].replace(r'\/',r'/')
                    article[url] = title
    for i,j in article.items():
        articleModel = articleUrl(url=i,title=j)
        articleModel.save()

    return HttpResponse(json.dumps({'action':'success'}),content_type='application/json')


