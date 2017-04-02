# -*- coding:utf8 -*-

# 定时爬取

from bs4 import BeautifulSoup
import requests
import db
import re
import json
import time
from spider.crawler import Crawl
from spider.getCompany import GetCompany

crawl = Crawl()

class Timed(object):
    def __init__(self,public_num_name):
        # 连接到数据库
        self.conn = db.connect()
        self.cur = self.conn.cursor()
        self.last_crawl_title = '久其软件(002279)—中位数177%增长的一季报开创10年Q1盈利先河!' # 上一次爬取的第一篇文章标题,这里可以从数据库里读取这一篇文章，而不是直接指定
        self.now_crawl_title = None
        self.public_num_name = public_num_name

    def get_public_num_url(self):
        # 获得公众号地址
        url = 'http://weixin.sogou.com/weixin?query='+self.public_num_name
        html = requests.get(url).text
        soup = BeautifulSoup(html,'lxml')
        url_public_num = soup.find_all(uigs='account_name_0')[0].get('href')
        print url_public_num
        return url_public_num

    def get_article_url(self,url_public_num):
        # 获得文章的URL
        html = requests.get(url_public_num).text
        msgList = re.findall('var msgList = (\{.*\})',html)[0]
        msgList = json.loads(msgList)['list'][0]
        urls = []

        for i in range(10):
            if msgList['app_msg_ext_info']['title'].strip() == self.last_crawl_title:
                # 遇到了last_crawl_title，退出循环
                break
            else:
                if i == 0:
                    print msgList
                    self.now_crawl_title = msgList['app_msg_ext_info']['title'].strip()  # 这次爬取的第一篇文章标题
                    self.last_crawl_title = self.now_crawl_title # 将最前面的文章表题赋值给上一次的文章表题
                url_parent = 'http://mp.weixin.qq.com' + msgList['app_msg_ext_info']['content_url']
                urls.append(url_parent)
                for j in range(len(msgList['app_msg_ext_info']['multi_app_msg_item_list'])):
                    url = 'http://mp.weixin.qq.com' + msgList['app_msg_ext_info']['multi_app_msg_item_list'][j]['content_url']
                    urls.append(url)
        urls = [re.sub('amp;', '', url) for url in urls]

        return urls

    def crawl(self,url,timeout):
        # urls为url列表
        # 从html中提取出所需内容
        webPage = crawl.download(url, timeout)
        pubTime, crawlTime, linkman, article, keyPoint, title = crawl.dispose(webPage)
        getcompany = GetCompany()
        companys = getcompany.get_company()
        company = None
        a = title.replace('（', '(').replace('）', ')').replace('：', ':')
        if re.search('\([A-Za-z0-9\: ]{5,7}\)', a):
            company = getcompany.title_split(a)  # 分割后的title列表
            company = getcompany.extract_more(company)  # 提取出了公司

        if not company:
            print 1
            company = []
            for j in companys.viewkeys():
                if j in a:
                    company.append(j + companys[j])
            company = ' '.join(company)

        return pubTime,crawlTime,linkman,article,keyPoint,title,company

    def save(self,pubTime,crawlTime,linkman,article,keyPoint,title,company):
        # 保存进数据库
        sql = "insert into article (pub_time,crawl_time,linkman,main_body,key_words,title,company) values('%s','%s','%s','%s','%s','%s','%s')" \
              % (pubTime, crawlTime, linkman, article, keyPoint, title, company)
        self.cur.execute(sql)
        self.conn.commit()


if __name__ == '__main__':
    timed = Timed('申万宏源研究')
    while (True):
        url_public_num = timed.get_public_num_url()
        urls = timed.get_article_url(url_public_num)
        print len(urls)
        if urls:
            for url in urls:
                pubTime, crawlTime, linkman, article, keyPoint, title, company = timed.crawl(url,2)
                print title
                # timed.save(pubTime,crawlTime,linkman,article,keyPoint,title,company)
        time.sleep(1800)