import os
from pathlib import Path
import environ
import dj_database_url

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicialización de las variables de entorno
env = environ.Env()
environ.Env.read_env()

# Clave secreta para la autenticación
SECRET_KEY = env('SECRET_KEY')
# Modo de depuración activado
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ['web-production-6e7ec.up.railway.app']

# Configuración de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'api',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
]

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Middlewares
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.RefererControlMiddleware'
]

# Orígenes permitidos para CORS
CORS_ALLOWED_ORIGINS = [
    'https://eatbook.vercel.app'
]
# Orígenes de confianza para CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://eatbook.vercel.app'
]

# URL de configuración principal
ROOT_URLCONF = 'backend.urls'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'api.Usuarios'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicación WSGI
WSGI_APPLICATION = 'backend.wsgi.application'

# Configuración de la base de datos
DATABASES = {
    "default": dj_database_url.config(default=env('DATABASE_URL'))
}

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración de archivos estáticos
STATIC_URL = 'static/'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

# Configuración de internacionalización
USE_I18N = True

# Configuración de uso de zona horaria
USE_TZ = True

# Configuración del campo de auto-incremento predeterminado
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
