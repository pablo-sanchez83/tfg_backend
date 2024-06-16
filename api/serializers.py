from rest_framework import serializers
from api.models import *

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'tel', 'rol', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Hacer que el campo de contraseña sea solo de escritura

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])  # Encriptar la contraseña
        user.save()  # Guardar el usuario en la base de datos
        return user

class EmpresasSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer  # Incluir el serializador de Usuarios

    class Meta:
        model = Empresas
        fields = ['id', 'nombre', 'confirmado', 'usuario', 'localNum']

class CategoriasCulinariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias_Culinarias
        fields = ['id', 'nombre', 'descripcion']

class UsuariosEmpresasSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer  # Incluir el serializador de Empresas
    usuario = UsuariosSerializer  # Incluir el serializador de Usuarios

    class Meta:
        model = Usuarios
        fields = ['id', 'usuario', 'empresa']

class LocalesSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer  # Incluir el serializador de Usuarios
    empresa = EmpresasSerializer  # Incluir el serializador de Empresas
    categoria_culinaria = CategoriasCulinariasSerializer  # Incluir el serializador de Categorías Culinarias

    class Meta:
        model = Locales
        fields = ['id', 'nombre', 'usuario', 'direccion', 'categoria_culinaria', 'empresa']

class HorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer  # Incluir el serializador de Locales

    class Meta:
        model = Horarios
        fields = ['id', 'local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']

class FotosLocalesSerializer(serializers.ModelSerializer):
    local = LocalesSerializer  # Incluir el serializador de Locales

    class Meta:
        model = Fotos_Locales
        fields = ['id', 'local', 'imagen']

class ProductosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer  # Incluir el serializador de Locales

    class Meta:
        model = Productos
        fields = ['id', 'local', 'precio', 'nombre_producto', 'descripcion', 'categoria', 'imagen']

class TramosHorariosSerializer(serializers.ModelSerializer):
    local = LocalesSerializer  # Incluir el serializador de Locales

    class Meta:
        model = Tramos_Horarios
        fields = ['id', 'local', 'h_inicio', 'h_final', 'nombre', 'clientes_maximos']

class ReservasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservas
        fields = ['id', 'usuario', 'local', 'fecha', 'hora', 'tramo_horario', 'estado', 'numero_personas']

    def create(self, validated_data):
        return Reservas.objects.create(**validated_data)  # Crear y retornar una nueva instancia de Reservas

class ReservasSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Reservas
        fields = ['id', 'usuario', 'local', 'fecha', 'hora', 'tramo_horario', 'estado', 'numero_personas']
        depth = 1  # Incluir relaciones anidadas

class ComentariosSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer  # Incluir el serializador de Usuarios
    local = LocalesSerializer  # Incluir el serializador de Locales
    respuesta_a = serializers.PrimaryKeyRelatedField(queryset=Comentarios.objects.all(), required=False, allow_null=True)  # Relación con la respuesta

    class Meta:
        model = Comentarios
        fields = ['id', 'usuario', 'local', 'fecha', 'comentario', 'estrellas', 'respuesta', 'respuesta_a']

class ComentariosSerializerAll(serializers.ModelSerializer):
    usuario = UsuariosSerializer  # Incluir el serializador de Usuarios
    local = LocalesSerializer  # Incluir el serializador de Locales
    respuestas = serializers.SerializerMethodField()  # Campo para incluir respuestas

    class Meta:
        model = Comentarios
        fields = ['id', 'usuario', 'local', 'fecha', 'comentario', 'estrellas', 'respuesta', 'respuestas']

    def get_respuestas(self, obj):
        serializer = ComentariosSerializerAll(obj.respuestas.all(), many=True)  # Serializar las respuestas
        return serializer.data  # Devolver los datos serializados
