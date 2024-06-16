from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.core.validators import MaxLengthValidator, RegexValidator, MinLengthValidator
from .managers import CustomUserManager
from django_resized import ResizedImageField

# Extender el modelo de usuario predeterminado
class Usuarios(AbstractUser, PermissionsMixin):
    class Rol(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        CLIENTE = 2, 'Cliente'
        ENCARGADO = 3, 'Encargado'
        EMPRESARIO = 4, 'Empresario'

    phone_regex = RegexValidator(
        regex=r"^\d{1,4}-\d{7,10}$",
        message="El número de teléfono debe ingresarse en el formato: '9999-9999999999'. Hasta 15 dígitos permitidos."
    )
    email = models.EmailField(unique=True)  # Email debe ser único
    tel = models.CharField(validators=[phone_regex, MinLengthValidator(10), MaxLengthValidator(15)], max_length=16)  # Validadores para el teléfono
    rol = models.IntegerField(choices=Rol.choices)  # Rol del usuario

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'tel', 'rol', 'password', 'username']

    objects = CustomUserManager()  # Administrador de usuarios personalizado

    groups = models.ManyToManyField(Group, related_name='customuser_set')  # Relaciones de grupos personalizadas
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')  # Relaciones de permisos personalizadas

    def __str__(self):
        return self.email  # Representación en string del usuario

class Empresas(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre de la empresa
    confirmado = models.BooleanField(default=False)  # Estado de confirmación
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='empresas')  # Relación con usuario
    localNum = models.IntegerField(default=0)  # Número local

    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre  # Representación en string de la empresa

class Categorias_Culinarias(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre de la categoría culinaria
    descripcion = models.TextField()  # Descripción de la categoría culinaria

    REQUIRED_FIELDS = ['nombre', 'description']

    def __str__(self):
        return self.nombre  # Representación en string de la categoría culinaria

class Locales(models.Model):
    nombre = models.CharField(max_length=100, null=True)  # Nombre del local
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='locales', null=True)  # Relación con usuario
    direccion = models.CharField(max_length=255)  # Dirección del local
    categoria_culinaria = models.ForeignKey(Categorias_Culinarias, on_delete=models.CASCADE, related_name='locales', null=True)  # Relación con categoría culinaria
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE, related_name='locales', null=True)  # Relación con empresa

    REQUIRED_FIELDS = ['nombre', 'direccion', 'categoria_culinaria', 'empresa']

    def __str__(self):
        return self.nombre  # Representación en string del local

class Horarios(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='horarios', null=True)  # Relación con local
    hora_apertura = models.TimeField()  # Hora de apertura
    hora_cierre = models.TimeField()  # Hora de cierre
    L = models.BooleanField(default=False)  # Lunes
    M = models.BooleanField(default=False)  # Martes
    X = models.BooleanField(default=False)  # Miércoles
    J = models.BooleanField(default=False)  # Jueves
    V = models.BooleanField(default=False)  # Viernes
    S = models.BooleanField(default=False)  # Sábado
    D = models.BooleanField(default=False)  # Domingo

    REQUIRED_FIELDS = ['local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']

class Fotos_Locales(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='fotos')  # Relación con local
    imagen = ResizedImageField(force_format="WEBP", quality=50, upload_to='fotos_locales/')  # Imagen redimensionada del local

class Productos(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='productos')  # Relación con local
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del producto
    nombre_producto = models.CharField(max_length=100)  # Nombre del producto
    descripcion = models.TextField()  # Descripción del producto
    categoria = models.CharField(max_length=100, null=True)  # Categoría del producto
    imagen = ResizedImageField(force_format="WEBP", quality=50, upload_to='productos_imagenes/')  # Imagen redimensionada del producto

    def __str__(self):
        return self.nombre_producto + ' - ' + self.categoria  # Representación en string del producto

class Tramos_Horarios(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='tramos_horarios')  # Relación con local
    h_inicio = models.TimeField()  # Hora de inicio del tramo
    h_final = models.TimeField()  # Hora final del tramo
    nombre = models.CharField(max_length=100)  # Nombre del tramo horario
    clientes_maximos = models.IntegerField()  # Número máximo de clientes

class Reservas(models.Model):
    class Estado(models.IntegerChoices):
        PENDIENTE = 1, 'Pendiente'
        ACEPTADA = 2, 'Aceptada'
        RECHAZADA = 3, 'Rechazada'

    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='reservas')  # Relación con usuario
    local = models.ForeignKey(Locales, on_delete=models.CASCADE)  # Relación con local
    fecha = models.DateField()  # Fecha de la reserva
    tramo_horario = models.ForeignKey(Tramos_Horarios, on_delete=models.SET_NULL, null=True)  # Relación con tramo horario
    hora = models.TimeField()  # Hora de la reserva
    estado = models.IntegerField(choices=Estado.choices)  # Estado de la reserva
    numero_personas = models.IntegerField()  # Número de personas en la reserva

class Comentarios(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='comentarios')  # Relación con usuario
    local = models.ForeignKey(Locales, on_delete=models.CASCADE)  # Relación con local
    fecha = models.DateField(auto_now_add=True)  # Fecha del comentario
    comentario = models.TextField(blank=True)  # Texto del comentario
    estrellas = models.IntegerField()  # Calificación con estrellas
    respuesta = models.BooleanField(default=False)  # Indicador de respuesta
    respuesta_a = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')  # Relación con comentario respondido

    def __str__(self):
        return self.comentario  # Representación en string del comentario