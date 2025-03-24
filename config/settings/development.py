import os
from config.logging import *
from config.settings.base import *
from dotenv import load_dotenv

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'miproyecto'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['grupo-iai.com.mx', 'www.grupo-iai.com.mx', 'iaipc130-pc.grupo-iai.com.mx', 'www.iaipc130-pc.grupo-iai.com.mx', '127.0.0.1', 'localhost','intranet.grupo-iai.com.mx']

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
       'archivos': {
        'ENGINE': 'mssql',
        'NAME': 'ArchivosBD',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
    'idiaiv1': {
        'ENGINE': 'mssql',
        'NAME': 'bdidiai',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "components",
]

# variable de Active Directory NO BORRAR!!!!!!!!!

#python manage.py runsslserver  333 --settings=config.settings.development
AD_SERVER =os.environ.get('AD_SERVER_P')  # Cambia esto según el protocolo tu servidor (ldap o ldaps)
AD_PORT =os.environ.get('AD_PORT_P')  # El puerto por defecto es 389 # El puerto por defecto es 389 normalmente 389 para conexiones no seguras o 636 para conexiones seguras con SSL
AD_USER =os.environ.get('AD_USER_P')# # Cambia esto según tus credenciales -----dsquery user -name desarrollo --------dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD =os.environ.get('AD_PASSWORD_P')