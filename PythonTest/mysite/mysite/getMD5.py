import hashlib
import xlrd
import pymysql


def md5(str):
    return hashlib.md5(str.encode('utf-8')).hexdigest()

def getstudent(file,loglist):
    flag = 0
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
    # 打印数据库连接对象
    # print('数据库连接对象为：{}'.format(conn))
    # 获取游标
    cur = conn.cursor()

    workbook = xlrd.open_workbook(filename=None, file_contents=file.read())
    # 根据sheet索引或者名称获取sheet内容
    sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
    # sheet的名称，行数，列数  说明拿到了！
    print(sheet1.name, sheet1.nrows, sheet1.ncols)
    # 进行验证
    if(sheet1.ncols != 5):
        flag = 1
        return flag

    # 正式开始
    # 进行逐行遍历

    # 先定义一个班级id用来存放班级id,如果id变了就说明换班级了，添加新的班级
    testid = sheet1.cell(1, 2).value[0:7]

    for i in range(1, sheet1.nrows):
        # 先拿出班级   班级id 取学号前7位
        college_name = sheet1.cell(i, 0).value
        class_name = sheet1.cell(i, 1).value
        classid = sheet1.cell(i, 2).value[0:7]
        student_no = sheet1.cell(i, 2).value
        student_name = sheet1.cell(i, 3).value
        sex_name = sheet1.cell(i, 4).value
        sex = 1
        if (sex_name == '女'):
            sex = 0
        if(len(student_name)>= 5 or student_no.isnumeric() == False or len(sex_name) != 1):
            flag = 1
            return flag
        # 拿到 classid, 到数据库中查看是否已存在 该班级，如果不存在，则添加新的班级
        isexistsql = "select count(1) from class where id ="+classid
        cur.execute(isexistsql)
        isexist = cur.fetchone()[0]
        if (isexist == 0):
            #  不存在，先进行添加新的班级
            classsql = "insert into class values(" + classid + ",\'" + class_name + "\',\'" + college_name + "-" + class_name + "\')"
            loglist.append("添加新的班级:" + class_name)
            try:
                # 执行sql语句
                cur.execute(classsql)
                loglist.append("添加新的班级:" + class_name+" 成功！")
                # 提交到数据库执行
                conn.commit()
            except:
                # 如果发生错误则回滚
                conn.rollback()
                loglist.append("添加新的班级:" + class_name + " 失败！")
                continue
        # 往数据库中 插入学生   默认密码123456
        studentsql = "insert into student(id,student_no,student_name,sex,password,class_id) values(" + student_no + "," + student_no + ",\'" + student_name + "\'," + str(
            sex) + ",\'e10adc3949ba59abbe56e057f20f883e\'," + classid + ")"
        statisticsql = "insert into statistics(id,student_name,class_id) values(" + student_no + ",\'" + student_name + "\'," + classid + ")"
        loglist.append(studentsql)
        try:
            # 执行sql语句
            cur.execute(studentsql)
            cur.execute(statisticsql)
            loglist.append("学生："+student_no+"-"+student_name+"添加成功！")
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
            loglist.append("学生：" + student_no + "-" + student_name + "添加失败！，可能是该同学已存在。")
            continue
    loglist.append("end...")
    cur.close()
    conn.close()
    return flag
