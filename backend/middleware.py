from django.http import HttpResponseForbidden

class RefererControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        referer = request.META.get('HTTP_REFERER')
        if referer and not referer.startswith('https://eatbook.vercel.app'):
            return HttpResponseForbidden('Forbidden: Invalid Referer')
        response = self.get_response(request)
        return response
