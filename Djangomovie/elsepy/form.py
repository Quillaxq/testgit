from django.utils.deprecation import MiddlewareMixin
from user.models import users


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        username = request.session.get('username', 0)
        # 通过session中保存的user查询到用户对象
        user_obj = users.objects.filter(username=username).first()
        # 将用户对象赋值给request.login_user,模板中只需判断request.login_user即可
        request.login_user = user_obj
