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
workbook = xlrd.open_workbook(r'G:\毕设\毕设测试数据\测试教师.xls')
# 根据sheet索引或者名称获取sheet内容
sheet1 = workbook.sheet_by_index(0) # sheet索引从0开始
# sheet的名称，行数，列数  说明拿到了！
print (sheet1.name,sheet1.nrows,sheet1.ncols)
# 获取单元格内容
print(sheet1.cell(1,0).value)
# 测试完成  。。。。。


# 正式开始
# 进行逐行遍历
# 定义list,用来存放教师id
nolist = set()



for i in range(2,sheet1.nrows):
    # 先拿出班级   班级id 取学号前7位
    try:
        college_name = sheet1.cell(i, 1).value
        teacher_no = str(int(sheet1.cell(i, 3).value))
        teacher_name = sheet1.cell(i, 2).value
        tel = "17756"+str(int(sheet1.cell(i, 3).value))
        nolist.add(teacher_no)
        print(college_name,teacher_name,teacher_no,tel)
    except:
        break

    # 往数据库中 插入教师   默认密码123456
    # teachersql = "insert into teacher(id,teacher_no,teacher_name,password,tel,notes) values("+teacher_no+","+teacher_no+",\'"+teacher_name+"\',\'e10adc3949ba59abbe56e057f20f883e\',\'"+tel+"\',\'"+college_name+"\')"
    # print(teachersql)
    # try:
    #     # 执行sql语句
    #     cur.execute(teachersql)
    #     # 提交到数据库执行
    #     conn.commit()
    # except:
    #     # 如果发生错误则回滚
    #     conn.rollback()
    #     print("出错了")
    #     continue
print(nolist)