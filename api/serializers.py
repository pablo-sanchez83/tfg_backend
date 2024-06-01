from rest_framework import serializers
from api.models import *


class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'tel', 'rol', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class EmpresasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    class Meta:
        model = Empresas
        fields = ['id', 'nombre', 'confirmado', 'usuario', 'localNum']

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
class LocalesSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    empresa = EmpresasSerializer
    categoria_culinaria = CategoriasCulinariasSerializer

    class Meta:
        model = Locales
        fields = ['id', 'nombre', 'usuario', 'direccion', 'categoria_culinaria', 'empresa']

class HorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Horarios
        fields = ['id', 'local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']

class FotosLocalesSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Fotos_Locales
        fields = ['id', 'local', 'imagen']

class ProductosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Productos
        fields = ['id', 'local', 'precio', 'nombre_producto', 'descripcion', 'categoria', 'imagen']

class TramosHorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Tramos_Horarios
        fields = ['id', 'local', 'h_inicio', 'h_final', 'nombre', 'clientes_maximos']

class ReservasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    local = LocalesSerializer
    tramo_horario = TramosHorariosSerializer

    class Meta:
        model = Reservas
        fields = ['id', 'usuario', 'local', 'fecha', 'tramo_horario', 'hora', 'estado', 'numero_personas']

class ComentariosSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer
    local = LocalesSerializer

    class Meta:
        model = Comentarios
        fields = ['id', 'usuario', 'local', 'fecha', 'comentario', 'estrellas', 'respuesta']