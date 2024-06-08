# Generated by Django 5.0.4 on 2024-06-02 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_usuarios_tel'),
    ]

    operations = [
        migrations.AddField(
            model_name='comentarios',
            name='respuesta_a',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='api.comentarios'),
        ),
        migrations.AlterField(
            model_name='comentarios',
            name='fecha',
            field=models.DateField(auto_now_add=True),
        ),
    ]