from rest_framework import serializers
from api.models import *

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'tel', 'rol', 'last_login', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Eliminar la contraseña del diccionario validado antes de crear el usuario
        password = validated_data.pop('password')
        user = Usuarios.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmpresasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    class Meta:
        model = Empresas
        fields = ['id', 'nombre', 'confirmado', 'usuario', 'localNum']
        depth = 1

class CategoriasCulinariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias_Culinarias
        fields = ['id', 'nombre', 'descripcion']
class UsuariosEmpresasSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer
    usuario = UsuariosSerializer
    class Meta:
        model = Usuarios
        fields = ['id', 'usuario', 'empresa']
        depth = 1
class LocalesSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    empresa = EmpresasSerializer
    categoria_culinaria = CategoriasCulinariasSerializer

    class Meta:
        model = Locales
        fields = ['id', 'usuario', 'direccion', 'categoria_culinaria', 'empresa']
        depth = 1

class HorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Horarios
        fields = ['id', 'local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']
        depth = 1

class FotosLocalesSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Fotos_Locales
        fields = ['id', 'local', 'imagen']
        depth = 1

class ProductosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Productos
        fields = ['id', 'local', 'precio', 'nombre_producto', 'descripcion', 'categoria', 'imagen']
        depth = 1

class TramosHorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Tramos_Horarios
        fields = ['id', 'local', 'h_inicio', 'h_final', 'nombre', 'clientes_maximos']
        depth = 1

class ReservasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    local = LocalesSerializer
    tramo_horario = TramosHorariosSerializer

    class Meta:
        model = Reservas
        fields = ['id', 'usuario', 'local', 'fecha', 'tramo_horario', 'hora', 'estado', 'numero_personas']
        depth = 1

class ComentariosSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    local = LocalesSerializer

    class Meta:
        model = Comentarios
        fields = ['id', 'usuario', 'local', 'fecha', 'comentario', 'estrellas', 'respuesta']
        depth = 1