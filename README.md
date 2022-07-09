一般情况下，部署python项目直接执行 python xxx.py 即可，不过这样部署非常不成熟。
存在以下弊端：
1、性能非常一般
2、不方便记录日志
3、不能后台运行

# 推荐使用 pipenv

```python
# Pipfile
jinja2 = "==3.0.3"
gunicorn = "==20.1.0"
supervisor = "==4.2.4"
Werkzeug = "~=2.0.0"
bcrypt = "==3.1.7"
```

# gunicorn
### 为什么要用 gunicorn
**gunicorn一个被广泛使用的高性能的python WSGI UNIX HTTP服务器,Gunicorn是主流的WSGI容器之一，它易于配置，兼容性好，CPU消耗很少.**

gunicorn 命令
```bash
-c CONFIG, --config=CONFIG
# 设定配置文件。
-b BIND, --bind=BIND
# 设定服务需要绑定的端口。建议使用HOST:PORT
-w WORKERS, --workers=WORKERS
# 设置工作进程数。建议服务器每一个核心可以设置2-4个。
-k MODULE
# 选定异步工作方式使用的模块。
```

```python
运行命令：
pipenv run gunicorn --workers=4 --bind=0.0.0.0:62323 wsgi:app
wsgi:app -> 执行文件：入口函数（本来我是app.py，但是执行有些问题）
```

# supervisor
supervisor是一个python开发的进程管理工具，不光可以管理python项目，java项目，php-pfm后台启动程序都可以管理哦
执行命令：
```bash
# 加载一个 config模版，然后把下边这个配置复制过去即可
pipenv run supervisord -c supervisor.conf
# 修改配置
supervisorctl -c ./supervisor.conf status
supervisorctl -c ./supervisor.conf start all

```
supervisor.conf 添加配置
```bash
[program:{package_name}]
directory = %(here)s
command = pipenv run gunicorn --workers=4 --bind=0.0.0.0:62323 wsgi:app
autostart = true
startsecs = 5
autorestart = true
startretries = 3
redirect_stderr = true
stdout_logfile_maxbytes = 200000000
stdout_logfile_backups = 5
stdout_logfile = %(here)s/wsgi.log
```
执行 supervisorctl -c ./supervisor.conf status 查看运行状态
![在这里插入图片描述](https://img-blog.csdnimg.cn/4560a501045f43b7a772794cce0bbe44.png)
如果成功运行了，就是这样，可以查看 wsgi.log的执行日志查看具体细节。
