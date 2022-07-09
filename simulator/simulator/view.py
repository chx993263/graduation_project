from django.shortcuts import render
from django.http import HttpResponse
import pymysql
import json
import sys
def index(request):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
    cur = conn.cursor()
    classSql = "select id,class_name from class"
    cur.execute(classSql)
    classList = cur.fetchall()
    actSql = "select id,behavior_name from behavior"
    cur.execute(actSql)
    actList = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, "simulator.html",{"classList":classList,"actList":actList})

def getstudents(request):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
    cur = conn.cursor()
    classid = request.GET["class_id"]
    studentsql = "select id,student_name from student where class_id = "+classid
    cur.execute(studentsql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(list), content_type="application/json")

def getcurriculums(request):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
    cur = conn.cursor()
    classid = request.GET["class_id"]
    curriculumsql = "select curriculum.id,year,term,week,time,subject_name from curriculum,subject where subject_id = subject.id and class_id = "+classid
    cur.execute(curriculumsql)
    list = cur.fetchall()
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(list), content_type="application/json")

def addtestdata(request):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='ok', db='attendancesystem', port=3306, charset='utf8')
    cur = conn.cursor()
    classid = request.GET["classid"]
    studentid = request.GET["studentid"]
    curriculumid = request.GET["curriculumid"]
    actid = request.GET["actid"]
    # 添加异常行为的记录
    testdatasql = "insert into performance(curriculum_id,student_id,behavior_id,time,cycle,class_id) values("+curriculumid+","+studentid+","+actid+",\'testdate:2019-05-10\',1,"+classid+")"
    # 先拿出需要扣除的分数
    cur.execute("select behavior_score from behavior where id = "+actid)
    score = cur.fetchone()[0]

    updatestatisticssql =""
    # 更新统计表
    if(int(actid) <= 3):
        updatestatisticssql = "update statistics set absence_count = absence_count+1,score = score-"+str(score)+" where id = "+studentid
    else:
        updatestatisticssql = "update statistics set violation_count = violation_count+1,score = score-" +str(score) + " where id = " + studentid
    try:
        # 执行sql语句
        cur.execute(testdatasql)
        cur.execute(updatestatisticssql)
        # 提交到数据库执行
        conn.commit()

    except:
        # 如果发生错误则回滚
        conn.rollback()
        return HttpResponse("failed")
    finally:
        cur.close()
        conn.close()
    return HttpResponse("success")