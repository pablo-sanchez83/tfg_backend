from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.core.validators import MaxLengthValidator, RegexValidator, MinLengthValidator
from .managers import CustomUserManager
# Extender el modelo de usuario predeterminado

class Usuarios(AbstractUser, PermissionsMixin):
    class Rol(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        CLIENTE = 2, 'Cliente'
        ENCARGADO = 3, 'Encargado'
        EMPRESARIO = 4, 'Empresario'
    phone_regex = RegexValidator(
    regex=r"^\d{1,4}-\d{7,10}$",
    message="El número de teléfono debe ingresarse en el formato: '+9999999999'. Hasta 15 dígitos permitidos."
    )
    email = models.EmailField(unique=True)
    tel = models.CharField(validators=[phone_regex, MinLengthValidator(10), MaxLengthValidator(15)], max_length=16)
    rol = models.IntegerField(choices=Rol.choices)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'tel', 'rol', 'password', 'username']

    objects = CustomUserManager()

    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')

    def __str__(self):
        return self.email

class Empresas(models.Model):
    nombre = models.CharField(max_length=100)
    confirmado = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='empresas')
    localNum = models.IntegerField(default=0)

    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre

class Categorias_Culinarias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    REQUIRED_FIELDS = ['nombre', 'description']

    def __str__(self):
        return self.nombre    
class Locales(models.Model):
    nombre = models.CharField(max_length=100, null=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='locales', null=True)
    direccion = models.CharField(max_length=255)
    categoria_culinaria = models.ForeignKey(Categorias_Culinarias, on_delete=models.CASCADE,related_name='locales', null=True)
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE, related_name='locales', null=True)

    REQUIRED_FIELDS = ['nombre', 'direccion', 'categoria_culinaria']

    def __str__(self):
        return self.nombre
class Horarios(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='horarios', null=True)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    L = models.BooleanField(default=False)
    M = models.BooleanField(default=False)
    X = models.BooleanField(default=False)
    J = models.BooleanField(default=False)
    V = models.BooleanField(default=False)
    S = models.BooleanField(default=False)
    D = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['local', 'hora_apertura', 'hora_cierre', 'L', 'M', 'X', 'J', 'V', 'S', 'D']

class Fotos_Locales(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='fotos_locales/')

class Productos(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100, null=True)
    imagen = models.ImageField(upload_to='productos_imagenes/')
    def __str__(self):
        return self.nombre_producto + ' - ' + self.categoria

class Tramos_Horarios(models.Model):
    local = models.ForeignKey(Locales, on_delete=models.CASCADE, related_name='tramos_horarios')
    h_inicio = models.TimeField()
    h_final = models.TimeField()
    nombre = models.CharField(max_length=100)
    clientes_maximos = models.IntegerField()

class Reservas(models.Model):
    class Estado(models.IntegerChoices):
        PENDIENTE = 1, 'Pendiente'
        ACEPTADA = 2, 'Aceptada'
        RECHAZADA = 3, 'Rechazada'
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='reservas')
    local = models.ForeignKey(Locales, on_delete=models.CASCADE)
    fecha = models.DateField()
    tramo_horario = models.ForeignKey(Tramos_Horarios, on_delete=models.SET_NULL, null=True)
    hora = models.TimeField()
    estado = models.IntegerField(choices=Estado.choices)
    numero_personas = models.IntegerField()

class Comentarios(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='comentarios')
    local = models.ForeignKey(Locales, on_delete=models.CASCADE)
    fecha = models.DateField()
    comentario = models.TextField(blank=True)
    estrellas = models.IntegerField()
    respuesta = models.BooleanField(default=False)