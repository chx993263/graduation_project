import time
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def today():
    return time.strftime("%Y-%m-%d", time.localtime())
def year():
    return time.strftime("%Y", time.localtime())
def month():
    return time.strftime("%m", time.localtime())
def day():
    return time.strftime("%d", time.localtime())
