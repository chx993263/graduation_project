# -*- coding: utf-8 -*-
from django.shortcuts import render
# from django.shortcuts import redirect
from django.http import HttpResponse
from . import getTime
from . import getMD5
from . import pageBean
import pymysql
import socket
import json
import os
# from django.core.paginator import Paginator
#获取本机电脑名
myname = socket.getfqdn(socket.gethostname(  ))
#获取本机ip
addr = socket.gethostbyname(myname)
# addr = ''
# 连接数据库
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
# conn = pymysql.connect(host='10.20.8.175', user='root', passwd='njit', db='attendancesystem', port=3306, charset='utf8')
print(conn)
# 打印数据库连接对象
# print('数据库连接对象为：{}'.format(conn))
# 获取游标
cur = conn.cursor()

# 登录
def login(request):
    global conn, cur, addr
    if not conn.ping():
        conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
        cur = conn.cursor()
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            addr = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            addr = request.META.get("REMOTE_ADDR")
    return render(request, "login.html", {"msg": json.dumps('logout')})
# 退出
def logout(request):
    request.session.clear()
    return render(request, "login.html")

# 修改密码
def modifypwd(request):
    oldpwd = request.POST['oldpwd']
    newpwd = request.POST['newpwd']
    isexist = "select count(1) from acct where adminName = \'" + request.session['adminName'] + "\' and password = \'" +getMD5.md5(oldpwd) + "\'"
    cur.execute(isexist)
    if cur.fetchone()[0]:
        print("旧密码正确")
        updateSql =  "update acct set password = \'"+getMD5.md5(newpwd)+"\' where adminName = \'"+request.session['adminName']+"\'"
        log = "insert into log(content,date) values(\'ADMIN:"+request.session['adminName']+" udpate his password\',\'"+getTime.now()+"\')"
        print(updateSql)
        try:
            # 执行sql语句
            cur.execute(updateSql)
            cur.execute(log)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
            return HttpResponse("failed")
        return HttpResponse("success")
    else:
        return HttpResponse("failed")

# 主页
def index(request):
    username= ''
    password= ''
    try:
        username = request.POST['username']
        print(username+"正在进行登录。。。")
        password = request.POST['password']
    except:
        return render(request, "login.html", {"msg": json.dumps('logout')})
    # testSql = "select id,count(1) from acct where adminName = \'"+username+"\' and password = \'"+getMD5.md5(password)+"\'"
    # cur.execute(testSql)
    # rs = cur.fetchone()
    # 将用户名传入，搜索出id,密码以及是否存在该管理员用户。
    adminSql = "select id,password,count(1) from acct where adminName = \'"+username+"\'"
    cur.execute(adminSql)
    rs = cur.fetchone()
    # 记录登录管理员id
    acct_id = rs[0]
    adminpwd = rs[1]
    count = rs[2]
    if(count):
        if adminpwd == getMD5.md5(password):
            # 即将进入主页，记录用户登录
            loginlog = "insert into loginlog(acct_id,loginTime,IPaddress,loginType) values("+str(acct_id)+",\'"+getTime.now()+"\', \'"+addr+"\', 1)"
            request.session['log_id'] = 0
            request.session['adminName'] = username
            try:
                # 执行sql语句
                cur.execute(loginlog)
                # 记录插入得log_id，方便后面进行跟踪更新下线
                request.session['log_id'] = cur.lastrowid
                    # cur.lastrowid
                # 提交到数据库执行
                conn.commit()
            except:
                # 如果发生错误则回滚
                conn.rollback()
                return render(request, "login.html",{"adminName": username,"msg":json.dumps('fail')})
            return render(request, "index.html", {"adminName": username},{"msg":json.dumps('success')})
        return render(request, "login.html",{"adminName": username,"msg":json.dumps('fail')})
    return render(request, "login.html", {"msg": json.dumps('noadmin')})
# 主页
def home(request):
    noticesql = "select performance.id,student_name,class_name,subject_name,behavior_name,performance.time from curriculum,performance,student,subject,behavior,class where curriculum.class_id = class.id and student.id = student_id and subject.id = subject_id and behavior.id = behavior_id and curriculum.id = curriculum_id order by id desc limit 0,3"
    cur.execute(noticesql)
    noticeList = cur.fetchall()
    # 获取今日违纪人数
    today = getTime.today()
    year = getTime.year()+"年"+getTime.month()+"月"
    date = getTime.day()
    personNumsql = "select count(1) from performance where time like \'%"+today+"%\'"
    cur.execute(personNumsql)
    personNum = cur.fetchone()[0]
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "home.html",{"personNum":personNum,"noticeList":noticeList,"year":year,"date":date})

