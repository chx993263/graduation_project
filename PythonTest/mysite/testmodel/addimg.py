#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/18 11:37
# @File    : Picture.py
import pymysql as mysql
import sys

conn = mysql.connect(host='localhost', user='root', passwd='ok', db='attendancesystem')

fp = open("phone.png",'rb')
img = fp.read()
print(img)
fp.close()


    # mysql连接

cursor = conn.cursor()
    # 注意使用Binary()函数来指定存储的是二进制
    # cursor.execute("insert into img set imgs='%s'" % mysql.Binary(img))
cursor.execute("update performance set pic = (%s) where behavior_id = 7",img)
    # 如果数据库没有设置自动提交，这里要提交一下
conn.commit()
cursor.close()
    # 关闭数据库连接
conn.close()


# 提取图片
# def select_imgs(img):
#     cursor = conn.cursor()
#     cursor.execute('select imgs from img')
#     print
#     cursor.fetchall()
#     cursor.close()
#     conn.close()
