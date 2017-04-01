# -*- coding:utf8 -*-
import db
import sys
import re
import os

#从标题中提取有股票代码的公司

reload(sys)
sys.setdefaultencoding( "utf-8" )

class GetCompany(object):
    def __init__(self):
        # 连接到数据库
        self.conn = db.connect()
        self.cur = self.conn.cursor()

    def get_titles(self):
        # 获取含有股票代码的标题
        # 返回字典{文章标题:对应数据库id}
        sql = 'select id,title from article'
        self.cur.execute(sql)
        titles_tuple = self.cur.fetchall()

        titles = {}
        for title_tuple in titles_tuple:
            title = title_tuple[1].replace('（','(').replace('）',')').replace('：',':') # 获得标题字符串 并 替换括号和冒号
            if re.search('\([A-Za-z0-9\: ]{5,7}\)',title):  # 如果有股票代码，取出标题
                titles[title_tuple[0]] = title

        return titles

    def title_split(self,title):
        # 对标题进行分割
        title_re = re.findall('\([A-Za-z0-9\: ]{5,7}\)',title)
        length = len(title_re)
        titles = []
        for i in range(length):
            if i==0:
                n = title[:title.find(title_re[i])+len(title_re[i])]
                titles.append(n)
            else:
                n = title[title.find(title_re[i-1])+len(title_re[i-1]):title.find(title_re[i])+len(title_re[i])]
                titles.append(n)
        return titles

    def extract_one(self,title):
        # 从标题中切割出公司名称
        title = title.encode('utf8')
        if re.search('—.*?\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('—(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('、(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('、(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search(':(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall(':(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('要】首推(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('要】首推(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('】(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('】(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('参与(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('参与(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('《(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('《(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('看好(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('看好(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('；(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('；(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return self.extract_one(a)
        elif re.search('(.*?)\([A-Za-z0-9\: ]{5,7}\)', title):
            a = ''.join(re.findall('(.*?\([A-Za-z0-9\: ]{5,7}\))', title))
            return a

    def extract_more(self,title_split):
        # title_split为列表
        # 调用 extract_one处理传过来的标题列表
        company = []
        for title in title_split:
            company.append(self.extract_one(title))
        company = ' '.join([i for i in company if i])
        if company:
            print company
            return  company

    def save(self,title_id,company):
        # 保存入数据库
        sql = "update article set company='%s' where id = '%d'" % (company,int(title_id))
        self.cur.execute(sql)
        self.conn.commit()

    def get_company(self):
        # 获得所有的公司名
        sql = 'select company from article where company != ""'
        self.cur.execute(sql)
        companys = self.cur.fetchall()
        companys = ' '.join([i[0] for i in companys if i[0]] )
        companys = list(set([i+')' for i in companys.split(')')]))
        company_dict = {}
        for company in companys:
            try:
                company_dict[company.split(u'(')[0]] = '('+company.split(u'(')[1]
            except:
                print company
        if not os.path.exists('company.txt'):
            with open('company.txt','a') as f:
                for code,company_name in company_dict.items():
                    f.write(code + '  ' + company_name + '\r\n')
        return company_dict

    def update_company(self):
        # 对没有股票代码的名称通过数据库已有公司进行匹配并更新
        sql = 'select id,title from article where company is null'
        self.cur.execute(sql)
        titles = self.cur.fetchall()
        # a =  len(titles)
        # print a
        titles = [list(i) for i in titles]
        companys = self.get_company()
        for i in titles:
            company = []
            for j in companys.viewkeys():
                if j in i[1]:
                    company.append(j+companys[j])
            company = ' '.join(company)
            sql = 'update article set company="%s" where id="%d"'%(company,i[0])
            self.cur.execute(sql)
            self.conn.commit()

if __name__ == '__main__':
    getCompany = GetCompany()
    titles = getCompany.get_titles() #此处为字典
    for title_id,title in titles.items():
        company = getCompany.title_split(title) # 分割后的title列表
        company = getCompany.extract_more(company) # 提取出了公司
        # getCompany.save(title_id,company)

    getCompany.conn.close()