# 工作日志
def worklog(request):
    date = ''
    pageNo = 1
    level = 0
    if request.method == 'POST':
        level = int(request.POST['level'])
        date = request.POST['date']
        pageNo = request.POST['pageNo']

    getCount = "select count(1) from log where date like \'%"+date+"%\'"
    if (level):
        getCount = getCount+"and level="+str(level)
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo),10,pageCount)
    testSql = ''
    if(level):
        testSql = "select * from log where date like \'%"+date+"%\' and level = "+str(level)+" order by id desc limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    else:
        testSql = "select * from log where date like \'%"+date+"%\' order by id desc limit "+str(pagebean.getStartNum())+","+str(pagebean.getPageSize())
    cur.execute(testSql)
    worklogList = cur.fetchall()
    pageinfo = {
        "pageNo" : pageNo,
        "totalPage" : pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "work.html", {'worklogList': worklogList, 'date': date, 'pageinfo' : pageinfo,"level":level})
# 批量删除 工作日志
def dellogs(request):
    delitems = request.POST['delitems']
    # 先将字符串进行解析，转化为全部存储id集合的集合形式
    ids = delitems.split(',')
    # 开始进行批量删除操作
    try:
        # 执行sql语句
        for id in ids:
            dellog = "delete from log where id = "+id
            cur.execute(dellog)
        # 删除log ,不用打印删除记录
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        return HttpResponse("fail")
    return HttpResponse("success")
# 单个删除
def dellog(request):
    id = request.GET['log_id']
    dellog = "delete from log where id = " + id
    try:
        cur.execute(dellog)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    return worklog(request)

# 显示班级，点击可查看课表
def schedule(request):
    pageNo = 1
    if request.method == 'POST':
        pageNo = request.POST['pageNo']
    getCount = "select count(1) from class"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    classSql = "select class.id,class_name,(select count(1) from student where class_id = class.id) as count from class left join student on class_id = class.id group by class_name limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    cur.execute(classSql)
    classList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "schedule.html",{'classList': classList,'pageinfo':pageinfo})
# 查询 课程表
def getKecheng(request):
    classid = request.GET["id"]
    term = request.GET["term"]
    year = request.GET["year"]
    subjectsql = "select week,time,class_name,subject_name,site from curriculum,class,subject where class_id = class.id and subject_id = subject.id and class_id = "+str(classid)+" and term = "+str(term)+" and year = "+str(year)
    cur.execute(subjectsql)
    list = cur.fetchall()
    return HttpResponse(json.dumps(list), content_type="application/json")
# 课程1管理
def curriculum(request):
    year = 1
    term = 1
    pageNo = 1
    classid = 0
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    if request.method == 'POST':
        year = int(request.POST['year'])
        term = int(request.POST['term'])
        classid = int(request.POST['classid'])
        pageNo = request.POST['pageNo']
    # 进行动态sql 拼装
    info1 = "select count(1) from curriculum where year = "+str(year)+" and term = "+str(term)
    info2 = ''
    info3 = ''
    if (classid != 0):
        info3 = "and class_id = "+str(classid)
    countstr = "{} {} {}"
    getCount = countstr.format(info1,info2,info3)
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info1 = "select curriculum.id,week,time,class_name,subject_name,teacher_name,site from curriculum,class,subject,teacher where class.id = class_id and teacher_id = teacher.id and subject.id = subject_id and year = "+str(year)+" and term = "+str(term)
    info2 = ''
    info3 = ''
    info4 = " limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    if (classid != 0):
        info3 = "and class_id = "+str(classid)
    curriculumstr = "{} {} {} {}"
    curriculumsql = curriculumstr.format(info1,info2,info3,info4)
    cur.execute(curriculumsql)
    curriculumList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "curriculum.html",{"pageinfo":pageinfo,"classList":classList,"curriculumList":curriculumList,"classid":classid,"year":year,"term":term})

# 展示修改课程信息
def curriculum_tail(request):
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    # 教师遍历
    teacherSql = "select id,teacher_name from teacher"
    cur.execute(teacherSql)
    teacherList = cur.fetchall()
    # 课程遍历
    subjectSql = "select id,subject_name from subject"
    cur.execute(subjectSql)
    subjectList = cur.fetchall()
    curlid = request.GET["id"]
    curlsql = "select * from curriculum where id = "+curlid
    cur.execute(curlsql)
    curlinfo = cur.fetchone()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "curriculum_tail.html",{"curlinfo":curlinfo,"classList":classList,"subjectList":subjectList,"teacherList":teacherList})
