from django.utils.deprecation import MiddlewareMixin
import jwt
from datetime import *
from django.http import HttpResponse, JsonResponse
from document_management_system.settings import SECRET_KEY


class AuthorizeToken(MiddlewareMixin):
    def process_request(self, request):
        print("中间件 process_request方法被调用！")
        path = request.path
        notAuthorizeUrls = ["/User/Login", "/User/Validate", "/User/FaceRecognitionLogin"]
        if path not in notAuthorizeUrls:
            token = request.META.get("HTTP_AUTHORIZATION")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                # print(payload)
            except Exception as e:
                # 如果 jwt 被篡改过; 或者算法不正确; 如果设置有效时间, 过了有效期; 或者密钥不相同; 都会抛出相应的异常
                print(e)
                return HttpResponse(status=403)