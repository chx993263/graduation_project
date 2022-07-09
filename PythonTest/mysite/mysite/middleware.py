from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
import json


try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x

class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 非指定网址需要进行验证 and request.path != '/index/'
        if request.path != '/login/':
            # 如果session中没有用户则说明没有登陆，需要返回登录界面重新登录
            # 这边有一个问题，在跳转index页面的时候实现进行拦截器后进行相关函数逻辑的实现的，对对象进行获取会导致报错，所以这边判断是否为POST请求
            if(request.session.get('adminName') != None or request.method == "POST"):
                # 如果有值，则不进行拦截，放行。
                pass
            else:
                # 没有值，则说明session已下线或者进行非正常访问
                return HttpResponseRedirect('/login/')
                # return render(request, "login.html", {"msg": json.dumps('logout')})