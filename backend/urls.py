from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Definición de las rutas de la aplicación
urlpatterns = [
    # Ruta para la administración de Django
    path('admin/', admin.site.urls),
    # Ruta para las URLs de la aplicación 'api'
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Configuración para servir archivos estáticos y de medios
