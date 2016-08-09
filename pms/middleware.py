
from django.shortcuts import HttpResponseRedirect
class LoginMiddleware(object):

    def process_request(self, request):

        if request.user.is_anonymous() and not str(request.path_info) == "/login/" and not str(request.path_info) == "/admin/":
            return HttpResponseRedirect('/login/')
        return None