# 修改课程提交申请
def updatecurriculum(request):
    id = request.POST["id"]
    subjectid = request.POST["subjectid"]
    teacherid = request.POST["teacherid"]
    classid = request.POST["classid"]
    time = request.POST["time"]
    week = request.POST["week"]
    term = request.POST["term"]
    year = request.POST["year"]
    site = request.POST["site"]
    # 进行简单的验证 时间跟场地冲突 时间跟老师冲突
    # 这里由于会出现自身冲突，所以我先删除，在添加，并设置事务，如果添加失败，则回滚
    try:
        delsql = "delete from curriculum where id = "+id
        cur.execute(delsql)
        curlsql = "select * from curriculum "
        cur.execute(curlsql)
        curlinfo = cur.fetchall()
        testsql = "select count(1) from curriculum where year = "+year+" and term = "+term+" and  time = "+time+" and week = "+week+" and ( teacher_id = "+teacherid+" or site = \'"+site+"\' )"
        cur.execute(testsql)
        hasexist = cur.fetchone()[0]
        if(int(hasexist)):
            # 场地或者 老师 存在时间冲突,强制异常，数据进行回滚，返回失败页面
            5/0
        # 验证完成，进行添加操作  因为是修改，所以需要 保留之前的 ID
        addsql = "insert into curriculum(id,subject_id,teacher_id,time,week,term,year,class_id,site) values("+id+","+subjectid+","+teacherid+","+time+","+week+","+term+","+year+","+classid+",\'"+site+"\')"
        try:
            # 执行sql语句
            cur.execute(addsql)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
            return render(request, "fail.html")
    except:
        # 如果发生错误则回滚
        conn.rollback()
        return render(request, "fail.html")
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")

def curriculum_add(request):
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    # 教师遍历
    teacherSql = "select id,teacher_name from teacher"
    cur.execute(teacherSql)
    teacherList = cur.fetchall()
    # 课程遍历
    subjectSql = "select id,subject_name from subject"
    cur.execute(subjectSql)
    subjectList = cur.fetchall()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "curriculum_add.html",{"classList":classList,"subjectList":subjectList,"teacherList":teacherList})
# 课程提交申请
def addcurriculum(request):
    subjectid = request.POST["subjectid"]
    teacherid = request.POST["teacherid"]
    classid = request.POST["classid"]
    time = request.POST["time"]
    week = request.POST["week"]
    term = request.POST["term"]
    year = request.POST["year"]
    site = request.POST["site"]
    # 进行简单的验证 时间跟场地冲突 时间跟老师冲突
    testsql = "select count(1) from curriculum where year = "+year+" and term = "+term+" and time = "+time+" and week = "+week+" and ( teacher_id = "+teacherid+" or site = \'"+site+"\' )"
    cur.execute(testsql)
    hasexist = cur.fetchone()[0]
    if(int(hasexist)):
        # 场地或者 老师 存在时间冲突，返回失败页面
        return render(request, "fail.html")
    # 验证完成，进行添加操作
    addsql = "insert into curriculum(subject_id,teacher_id,time,week,term,year,class_id,site) values("+subjectid+","+teacherid+","+time+","+week+","+term+","+year+","+classid+",\'"+site+"\')"
    print(addsql)
    try:
        # 执行sql语句
        cur.execute(addsql)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        return render(request, "fail.html")
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 注销课程
def delcurl(request):
    curlid = request.GET['curlid']
    class_name = request.GET['classname']
    subject_name = request.GET['subjectname']
    delcurl = "delete from curriculum where id = " + curlid
    log = "insert into log(admin,content,date,level) values(\'" + request.session['adminName'] + "\',\'ADMIN:" + request.session['adminName'] + " delete the 课程："+class_name+" 的 "+subject_name+"\' ,\'" + getTime.now() + "\',3)"
    print(log)
    try:
        cur.execute(delcurl)
        # 提交到数据库执行
        cur.execute(log)
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    return curriculum(request)



def absence(request):
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    actSql = "select id,behavior_name from behavior where id <= 3"
    cur.execute(actSql)
    actList = cur.fetchall()
    classid = 0
    actid = 0
    date = ''
    pageNo = 1
    likestudent = ''
    if request.method == 'POST':
        actid = int(request.POST['actid'])
        date = request.POST['date']
        classid = int(request.POST['classid'])
        likestudent = request.POST['likestudent']
        pageNo = request.POST['pageNo']
    info1 = "from performance,student,subject,behavior,class,curriculum where curriculum.id = curriculum_id and curriculum.class_id = class.id and student.id = performance.student_id and subject.id = subject_id and behavior.id = behavior_id and behavior.id <=3 "
    info2 = ''
    info3 = ''
    info4 = ''
    info5 = ''
    info6 = ' order by performance.id desc '
    info7 = ''
    if (actid != 0):
        info2 = "and behavior.id = " + str(actid)
    if (date != ''):
        info3 = "and time like \'%" + date + "%\'"
    if (classid != 0):
        info4 = "and curriculum.class_id = " + str(classid)
    if (likestudent != ''):
        info5 = "and student_name like \'%" + likestudent + "%\'"
    # 获取总的个数
    str1 = "select count(1) {} {} {} {} {} {} {}"
    getCount = str1.format(info1, info2, info3, info4, info5, info6, info7)
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info7 = "limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    str2 = "select performance.id,student_name,class_name,subject_name,behavior_name,performance.time {} {} {} {} {} {} {}"
    testSql = str2.format(info1, info2, info3, info4, info5, info6, info7)
    cur.execute(testSql)
    noticeList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "absence.html",
                  {'date': date, 'classid': classid, 'likestudent': likestudent, 'actid': actid,
                   'likestudent': likestudent, 'classList': classList, 'actList': actList, 'noticeList': noticeList,
                   'pageinfo': pageinfo})

def mesage(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "mesage.html")

