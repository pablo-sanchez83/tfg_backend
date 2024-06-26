# Generated by Django 5.0.4 on 2024-05-22 20:50

import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorias_Culinarias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('tel', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message="El número de teléfono debe ingresarse en el formato: '+999999999'. Hasta 15 dígitos permitidos.", regex='^\\+?1?\\d{9,15}$'), django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(15)])),
                ('rol', models.IntegerField(choices=[(1, 'Admin'), (2, 'Cliente'), (3, 'Encargado'), (4, 'Empresario')])),
                ('groups', models.ManyToManyField(related_name='customuser_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(related_name='customuser_set', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Empresas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('confirmado', models.BooleanField(default=False)),
                ('localNum', models.IntegerField(default=0)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='empresas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Locales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, null=True)),
                ('direccion', models.CharField(max_length=255)),
                ('categoria_culinaria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='api.categorias_culinarias')),
                ('empresa', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='api.empresas')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locales', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Horarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hora_apertura', models.TimeField()),
                ('hora_cierre', models.TimeField()),
                ('L', models.BooleanField(default=False)),
                ('M', models.BooleanField(default=False)),
                ('X', models.BooleanField(default=False)),
                ('J', models.BooleanField(default=False)),
                ('V', models.BooleanField(default=False)),
                ('S', models.BooleanField(default=False)),
                ('D', models.BooleanField(default=False)),
                ('local', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='api.locales')),
            ],
        ),
        migrations.CreateModel(
            name='Fotos_Locales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='fotos_locales/')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='api.locales')),
            ],
        ),
        migrations.CreateModel(
            name='Comentarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('comentario', models.TextField(blank=True)),
                ('estrellas', models.IntegerField()),
                ('respuesta', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to=settings.AUTH_USER_MODEL)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locales')),
            ],
        ),
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nombre_producto', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('categoria', models.CharField(max_length=100, null=True)),
                ('imagen', models.ImageField(upload_to='productos_imagenes/')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='api.locales')),
            ],
        ),
        migrations.CreateModel(
            name='Tramos_Horarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('h_inicio', models.TimeField()),
                ('h_final', models.TimeField()),
                ('nombre', models.CharField(max_length=100)),
                ('clientes_maximos', models.IntegerField()),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tramos_horarios', to='api.locales')),
            ],
        ),
        migrations.CreateModel(
            name='Reservas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('estado', models.IntegerField(choices=[(1, 'Pendiente'), (2, 'Aceptada'), (3, 'Rechazada')])),
                ('numero_personas', models.IntegerField()),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locales')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to=settings.AUTH_USER_MODEL)),
                ('tramo_horario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.tramos_horarios')),
            ],
        ),
    ]
