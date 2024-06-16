from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Administrador de usuarios personalizado para este proyecto.
    """
    def create_user(self, username, first_name, last_name, email, password, tel, rol, **extra_fields):
        """
        Crear y guardar un usuario con el email y password proporcionado.
        """
        if not email:
            raise ValueError('Debes introducir un email')  # Verificar que el email sea proporcionado
        email = self.normalize_email(email)  # Normalizar el email
        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            tel=tel,
            rol=rol,
            **extra_fields
        )
        user.set_password(password)  # Establecer la contraseña del usuario
        user.save(using=self._db)  # Guardar el usuario en la base de datos
        return user

    def create_superuser(self, username, first_name, last_name, email, password, tel, **extra_fields):
        """
        Crear y guardar un super usuario con el email y password proporcionado.
        """
        extra_fields.setdefault('is_staff', True)  # Establecer is_staff a True por defecto
        extra_fields.setdefault('is_superuser', True)  # Establecer is_superuser a True por defecto
        extra_fields.setdefault('is_active', True)  # Establecer is_active a True por defecto
        extra_fields.setdefault('rol', 1)  # Añadir rol aquí
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super usuario debe tener is_staff=True.')  # Validar que is_staff sea True
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super usuario debe tener is_superuser=True.')  # Validar que is_superuser sea True

        return self.create_user(username, first_name, last_name, email, password, tel, **extra_fields)  # Crear y retornar el superusuario