def mailList(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "mailList.html")

# 通告
def notice(request):
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    actSql = "select id,behavior_name from behavior where id > 3"
    cur.execute(actSql)
    actList = cur.fetchall()
    classid = 0
    actid = 0
    date = ''
    pageNo = 1
    likestudent = ''
    if request.method == 'POST':
        actid = int(request.POST['actid'])
        date = request.POST['date']
        classid = int(request.POST['classid'])
        likestudent = request.POST['likestudent']
        pageNo = request.POST['pageNo']
    info1 = "from performance,student,subject,behavior,class,curriculum where curriculum.id = curriculum_id and curriculum.class_id = class.id and student.id = student_id and subject.id = subject_id and behavior.id = behavior_id and behavior.id > 3 "
    info2 = ''
    info3 = ''
    info4 = ''
    info5 = ''
    info6 = ' order by performance.id desc '
    info7 = ''
    if (actid !=0):
        info2 = "and behavior.id = "+str(actid)
    if (date != ''):
        info3 = "and time like \'%"+date+"%\'"
    if (classid != 0):
        info4 = "and curriculum.class_id = "+str(classid)
    if (likestudent != ''):
        info5 = "and student_name like \'%"+likestudent+"%\'"
    # 获取总的个数
    str1 = "select count(1) {} {} {} {} {} {} {}"
    getCount = str1.format(info1,info2,info3,info4,info5,info6,info7)
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info7 = "limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    str2 = "select performance.id,student_name,class_name,subject_name,behavior_name,performance.time {} {} {} {} {} {} {}"
    testSql = str2.format(info1,info2,info3,info4,info5,info6,info7)
    cur.execute(testSql)
    noticeList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "notice.html",{'date': date,'classid': classid,'likestudent':likestudent, 'actid': actid,'likestudent': likestudent,'classList': classList,'actList': actList,'noticeList': noticeList,'pageinfo': pageinfo})
# 批量删除 违纪
def delacts(request):
    delitems = request.POST['delitems']
    ids = delitems.split(',')
    print(ids)
    # 开始进行批量删除操作
    try:
        # 执行sql语句
        for id in ids:
            delp = "delete from performance where id = "+id
            getinfo = "select student_id,behavior_id,behavior_score from performance,behavior where behavior_id = behavior.id and performance.id = " + id
            cur.execute(getinfo)
            info = cur.fetchone()
            updatestatistics = ''
            if (int(info[1]) > 3):
                acttype = 1
                updatestatistics = "update statistics set absence_count = absence_count-1 ,score = score +" + str(
                    info[2]) + " where id =" + str(info[0])
            else:
                updatestatistics = "update statistics set violation_count = violation_count-1 ,score = score+" + str(
                    info[2]) + " where id =" + str(info[0])
            print(updatestatistics)
            cur.execute(delp)
            cur.execute(updatestatistics)
        # 提交到数据库执行
        log = "insert into log(admin,content,date,level) values(\'" + request.session['adminName'] + "\',\'ADMIN:" + \
              request.session['adminName'] + " done bulk delete on behavioral notice',\'" + getTime.now() + "\',3)"
        cur.execute(log)
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        return HttpResponse("fail")
    return HttpResponse("success")
# 单个删除
def delact(request):
    id = request.GET['actid']
    acttype = 0
    studentname = request.GET["studentname"]
    delp = "delete from performance where id = " + id
    log = "insert into log(admin,content,date,level) values(\'" + request.session['adminName'] + "\',\'ADMIN:" + request.session['adminName'] + " delete the student:" + studentname + " performance notice\' ,\'" + getTime.now() + "\',3)"
    try:
        getinfo = "select student_id,behavior_id,behavior_score from performance,behavior where behavior_id = behavior.id and performance.id = " + id
        cur.execute(getinfo)
        info = cur.fetchone()
        updatestatistics = ''
        if (int(info[1]) > 3):
            acttype = 1
            updatestatistics = "update statistics set absence_count = absence_count-1 ,score = score +" + str(info[2]) + " where id =" +str(info[0])
        else:
            updatestatistics = "update statistics set violation_count = violation_count-1 ,score = score+" + str(info[2]) + " where id =" + str(info[0])
        print(updatestatistics)
        cur.execute(delp)
        cur.execute(updatestatistics)
        # 提交到数据库执行
        cur.execute(log)
        conn.commit()
    except Exception as err:
        print(err)
        # 如果发生错误则回滚
        conn.rollback()
        return render(request, "fail.html")
    if(acttype):
        return notice(request)
    else:
        return absence(request)

# 显示学生违纪图片
def showimg(request):
    id = request.GET['id']
    # 定义一个图片名称
    imgflag = "media/img"+id+".png"
    if(os.path.exists("./static/"+imgflag)):
        # print("该图片在文件中已存在无需进入数据库查询！")
        None
    else:
        imgsql = "select pic from performance where id ="+id
        cur.execute(imgsql)
        img = cur.fetchone()
        fp = open("./static/"+imgflag, 'wb')
        fp.write(img[0])
        fp.close()
    # img.save('img.png')
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "showimg.html",{"img":imgflag})

