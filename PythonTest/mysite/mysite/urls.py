from django.contrib import admin
from django.urls import path
from . import view


urlpatterns = [
    path('admin/', admin.site.urls),
    # 登录界面
    path("login/", view.login),
    # 主页
    path("index/", view.index),
    # 操作日志
    path("index/work.html", view.worklog),
    # 批量删除日志
    path("index/dellogs", view.dellogs),
    # 单个删除
    path("index/dellog", view.dellog),

    path("index/modifypwd", view.modifypwd),
    path("index/home.html", view.home),

    path("index/absence.html", view.absence),
    path("index/mesage.html", view.mesage),


    path("index/schedule.html", view.schedule),
    # 课表管理
    path("index/curriculum.html", view.curriculum),
    path("index/curriculum_tail", view.curriculum_tail),
    path("index/updatecurriculum", view.updatecurriculum),
    path("index/curriculum_add", view.curriculum_add),
    path("index/addcurriculum", view.addcurriculum),
    # 注销课程 delcurl
    path("index/delcurl", view.delcurl),
    # 课程表
    path("index/getKecheng", view.getKecheng),


    path("index/mailList.html", view.mailList),

    # 通告
    path("index/notice.html", view.notice),
    # 批量删除通告
    path("index/delacts", view.delacts),
    # 单个删除
    path("index/delact", view.delact),



    # student 请求地址
    path("index/student.html", view.student),
    path("index/student_tail", view.student_tail),
    path("index/student_add.html", view.student_add),
    path("index/addstudent", view.addstudent),
    path("index/delstudent", view.delstudent),
    path("index/updatestudent", view.updatestudent),
    path("index/studenttoupdate", view.studenttoupdate),

    # teacher 请求地址
    path("index/teacher.html", view.teacher),
    path("index/teacher_tail", view.teacher_tail),
    path("index/teacher_add.html", view.teacher_add),
    path("index/addteacher", view.addteacher),
    path("index/delteacher", view.delteacher),
    path("index/updateteacher", view.updateteacher),
    path("index/teachertoupdate", view.teachertoupdate),

    # class 请求地址
    path("index/class.html", view.classes),
    path("index/class_tail.html", view.class_tail),
    path("index/addclass", view.addclass),
    path("index/delclass", view.delclass),
    path("index/updateclass", view.updateclass),
    path("index/classtoupdate", view.classtoupdate),

    # subject 请求地址
    path("index/subject.html", view.subject),
    path("index/subject_tail.html", view.subject_tail),
    path("index/addsubject", view.addsubject),
    path("index/delsubject", view.delsubject),
    path("index/updatesubject", view.updatesubject),
    path("index/subjecttoupdate", view.subjecttoupdate),

    # behavior 请求地址
    path("index/behavior.html", view.behavior),
    path("index/behavior_tail.html", view.behavior_tail),
    path("index/addbehavior", view.addbehavior),
    path("index/delbehavior", view.delbehavior),
    path("index/updatebehavior", view.updatebehavior),
    path("index/behaviortoupdate", view.behaviortoupdate),




    path("index/calendar.html", view.calendar),


    path("index/behavior_tail.html", view.behavior_tail),

    path("index/login.html", view.login),







    path("index/success", view.success),









]
