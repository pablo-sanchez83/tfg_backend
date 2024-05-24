# Generated by Django 5.0.4 on 2024-05-23 08:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='tel',
            field=models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message="El número de teléfono debe ingresarse en el formato: '+9999999999'. Hasta 15 dígitos permitidos.", regex='^\\+?(\\d{1,3}[- ]?)?\\d{10}$'), django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(15)]),
        ),
    ]
