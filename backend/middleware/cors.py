rom django.utils.deprecation import MiddlewareMixin


# class MiddlewareMixin(object):
#     def __init__(self, get_response=None):
#         self.get_response = get_response
#         super(MiddlewareMixin, self).__init__()

#     def __call__(self, request):
#         response = None
#         if hasattr(self, 'process_request'):
#             response = self.process_request(request)
#         if not response:
#             response = self.get_response(request)
#         if hasattr(self, 'process_response'):
#             response = self.process_response(request, response)
#         return response


class CorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 允许你的域名来获取我的数据
        response['Access-Control-Allow-Origin'] = "*"

        # 允许你携带Content-Type请求头
        response['Access-Control-Allow-Headers'] = "Content-Type"

        # 允许你发送DELETE,PUT
        response['Access-Control-Allow-Methods'] = "GET,POST,OPTIONS,DELETE,PUT"

        return response
