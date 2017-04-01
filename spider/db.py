# -*- coding:utf8 -*-
import MySQLdb

#数据库连接

def connect():
    return  MySQLdb.connect(host='10.0.0.59',user='hyf',db='sf_hyf',passwd='9PSO04KR8',charset='utf8')