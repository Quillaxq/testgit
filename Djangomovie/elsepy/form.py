from django.utils.deprecation import MiddlewareMixin
from user.models import users


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        username = request.session.get('username', 0)
        # ͨ��session�б����user��ѯ���û�����
        user_obj = users.objects.filter(username=username).first()
        # ���û�����ֵ��request.login_user,ģ����ֻ���ж�request.login_user����
        request.login_user = user_obj
