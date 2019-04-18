from django.shortcuts import render
from django.http import HttpResponse
from . import getTime
from . import getMD5
from . import pageBean
import pymysql
import socket
import json
from django.core.paginator import Paginator
#获取本机电脑名
myname = socket.getfqdn(socket.gethostname(  ))
#获取本机ip
addr = socket.gethostbyname(myname)
# addr = '198.168.1.1'

conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')

# 打印数据库连接对象
# print('数据库连接对象为：{}'.format(conn))
# 获取游标
cur = conn.cursor()

# 登录
def login(request):
    return render(request, "login.html")


# 修改密码
def modifypwd(request):
    oldpwd = request.POST['oldpwd']
    print(oldpwd)
    newpwd = request.POST['newpwd']
    print(newpwd)
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
    username = request.POST['username']
    print(username)
    password = request.POST['password']
    print(password)
    testSql = "select id,count(1) from acct where adminName = \'"+username+"\' and password = \'"+getMD5.md5(password)+"\'"
    cur.execute(testSql)
    rs = cur.fetchone()
    # 记录登录管理员id
    acct_id = rs[0]
    count = rs[1]
    if count:
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
            return render(request, "login.html",{"msg":json.dumps('fail')})
        return render(request, "index.html", {"adminName": username},{"msg":json.dumps('success')})
    return render(request, "login.html",{"msg":json.dumps('fail')})

# 主页
def home(request):
    noticesql = "select performance.id,student_name,class_name,subject_name,behavior_name,performance.time from performance,student,subject,behavior,class where class_id = class.id and student.id = student_id and subject.id = subject_id and behavior.id = behavior_id order by id desc limit 0,3"
    cur.execute(noticesql)
    noticeList = cur.fetchall()
    # 获取今日违纪人数
    today = getTime.today();
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
    return render(request, "home.html",{"personNum":personNum,"noticeList":noticeList})

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
    return render(request, "work.html", {'worklogList': worklogList, 'date': date, 'pageinfo' : pageinfo})
# 批量删除 工作日志
def dellogs(request):
    delitems = request.POST['delitems']
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
    pagebean = pageBean.PageTest(int(pageNo), 3, pageCount)
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
    pagebean = pageBean.PageTest(int(pageNo), 3, pageCount)
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
        print(delsql)
        cur.execute(delsql)
        curlsql = "select * from curriculum "
        cur.execute(curlsql)
        curlinfo = cur.fetchall()
        print(curlinfo)
        testsql = "select count(1) from curriculum where time = "+time+" and week = "+week+" and ( teacher_id = "+teacherid+" or site = \'"+site+"\' )"
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
    testsql = "select count(1) from curriculum where time = "+time+" and week = "+week+" and ( teacher_id = "+teacherid+" or site = \'"+site+"\' )"
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
    return render(request, "absence.html")
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
    actSql = "select id,behavior_name from behavior"
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
    info1 = "from performance,student,subject,behavior,class where class_id = class.id and student.id = student_id and subject.id = subject_id and behavior.id = behavior_id "
    info2 = ''
    info3 = ''
    info4 = ''
    info5 = ''
    info6 = ' order by performance.id desc '
    info7 = ''
    if (actid !=0):
        info2 = "and behavior.id = "+str(actid)
    if (date != ''):
        info3 = "and date like \'"+date+"\'"
    if (classid != 0):
        info4 = "and class_id = "+str(classid)
    if (likestudent != ''):
        info5 = "and student_name like \'"+likestudent+"\'"
    # 获取总的个数
    str1 = "select count(1) {} {} {} {} {} {} {}"
    getCount = str1.format(info1,info2,info3,info4,info5,info6,info7)
    cur.execute(getCount)
    pageCount = cur.fetchone()[0]
    pagebean = pageBean.PageTest(int(pageNo), 3, pageCount)
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
            deln = "delete from performance where id = "+id
            cur.execute(deln)
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
    studentname = request.GET["studentname"]
    delp = "delete from performance where id = " + id
    log = "insert into log(admin,content,date,level) values(\'" + request.session['adminName'] + "\',\'ADMIN:" + request.session['adminName'] + " delete the student:" + studentname + " performance notice\' ,\'" + getTime.now() + "\',3)"
    try:
        cur.execute(delp)
        # 提交到数据库执行
        cur.execute(log)
        conn.commit()
    except:
        # 如果发生错误则回滚
        conn.rollback()
    return notice(request)


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
    pagebean = pageBean.PageTest(int(pageNo), 3, pageCount)
    testSql = ''
    if(classid):
        testSql = "select student.id,student_name,student_no,tel,sex,class_name from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id and class_id = "+str(classid)+" limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())
    else:
        testSql = "select student.id,student_name,student_no,tel,sex,class_name from student,class where (student.student_name like \'%" + likestudent + "%\' or student.student_no like \'%" + likestudent + "%\') and student.class_id = class.id  limit " + str(pagebean.getStartNum()) + "," + str(pagebean.getPageSize())

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
    print(updatestu)
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
    deltea = "delete from student where id = "+student_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the student: "+studentname+"\',\'"+getTime.now()+"\',3)"
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
    pagebean = pageBean.PageTest(int(pageNo),3,pageCount)
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
    pagebean = pageBean.PageTest(int(pageNo),3,pageCount)
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
    return render(request, "class_update.html", {"info": info})
# 提交修改班级
def classtoupdate(request):
    class_id = request.POST["id"]
    classname = request.POST["classname"]
    notes = request.POST["notes"]
    upadtecl = "update class set class_name = \'"+classname+"\',class_note = \'"+notes+"\' where id ="+class_id
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" update the classname: "+classname+"\',\'"+getTime.now()+"\',2)"
    try:
        # 执行sql语句
        cur.execute(upadtecl)
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
# 删除班级
def delclass(request):
    class_id = request.GET["class_id"]
    delcl = "delete from class where id = "+class_id
    classname = request.GET["class_name"]
    log = "insert into log(admin,content,date,level) values(\'"+request.session['adminName']+"\',\'ADMIN:"+request.session['adminName']+" delete the classname: "+classname+"\',\'"+getTime.now()+"\',3)"
    try:
        # 执行sql语句
        cur.execute(delcl)
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
    pagebean = pageBean.PageTest(int(pageNo),3,pageCount)
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
    pagebean = pageBean.PageTest(int(pageNo),3,pageCount)
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



