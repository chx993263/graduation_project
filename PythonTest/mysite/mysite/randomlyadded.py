# 随机添加 添加 课程 以及 上课违纪
import random
import xlrd
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
# 打印数据库连接对象
# print('数据库连接对象为：{}'.format(conn))
# 获取游标
cur = conn.cursor()

# 拿到测试文件 G:\毕设\毕设测试数据\15届分班名单.xlsx
# 拿到学生id,班级id
workbook = xlrd.open_workbook(r'G:\毕设\毕设测试数据\15届分班名单.xlsx')
sheet1 = workbook.sheet_by_index(0) # sheet索引从0开始

# sheet的名称，行数，列数  说明拿到了！
print (sheet1.name,sheet1.nrows,sheet1.ncols)
# 教师id表
teacherid = ['107034', '115030', '120046', '421012', '107032', '106031', '112047', '103055', '107035', '123069', '401033', '117032', '111040', '107037', '120047', '123067', '108050', '104062', '101046', '413020', '419030', '105042', '104061', '107033', '101047', '103054', '106030', '119033', '121033', '112046', '107036', '421013', '413021', '301007']
# 获取单元格内容
print(sheet1.cell(1,0).value)
# 测试完成  。。。。。

# 写入课程
# for i in range(1,500):
#     rand = random.randint(1, sheet1.nrows)
#     classid = sheet1.cell(rand, 2).value[0:7]
#     building = ['信息楼','教学楼东','教学楼西','教学楼南','工业中心','经管楼','文理楼']
#     site = random.choice(building) + random.choice(['A','B','C']) + str(random.randint(1,5)) + '0' + str(random.randint(1,9))
#     cursql = "insert into curriculum(subject_id,teacher_id,time,week,term,year,class_id,site) values("+str(random.randint(1,10))+","+random.choice(teacherid)+","+str(random.randint(1,5))+","+str(random.randint(1,5))+","+str(random.randint(1,2))+","+str(random.randint(1,4))+","+classid+",\'"+site+"\')"
#     print(cursql)
# #     向数据库中 插 课程
#     try:
#         # 执行sql语句
#         cur.execute(cursql)
#         # 提交到数据库执行
#         conn.commit()
#     except:
#         # 如果发生错误则回滚
#         conn.rollback()
#         print("出错了")
#         continue
# print("finish")

# 写入违纪记录
for i in range(1,500):
    rand = random.randint(1, sheet1.nrows)
    student_id = sheet1.cell(rand, 2).value
    classid = sheet1.cell(rand, 2).value[0:7]
    time = "2019-0"+str(random.randint(2,4))+"-"+str(random.randint(1,30)).zfill(2)+" "+str(random.randint(8,17)).zfill(2)+":"+str(random.randint(0,60)).zfill(2)+":"+str(random.randint(0,60)).zfill(2)
    behaviorsql = "insert into performance(subject_id,student_id,behavior_id,class_id,time) values("+str(random.randint(1,10))+","+student_id+","+str(random.randint(1,5))+","+classid+",\'"+time+"\')"
    print(behaviorsql)
#     向数据库中 插 课程
    try:
        # 执行sql语句
        cur.execute(behaviorsql)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        print("出错了")
        continue
print("finish")





