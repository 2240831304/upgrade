from django.http.response import JsonResponse

from guowen.response_code import CODE


def is_login(func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            context = {
                "code": CODE.LOGINERR,
                "msg": "请先登录",
                "data": {
                    "to_url": "/user/login"
                }
            }
            return JsonResponse(context)
        return func(request, *args, **kwargs)
    return wrapper