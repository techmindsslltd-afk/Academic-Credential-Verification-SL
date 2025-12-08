# myapp/middleware.py

from django.http import HttpResponseForbidden

ALLOWED_IP_ADDRESSES = ['bank_ipv4_address', 'bank_ipv6_address']

class IPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if ip not in ALLOWED_IP_ADDRESSES:
            return HttpResponseForbidden("Forbidden: Your IP address is not allowed.")
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
# http://127.0.0.1:8000/api/applicationpins/<pin_id>/
# http://127.0.0.1:8000/api/applicationpins/