# 学生统计
def studentstatistics(request):
    classSql= "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    pageNo = 1
    rank = 0
    ranktype = 0
    classid = 0
    likestudent = ''
    if request.method == 'POST':
        pageNo = request.POST['pageNo']
        rank = int(request.POST['rank'])
        ranktype = int(request.POST['ranktype'])
        classid = int(request.POST['classid'])
        likestudent = request.POST['likestudent']
    setclass = ''
    if (classid != 0):
        setclass = 'and class_id = '+str(classid)
    getCount = "select count(1) from statistics where student_name like \'%"+likestudent+"%\'"+setclass
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info1 = "select statistics.id,student_name,class_name,violation_count,absence_count,score from statistics,class where class_id = class.id and  student_name like \'%"+likestudent+"%\'"+setclass
    info2 = " order by id "
    info3 = ""
    if (ranktype == 1):
        info2 = " order by violation_count "
    if (ranktype == 2):
        info2 = " order by absence_count"
    if (ranktype == 3):
        info2 = " order by score"
    if (rank == 1):
        info3 = " desc "
    info4 = "  limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    studentstr = "{} {} {} {}"
    studentSql = studentstr.format(info1, info2, info3, info4)
    cur.execute(studentSql)
    studentList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "studentstatistics.html",{"classList":classList,"pageinfo":pageinfo,"rank":rank,"ranktype":ranktype,"likestudent":likestudent,"classid":classid,"studentList":studentList})



# 班级统计
def classstatistics(request):
    pageNo = 1
    rank = 0
    ranktype = 0
    if request.method == 'POST':
        pageNo = request.POST['pageNo']
        rank = int(request.POST['rank'])
        ranktype = int(request.POST['ranktype'])
    getCount = "select count(1) from class"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info1 = "select class.id,class_name,(select count(1) from statistics where class_id = class.id ) as personcount,(select sum(violation_count) from statistics where class_id = class.id) as percount,(select sum(absence_count) from statistics where class_id = class.id) as absencecount,(select avg(score) from statistics where class_id = class.id) as avgscore from class,statistics  where  class_id = class.id group by class.id "
    info2 = " order by id "
    info3 = ""
    if(ranktype == 1):
        info2 = " order by percount"
    if(ranktype == 2):
        info2 = " order by absencecount"
    if (ranktype == 3):
        info2 = " order by avgscore"
    if(rank == 1):
        info3 = " desc "
    info4 = "  limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    classstr = "{} {} {} {}"
    classSql = classstr.format(info1,info2,info3,info4)
    cur.execute(classSql)
    classList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "classstatistics.html",{"classList":classList,"pageinfo":pageinfo,"rank":rank,"ranktype":ranktype})
# 跳转
# 班级统计
def showclass(request):
    classSql= "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    pageNo = 1
    rank = 0
    ranktype = 0
    likestudent = ''
    classid = int(request.GET['class_id'])
    setclass = ''
    if (classid != 0):
        setclass = 'and class_id = '+str(classid)
    getCount = "select count(1) from statistics where student_name like \'%"+likestudent+"%\'"+setclass
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    info1 = "select statistics.id,student_name,class_name,violation_count,absence_count,score from statistics,class where class_id = class.id and  student_name like \'%"+likestudent+"%\'"+setclass
    info2 = " order by id "
    info3 = ""
    if (ranktype == 1):
        info2 = " order by percount "
    if (rank == 1):
        info3 = " desc "
    info4 = "  limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    studentstr = "{} {} {} {}"
    studentSql = studentstr.format(info1, info2, info3, info4)
    cur.execute(studentSql)
    studentList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "studentstatistics.html",{"classList":classList,"pageinfo":pageinfo,"rank":rank,"ranktype":ranktype,"likestudent":likestudent,"classid":classid,"studentList":studentList})



# 学生
def student(request):
    classSql= "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    classid = 0
    pageNo = 1
    likestudent = ''
    if request.method == 'POST':
        classid = int(request.POST['classid'])
        likestudent = request.POST['likestudent']
        pageNo = request.POST['pageNo']
    getCount = ""
    if(classid):
        getCount = "select count(1) from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id and class_id = " + str(classid)
    else:
        getCount = "select count(1) from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id "
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 10, pageCount)
    testSql = ''
    if(classid):
        # (CASE WHEN u.timeType=2 THEN '每月第二天' WHEN u.timeType=4 THEN '每月第四天' END) AS timeType
        testSql = "select student.id,student_name,student_no,tel,(case when sex=0 then '女' when sex=1 then '男' end) as sex,class_name from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id and class_id = "+str(classid)+" limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    else:
        testSql = "select student.id,student_name,student_no,tel,(case when sex=0 then '女' when sex=1 then '男' end) as sex,class_name from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id  limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())

    cur.execute(testSql)
    studentList = cur.fetchall()
    pageinfo = {
        "pageNo": pageNo,
        "totalPage": pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "student.html",
                  {'studentList': studentList, 'likestudent': likestudent,'classList': classList, 'classid': classid, 'pageinfo': pageinfo})
