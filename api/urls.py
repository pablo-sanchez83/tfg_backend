from django.urls import path, re_path
from api.views import *
urlpatterns = [
    path('login', login),
    path('register', signup),
    path('logout', logout),
    path('usuario/<int:pk>', DetailedUsers.as_view(), name='user-detail'),
    path('usuarios', ListUsers.as_view(), name='users-list'),
    path('empresas', ListEmpresas.as_view(), name='empresas-list'),
    path('empresa/<int:pk>', DetailedEmpresas.as_view(), name='empresas-detail'),
    path('categorias_culinarias', ListCategoriasCulinarias.as_view(), name='categorias-culinarias-list'),
    path('categoria_culinaria/<int:pk>', DetailedCategoriasCulinarias.as_view(), name='categorias-culinarias-detail'),
    path('locales', ListLocales.as_view(), name='locales-list'),
    path('local/<int:pk>', DetailedLocales.as_view(), name='locales-detail'),
    path('horarios', ListHorarios.as_view(), name='horarios-list'),
    path('horario/<int:pk>/local/<int:local>', DetailedHorarios.as_view(), name='horarios-detail'),
    path('fotos_locales', ListFotosLocales.as_view(), name='fotos-locales-list'),
    path('foto_local/<int:pk>/local/<int:local>', DetailedFotosLocales.as_view(), name='fotos-locales-detail'),
    path('productos', ListProductos.as_view(), name='productos-list'),
    path('producto/<int:pk>/local/<int:local>', DetailedProductos.as_view(), name='productos-detail'),
    path('tramos_horarios', ListTramosHorarios.as_view(), name='tramos-horarios-list'),
    path('tramo_horario/<int:pk>/local/<int:local>', DetailedTramosHorarios.as_view(), name='tramos-horarios-detail'),
    path('reservas', ListReservas.as_view(), name='reservas-list'),
    path('reserva/<int:pk>/local/<int:local>', DetailedReservas.as_view(), name='reservas-detail'),
    path('comentarios/local/<int:local>', ListComentarios.as_view(), name='comentarios-list'),
    path('comentario/<int:pk>', DetailedComentarios.as_view(), name='comentarios-detail'),
]