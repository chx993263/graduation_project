import time
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def today():
    return time.strftime("%Y-%m-%d", time.localtime())
