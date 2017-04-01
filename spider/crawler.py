# -*- coding:utf8 -*-

#文章爬取

import sys
import db
import time
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding( "utf-8" )

class Crawl(object):
    def __init__(self):
        # 连接数据库
        self.conn = db.connect()
        self.cur = self.conn.cursor()

    def get_url(self):
        # 获得历史文章的url
        print '**********************************'
        print '获取url'
        sql = 'select url from historylist_articleurl'
        self.cur.execute(sql)
        urls = self.cur.fetchall()
        urls = [url[0] for url in urls]
        print '总共'+str(len(urls))+'条url'
        print '**********************************'
        return urls

    def download(self,url,timeout):
        # 下载 返回BeautifulSoup对象
        print '下载' + url
        webPage = requests.get(url,timeout=timeout)
        webPage = BeautifulSoup(webPage.text,'lxml')
        return webPage

    def dispose(self,webPage):
        # 获得文章 标题，联系人，发布时间，爬取时间，正文
        title = webPage(id='activity-name')[0].text.strip()
        pubTime = webPage(id='post-date')[0].text
        crawlTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        article = []
        keyPoint = []
        main_body = list(webPage(id='js_content')[0])[1:-1]
        for tag in main_body:
            article.append(tag.text.strip()+'\r\n')
            for strong_tag in tag('strong'):
                strong_text = strong_tag.text
                if strong_text is not u'\xa0':
                    keyPoint.append(strong_text.strip())
        article = ''.join(article).replace('\'','\'\'').strip()
        keyPoint = ' '.join(keyPoint).replace('\'','\'\'').strip()
        if len(webPage(class_='rich_media_meta rich_media_meta_text'))==2:
            linkman = webPage(class_='rich_media_meta rich_media_meta_text')[-1].text
            if '/' in linkman:
                linkman = ' '.join(linkman.split('/'))
            if linkman == '请点右侧关注→→':
                linkman = '申万宏源研究'
        else:
            linkman = None
        for tag in main_body:
            if tag.text:
                link = tag.text
                link = link.replace('：',':').replace('（','(').replace('）',')')
                break

        # linkman以三种形式存在
        if '联系人' in link and link.find('联系人')<3:
            print '联系人'
            try:
                linkman = link.split('联系人:')[1]
            except:
                linkman = link.split('联系人 :')[1]
            linkman = linkman.lstrip('(').rstrip(')').rstrip('等')
            if '/' in linkman:
                linkman = ' '.join(linkman.split('/'))
            if '，' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if ',' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if '、' in linkman:
                linkman = ' '.join(linkman.split('、'))
        elif '分析师' in link and link.find('分析师')<3:
            print '分析师'
            linkman = link.split(' ')[0]
            linkman = link.split('\n')[0]
            try:
                linkman = linkman.split('分析师:')[1]
            except:
                linkman = linkman.split('分析师')[0]
            linkman = linkman.lstrip('(').rstrip(')').rstrip('等')
            if '/' in linkman:
                linkman = ' '.join(linkman.split('/'))
            if '，' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if ',' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if '、' in linkman:
                linkman = ' '.join(linkman.split('、'))
        elif '申万宏源宏观' in link and link.find('申万宏源宏观')<10:
            print '申'
            linkman = link.split('申万宏源宏观')[1]
            linkman = linkman.lstrip('(').rstrip(')').rstrip('等')
            if '/' in linkman:
                linkman = ' '.join(linkman.split('/'))
            if '，' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if ',' in linkman:
                linkman = ' '.join(linkman.split('，'))
            if '、' in linkman:
                linkman = ' '.join(linkman.split('、'))
        if not linkman:
            linkman = '申万宏源研究'
        if len(linkman)>200:
            linkman = linkman.split(')')[0]
        linkman.strip().strip('等')
        linkman = linkman.split(' ')
        linkman = ' '.join([i for i in linkman if 1<len(i)<10]).strip()
        if not linkman:
            linkman = '申万宏源研究'
        return pubTime,crawlTime,linkman,article,keyPoint,title

    def save(self,pubTime,crawlTime,linkman,article,keyPoint,title):
        # 保存到数据库
        sql_insert = "insert into article (pub_time,crawl_time,linkman,main_body,key_words,title) values('%s','%s','%s','%s','%s','%s')" \
              % (pubTime,crawlTime,linkman,article,keyPoint,title)
        self.cur.execute(sql_insert)
        self.conn.commit()
        sql_del = 'delete from historylist_articleurl where url="%s"'%(url)
        self.cur.execute(sql_del)
        self.conn.commit()


if __name__ == '__main__':
    crawl = Crawl()
    urls = crawl.get_url()
    length = len(urls)
    for url in urls:
        try:
            webPage = crawl.download(url,0.5)
            pubTime,crawlTime,linkman,article,keyPoint,title = crawl.dispose(webPage)
            print linkman
            crawl.save(pubTime,crawlTime,linkman,article,keyPoint,title)
            length -= 1
            print '剩余'+str(length)+'条url'
        except:
            pass
    crawl.conn.close()
