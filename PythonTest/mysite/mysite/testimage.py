#!/usr/bin/python

# -*- coding: utf-8 -*-
import pymysql
import sys
import base64


with open('logo.jpg', 'rb') as fp:
    data = fp.read()

conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
cursor = conn.cursor()
sql="INSERT INTO performance SET pic= "+data
print(sql)
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()

