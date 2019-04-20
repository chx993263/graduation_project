# 添加测试数据
# 需求：15级的表，将所有同学进行分班并且插入到学生中
import xlrd
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
# 打印数据库连接对象
# print('数据库连接对象为：{}'.format(conn))
# 获取游标
cur = conn.cursor()

# 拿到测试文件 G:\毕设\毕设测试数据\15届分班名单.xlsx
# 打开文件
workbook = xlrd.open_workbook(r'G:\毕设\毕设测试数据\15届分班名单.xlsx')
# 根据sheet索引或者名称获取sheet内容
sheet1 = workbook.sheet_by_index(0) # sheet索引从0开始
# sheet的名称，行数，列数  说明拿到了！
print (sheet1.name,sheet1.nrows,sheet1.ncols)
# 获取单元格内容
print(sheet1.cell(1,0).value)
# 测试完成  。。。。。


# 正式开始
# 进行逐行遍历

# 先定义一个班级id用来存放班级id,如果id变了就说明换班级了，添加新的班级
testid = sheet1.cell(1, 2).value[0:7]

for i in range(1,sheet1.nrows):
    # 先拿出班级   班级id 取学号前7位
    college_name = sheet1.cell(i, 0).value
    class_name = sheet1.cell(i, 1).value
    classid = sheet1.cell(i, 2).value[0:7]
    student_no = sheet1.cell(i, 2).value
    student_name = sheet1.cell(i, 3).value
    sex_name = sheet1.cell(i, 4).value
    sex = 1
    if(sex_name == '女'):
        sex = 0


    if(classid != testid):
    #     如果classid 变了，说明需要添加新的班级，并将 testid刷新
        testid = classid
        classsql = "insert into class values("+classid+",\'"+class_name+"\',\'"+college_name+"-"+class_name+"\')"
        print(classsql)
        try:
            # 执行sql语句
            cur.execute(classsql)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
            print("出错了")
            break
    # 往数据库中 插入学生   默认密码123456
    studentsql = "insert into student(id,student_no,student_name,sex,password,class_id) values("+student_no+","+student_no+",\'"+student_name+"\',"+str(sex)+",\'e10adc3949ba59abbe56e057f20f883e\',"+classid+")"
    print(studentsql)
    try:
        # 执行sql语句
        cur.execute(studentsql)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        print("出错了")
        break