# 查看学生
def student_tail(request):
    # 获取数据库 class列表
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    student_id = request.GET['id']
    select = "select * from student where id = "+str(student_id)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    print(info)
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "student_tail.html", {"info": info, "classList": classList})
# 添加学生
def student_add(request):
    # 获取数据库 class列表
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "student_add.html", {"classList": classList})

# 批量添加学生   导入excel文件
def addstudents(request):
    return render(request, "addstudents.html")
def uploadfile(request):
    uploadedFile = request.FILES.get('uploadfile')
    loglist = list()
    fail = ''
    # "导入失败，请检查一下导入的格式！！！"
    flag = getMD5.getstudent(uploadedFile,loglist)
    if flag==1:
        fail = "导入失败，请检查一下导入的格式！！！"
    else:
        log = "insert into log(admin,content,date,level) values(\'" + request.session['adminName'] + "\',\'The ADMIN:" + \
              request.session['adminName'] + " has added students in batches.\',\'" + getTime.now() + "\',2)"
        try:
            # 添加到操作日志
            cur.execute(log)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request,"uploadlog.html",{"loglist": loglist,"fail":fail})



# 提交添加学生
def addstudent(request):
    studentname = request.POST["student_name"]
    studentname = request.POST["student_name"]
    student_no = request.POST["student_no"]
    password = request.POST["password"]
    sex = request.POST["sex"]
    class_id = request.POST["classid"]
    tel = request.POST["tel"]
    notes = request.POST["notes"]
    addstu = "insert into student(student_name,student_no,password,sex,class_id,tel,notes) values(\'"+studentname+"\',"+student_no+",\'"+getMD5.md5(password)+"\',"+sex+","+class_id+",\'"+tel+"\',\'"+notes+"\')"
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" add the new student: "+studentname+"\',\'"+getTime.now()+"\',1)"
    try:
        # 执行sql语句
        cur.execute(addstu)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 修改学生
def updatestudent(request):
    # 获取数据库 class列表
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    student_id = request.GET['id']
    select = "select * from student where id = " + str(student_id)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    print(info)
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "student_update.html", {"info": info, "classList": classList})
# 提交修改学生
def studenttoupdate(request):
    student_id = request.POST["id"]
    studentname = request.POST["student_name"]
    student_no = request.POST["student_no"]
    password = request.POST["password"]
    sex = request.POST["sex"]
    class_id = request.POST["classid"]
    tel = request.POST["tel"]
    notes = request.POST["notes"]
    updatestu = "update student set student_name = \'"+studentname+"\',student_no = \'"+student_no+"\',password = \'"+getMD5.md5(password)+"\',tel = \'"+tel+"\',sex = "+sex+",class_id = "+class_id+", notes = \'"+notes+"\' where id ="+student_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the student: "+studentname+"\',\'"+getTime.now()+"\',2)"
    try:
        # 执行sql语句
        cur.execute(updatestu)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 删除学生
def delstudent(request):
    student_id = request.GET["student_id"]
    studentname = request.GET["student_name"]
    delstu = "delete from student where id = "+student_id
    delstu2 = "delete from statistics where id = "+student_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the student: "+studentname+"\',\'"+getTime.now()+"\',3)"
    try:
        # 执行sql语句
        cur.execute(delstu)
        cur.execute(delstu2)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return student(request)

# 老师
def teacher(request):
    liketeacher = ''
    pageNo = 1
    if request.method == 'POST':
        liketeacher = request.POST['liketeacher']
        pageNo = request.POST['pageNo']
    getCount = "select count(1) from teacher where teacher_name like \'%"+liketeacher+"%\'"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo),10,pageCount)
    testSql = "select id,teacher_name,teacher_no,tel from teacher where teacher_name like \'%"+liketeacher+"%\' or teacher_no like \'%"+liketeacher+"%\' limit "+str(pagebean.getStartNum())+","+str(pagebean.getPageSize())
    cur.execute(testSql)
    teacherList = cur.fetchall()
    pageinfo = {
        "pageNo" : pageNo,
        "totalPage" : pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "teacher.html", {'teacherList': teacherList, 'liketeacher': liketeacher, 'pageinfo' : pageinfo})
# 查看老师
def teacher_tail(request):
    teacher_id = request.GET['id']
    select = "select * from teacher where id = "+str(teacher_id)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "teacher_tail.html", {"info": info})
# 添加老师
def teacher_add(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "teacher_add.html")
# 提交添加老师
def addteacher(request):
    teachername = request.POST["teacher_name"]
    teacher_no = request.POST["teacher_no"]
    password = request.POST["password"]
    tel = request.POST["tel"]
    notes = request.POST["notes"]
    addtea = "insert into teacher(teacher_name,teacher_no,password,tel,notes) values(\'"+teachername+"\',"+teacher_no+",\'"+getMD5.md5(password)+"\',\'"+tel+"\',\'"+notes+"\')"
    print(addtea)
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" add the new teachername: "+teachername+"\',\'"+getTime.now()+"\',1)"
    try:
        # 执行sql语句
        cur.execute(addtea)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 修改老师
