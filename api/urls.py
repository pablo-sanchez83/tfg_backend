from django.urls import path, re_path
from api.views import *
urlpatterns = [
    path('login', login),
    path('register', signup),
    path('logout', logout),
    path("mi_usuario", mi_usuario),
    path('usuario/<int:pk>', DetailedUsers.as_view(), name='user-detail'),
    path('usuarios', ListUsers.as_view(), name='users-list'),
    path('empresas', ListEmpresas.as_view(), name='empresas-list'),
    path('empresa/<int:pk>', DetailedEmpresas.as_view(), name='empresas-detail'),
    path('categorias_culinarias', ListCategoriasCulinarias.as_view(), name='categorias-culinarias-list'),
    path('categoria_culinaria/<int:pk>', DetailedCategoriasCulinarias.as_view(), name='categorias-culinarias-detail'),
    path('locales', get_locales, name='locales-list'),
    path('locales/empresa/<int:id>', get_locales_empresas, name='locales-empresas-list'),
    path('local/<int:id>', get_local, name='locales-detail'),
    path('crear_local', CrearLocales.as_view(), name='locales-create'),
    path('horarios', ListHorarios.as_view(), name='horarios-list'),
    path('fotos_locales', ListFotosLocales.as_view(), name='fotos-locales-list'),
    path('foto_local/<int:pk>/local/<int:local>', DetailedFotosLocales.as_view(), name='fotos-locales-detail'),
    path('productos', ListProductos.as_view(), name='productos-list'),
    path('producto/<int:pk>/local/<int:local>', DetailedProductos.as_view(), name='productos-detail'),
    path('tramos_horarios', ListTramosHorarios.as_view(), name='tramos-horarios-list'),
    path('tramos_horarios/<int:local>', get_tramos_horarios_local, name='tramos-horarios-list'),
    path('tramo_horario/<int:pk>/local/<int:local>', DetailedTramosHorarios.as_view(), name='tramos-horarios-detail'),
    path('reservas/local/<int:local>', get_reservas, name='reservas-list'),
    path('reserva/crear', crear_reserva, name='reservas-create'),
    path('reserva/<int:pk>/local/<int:local>', DetailedReservas.as_view(), name='reservas-detail'),
    path('crear_comentarios/local/<int:local>', CrearComentario.as_view(), name='comentarios-list'),
    path('comentario/<int:pk>', DetailedComentarios.as_view(), name='comentarios-detail'),
    path('mis_reservas', get_reservas_cliente, name='mis-reservas'),
    path('cancelar_reserva/<int:pk>', cancelar_reserva, name='cancelar-reserva'),
    path('eliminar_reserva/<int:pk>', delete_reserva, name='eliminar-reserva'),
    path('eliminar_reserva/local/<int:pk>', delete_reserva_as_local, name='eliminar-reserva'),
    path('mi_local', get_mi_local, name='mi-local'),
    path('eliminar_local/<int:id>', delete_local, name='eliminar-local'),
]  