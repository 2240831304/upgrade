from django.conf import settings
from django.shortcuts import reverse
from django.utils.deprecation import MiddlewareMixin


class SWFUploadMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (request.method == 'POST') and (request.path == reverse('pack:pack_upload')) and \
                request.POST.get(settings.SESSION_COOKIE_NAME,''):
            request.COOKIES[settings.SESSION_COOKIE_NAME] = request.POST[settings.SESSION_COOKIE_NAME]
        if request.POST.get('csrftoken',''):
            request.COOKIES['csrftoken'] = request.POST['csrftoken']