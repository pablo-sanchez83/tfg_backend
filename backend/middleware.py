from django.http import HttpResponseForbidden

# Middleware para controlar el Referer de las solicitudes
class RefererControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtener el referer de los metadatos de la solicitud
        referer = request.META.get('HTTP_REFERER')
        # Verificar si el referer es válido
        if referer and not referer.startswith('https://eatbook.vercel.app'):
            return HttpResponseForbidden('Prohibido: Referer inválido')
        # Obtener la respuesta para la solicitud
        response = self.get_response(request)
        return response
