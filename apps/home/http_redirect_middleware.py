from django.http import HttpResponsePermanentRedirect

class HttpRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.is_secure():
            new_url = "http://" + request.get_host() + request.get_full_path()
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)
