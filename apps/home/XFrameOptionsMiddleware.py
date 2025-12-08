from django.utils.deprecation import MiddlewareMixin

class DisableXFrameOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']
        return response

class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = (
            "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval';"
            "style-src 'self' 'unsafe-inline';"
        )
        return response