def updateteacher(request):
    teacher_id = request.GET['id']
    select = "select * from teacher where id = "+str(teacher_id)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "teacher_update.html", {"info": info})
# 提交修改老师
def teachertoupdate(request):
    teacher_id = request.POST["id"]
    teachername = request.POST["teacher_name"]
    teacher_no = request.POST["teacher_no"]
    password = request.POST["password"]
    tel = request.POST["tel"]
    notes = request.POST["notes"]
    updatetea = "update teacher set teacher_name = \'"+teachername+"\',teacher_no = "+teacher_no+",password = \'"+getMD5.md5(password)+"\',tel = \'"+tel+"\',notes = \'"+notes+"\' where id ="+teacher_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the teachername: "+teachername+"\',\'"+getTime.now()+"\',2)"
    try:
        # 执行sql语句
        cur.execute(updatetea)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 删除老师
def delteacher(request):
    teacher_id = request.GET["teacher_id"]
    teachername = request.GET["teacher_name"]
    deltea = "delete from teacher where id = "+teacher_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the teachername: "+teachername+"\',\'"+getTime.now()+"\',3)"
    try:
        # 执行sql语句
        cur.execute(deltea)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return teacher(request)



# 班级
def classes(request):
    likeclass = ''
    pageNo = 1
    if request.method == 'POST':
        likeclass = request.POST['likeclass']
        pageNo = request.POST['pageNo']
    getCount = "select count(1) from class where class_name like \'%"+likeclass+"%\'"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo),10,pageCount)
    testSql = "select * from class where class_name like \'%"+likeclass+"%\' limit "+str(pagebean.getStartNum())+","+str(pagebean.getPageSize())
    cur.execute(testSql)
    classList = cur.fetchall()
    pageinfo = {
        "pageNo" : pageNo,
        "totalPage" : pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "class.html", {'classList': classList, 'likeclass': likeclass, 'pageinfo' : pageinfo})
# 添加班级
def class_tail(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "class_tail.html")
# 提交添加班级
def addclass(request):
    classname = request.POST["classname"]
    notes = request.POST["notes"]
    addcl = "insert into class(class_name,class_note) values(\'"+classname+"\',\'"+notes+"\')"
    print(addcl)
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" add the new classname: "+classname+"\',\'"+getTime.now()+"\',1)"
    try:
        # 执行sql语句
        cur.execute(addcl)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 修改班级
def updateclass(request):
    class_id = request.GET['id']
    select = "select * from class where id = "+str(class_id)
    print(select)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    if (request.session.get('log_id')):
        try:
            logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
                request.session['log_id'])
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "class_update.html", {"info": info})
# 提交修改班级
def classtoupdate(request):
    class_id = request.POST["id"]
    classname = request.POST["classname"]
    notes = request.POST["notes"]
    upadtecl = "update class set class_name = \'"+classname+"\',class_note = \'"+notes+"\' where id ="+class_id
    try:
        log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the classname: "+classname+"\',\'"+getTime.now()+"\',2)"
        # 执行sql语句
        cur.execute(upadtecl)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
        return render(request, "fail.html", {"msg": 'logout'})
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 删除班级
def delclass(request):
    class_id = request.GET["class_id"]
    delcl = "delete from class where id = "+class_id
    # 出了删除班级 还需要 删除学生， 删除 这个班的课程  删这个班的违规 删这个班的统计表
    delstu = "delete from student where class_id = "+class_id
    delsub = "delete from curriculum where class_id = "+class_id
    delperfor = "delete from performance where class_id = "+class_id
    delstatistics = "delete from statistics where class_id = " + class_id
    classname = request.GET["class_name"]
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the classname: "+classname+" and more\',\'"+getTime.now()+"\',3)"

    try:
        # 执行sql语句
        cur.execute(delcl)
        cur.execute(delstu)
        cur.execute(delsub)
        cur.execute(delperfor)
        cur.execute(delstatistics)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except Exception as e:
        # 如果发生错误则回滚
        print(e)
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return classes(request)


def subject(request):
    likesubject = ''
    pageNo = 1
    if request.method == 'POST':
        likesubject = request.POST['likesubject']
        pageNo = request.POST['pageNo']
    getCount = "select count(1) from subject where subject_name like \'%"+likesubject+"%\'"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo),10,pageCount)
    testSql = "select * from subject where subject_name like \'%"+likesubject+"%\' limit "+str(pagebean.getStartNum())+","+str(pagebean.getPageSize())
    cur.execute(testSql)
    subjectList = cur.fetchall()
    pageinfo = {
        "pageNo" : pageNo,
        "totalPage" : pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "subject.html",{'subjectList': subjectList, 'likesubject': likesubject, 'pageinfo' : pageinfo})
