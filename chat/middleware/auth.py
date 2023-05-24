from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class sessionAuthentication(MiddlewareMixin):
    def process_request(self, request):
        if request.path not in ['/login/', '/register/']:
            if request.session.get('user'):
                return
            else:
                return redirect('login')
