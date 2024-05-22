from django.contrib import admin
from api.models import *

# Register your models here.
admin.site.register(Usuarios)
admin.site.register(Empresas)
admin.site.register(Categorias_Culinarias)
admin.site.register(Locales)
admin.site.register(Horarios)
admin.site.register(Fotos_Locales)
admin.site.register(Productos)
admin.site.register(Tramos_Horarios)
admin.site.register(Reservas)
admin.site.register(Comentarios)