# 添加课程
def subject_tail(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "subject_tail.html")
# 提交添加课程
def addsubject(request):
    subjectname = request.POST["subjectname"]
    notes = request.POST["notes"]
    subjecttime = request.POST["subjecttime"]
    addsub = ''
    if(subjecttime):
        addsub = "insert into subject(subject_name,subject_note,subject_time) values(\'"+subjectname+"\',\'"+notes+"\',"+subjecttime+")"
    else:
        addsub = "insert into subject(subject_name,subject_note) values(\'" + subjectname + "\',\'" + notes + "\')"
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" add the new subjectname: "+subjectname+"\',\'"+getTime.now()+"\',1)"
    try:
        # 执行sql语句
        cur.execute(addsub)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 修改课程
def updatesubject(request):
    subject_id = request.GET['id']
    select = "select * from subject where id = "+str(subject_id)
    print(select)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "subject_update.html", {"info": info})
# 提交修改课程
def subjecttoupdate(request):
    subject_id = request.POST["id"]
    subjectname = request.POST["subjectname"]
    notes = request.POST["notes"]
    subjecttime = request.POST["subjecttime"]
    upadtesub = "update subject set subject_name = \'"+subjectname+"\',subject_note = \'"+notes+"\',subject_time = \'"+subjecttime+"\' where id ="+subject_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the subjectname: "+subjectname+"\',\'"+getTime.now()+"\',2)"
    try:
        # 执行sql语句
        cur.execute(upadtesub)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 删除课程
def delsubject(request):
    subject_id = request.GET["subject_id"]
    delsub = "delete from subject where id = "+subject_id
    subjectname = request.GET["subject_name"]
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the subjectname: "+subjectname+"\',\'"+getTime.now()+"\',3)"
    try:
        # 执行sql语句
        cur.execute(delsub)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return subject(request)

# 不良行为
def behavior(request):
    likebehavior = ''
    pageNo = 1
    if request.method == 'POST':
        likebehavior = request.POST['likebehavior']
        pageNo = request.POST['pageNo']
    getCount = "select count(1) from behavior where behavior_name like \'%"+likebehavior+"%\'"
    # 获取总的个数
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo),10,pageCount)
    testSql = "select * from behavior where behavior_name like \'%"+likebehavior+"%\' limit "+str(pagebean.getStartNum())+","+str(pagebean.getPageSize())
    cur.execute(testSql)
    behaviorList = cur.fetchall()
    pageinfo = {
        "pageNo" : pageNo,
        "totalPage" : pagebean.getTotalPage()
    }
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "behavior.html", {'behaviorList': behaviorList, 'likebehavior': likebehavior, 'pageinfo' : pageinfo})
# 添加不良行为
def behavior_tail(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "behavior_tail.html")
# 提交添加不良行为
def addbehavior(request):
    behaviorname = request.POST["behaviorname"]
    notes = request.POST["notes"]
    behaviorscore = request.POST["behaviorscore"]
    addcl = "insert into behavior(behavior_name,behavior_note,behavior_score) values(\'"+behaviorname+"\',\'"+notes+"\',\'"+behaviorscore+"\')"
    print(addcl)
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" add the new behaviorname: "+behaviorname+"\',\'"+getTime.now()+"\',1)"
    try:
        # 执行sql语句
        cur.execute(addcl)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 修改不良行为
def updatebehavior(request):
    behavior_id = request.GET['id']
    select = "select * from behavior where id = "+str(behavior_id)
    print(select)
    # 执行sql语句
    cur.execute(select)
    info = cur.fetchone()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "behavior_update.html", {"info": info})
# 提交修改不良行为
def behaviortoupdate(request):
    behavior_id = request.POST["id"]
    behaviorname = request.POST["behaviorname"]
    notes = request.POST["notes"]
    behaviorscore = request.POST["behaviorscore"]
    upadtesub = "update behavior set behavior_name = \'"+behaviorname+"\',behavior_note = \'"+notes+"\',behavior_score = \'"+behaviorscore+"\' where id ="+behavior_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the behaviorname: "+behaviorname+"\',\'"+getTime.now()+"\',2)"
    try:
        # 执行sql语句
        cur.execute(upadtesub)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")
# 删除不良行为
def delbehavior(request):
    behavior_id = request.GET["behavior_id"]
    behaviorname = request.GET["behavior_name"]
    delsub = "delete from behavior where id = "+behavior_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the behaviorname: "+behaviorname+"\',\'"+getTime.now()+"\',3)"
    try:
        # 执行sql语句
        cur.execute(delsub)
        # 添加到操作日志
        cur.execute(log)
        # 提交到数据库执行
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return behavior(request)








def success(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "success.html")

# 日历
def calendar(request):
    if (request.session.get('log_id')):
        logout = "update loginlog set logoutTime = \'" + getTime.now() + "\' where id = " + str(
            request.session['log_id'])
        try:
            # 执行sql语句
            cur.execute(logout)
            # 提交到数据库执行
            conn.commit()
        except:
            # 如果发生错误则回滚
            conn.rollback()
    return render(request, "calendar.html")



