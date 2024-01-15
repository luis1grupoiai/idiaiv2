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

<<<<<<< HEAD
# variable de Active Directory NO BORRAR!!!!!!!!!
AD_SERVER = os.environ.get('ActiveDirectory_SERVER')  # Cambia esto segÃºn tu servidor
AD_PORT = 389#int(os.environ.get('ActiveDirectory_PORT'))   # El puerto por defecto es 389
AD_USER = os.environ.get('ActiveDirectory_USER')   # Cambia esto segÃºn tus credenciales
#dsquery user -name desarrollo
#dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD = os.environ.get('ActiveDirectory_PASSWORD') 


=======
>>>>>>> 7ed056a12a6bc90ff88907379ec37b74ed3bf742
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sistemas.iai@grupo-iai.com.mx'
EMAIL_HOST_PASSWORD = 'hLW*t37l_'
