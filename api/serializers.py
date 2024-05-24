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
    usuario = UsuariosSerializer(read_only=True)
    class Meta:
        model = Empresas
        fields = ['id', 'nombre', 'confirmado', 'usuario', 'localNum']

class CategoriasCulinariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias_Culinarias
        fields = ['id', 'nombre', 'descripcion']
class UsuariosEmpresasSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer
    usuario = UsuariosSerializer(read_only=True)
    class Meta:
        model = Usuarios
        fields = ['id', 'usuario', 'empresa']
        read_only_fields = ['empresa', 'usuario']

class LocalesSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer(read_only=True)
    empresa = EmpresasSerializer
    categoria_culinaria = CategoriasCulinariasSerializer

    class Meta:
        model = Locales
        fields = ['id', 'usuario', 'direccion', 'categoria_culinaria', 'empresa']
        read_only_fields = ['usuario', 'empresa', 'categoria_culinaria']

class HorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer
    class Meta:
        model = Horarios
        fields = ['id', 'local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']
        read_only_fields = ['local']

class FotosLocalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fotos_Locales
        fields = ['id', 'local', 'imagen']

class ProductosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = ['id', 'local', 'precio', 'nombre_producto', 'descripcion', 'categoria', 'imagen']

class TramosHorariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tramos_Horarios
        fields = ['id', 'local', 'h_inicio', 'h_final', 'nombre', 'clientes_maximos']

class ReservasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer(read_only=True)
    local = LocalesSerializer
    tramo_horario = TramosHorariosSerializer

    class Meta:
        model = Reservas
        fields = ['id', 'usuario', 'local', 'fecha', 'tramo_horario', 'hora', 'estado', 'numero_personas']

class ComentariosSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer(read_only=True)
    local = LocalesSerializer

    class Meta:
        model = Comentarios
        fields = ['id', 'usuario', 'local', 'fecha', 'comentario', 'estrellas', 'respuesta']