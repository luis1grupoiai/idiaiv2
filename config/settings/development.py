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
        'NAME': os.environ.get('DB_NAME_DEFAULT'),
        'USER': os.environ.get('DB_USER_DEFAULT'),
        'PASSWORD': os.environ.get('DB_PASSWORD_DEFAULT'),
        'HOST': os.environ.get('DB_HOST_DEFAULT'),
        'PORT': os.environ.get('DB_PORT_DEFAULT'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
    # 'db2': {
    #     'ENGINE': 'mssql',
    #     'NAME': os.environ.get('DB_NAME_DB2'),
    #     'USER': os.environ.get('DB_USER_DB2'),
    #     'PASSWORD': os.environ.get('DB_PASSWORD_DB2'),
    #     'HOST': os.environ.get('DB_HOST_DB2'),
    #     'PORT': os.environ.get('DB_PORT_DB2'),
    #     'OPTIONS': {
    #         'driver': 'ODBC Driver 17 for SQL Server',
    #         'unicode_results': True,
    #     },
    # },
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

# variable de Active Directory NO BORRA!!!!!!!!!
AD_SERVER = os.environ.get('ActiveDirectory_SERVER')  # Cambia esto segÃºn tu servidor
AD_PORT = int(os.environ.get('ActiveDirectory_PORT'))   # El puerto por defecto es 389
AD_USER = os.environ.get('ActiveDirectory_USER')   # Cambia esto segÃºn tus credenciales
#dsquery user -name desarrollo
#dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD = os.environ.get('ActiveDirectory_PASSWORD') 
