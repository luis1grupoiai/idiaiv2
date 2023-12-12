import os
from config.logging import *
from config.settings.base import *
from dotenv import load_dotenv

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'miproyecto'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '',
        'OPTIONS':{
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Configuración de LDAP

AD_SERVER = 'ldap://192.192.194.10'  # Cambia esto según tu servidor
AD_PORT = 389  # El puerto por defecto es 389
AD_USER = 'CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx'  # Cambia esto según tus credenciales
#dsquery user -name desarrollo
#dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD = 'D3sarrollo'
LOGIN_REDIRECT_URL = 'home' 
LOGOUT_REDIRECT_URL = 'home'

