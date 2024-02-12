import os
from config.logging import *
from config.settings.base import *
from dotenv import load_dotenv


load_dotenv(Path.joinpath(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['grupo-iai.com.mx', 'www.grupo-iai.com.mx', 'iaipc130-pc.grupo-iai.com.mx', 'www.iaipc130-pc.grupo-iai.com.mx', '127.0.0.1', 'localhost']

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
        'OPTIONS':{
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

AD_SERVER = 'ldaps://'  # Cambia esto según tu servidor
AD_PORT = 636  # El puerto por defecto es 389 # El puerto por defecto es 389 normalmente 389 para conexiones no seguras o 636 para conexiones seguras con SSL
AD_USER = 'CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx'  # Cambia esto según tus credenciales -----dsquery user -name desarrollo --------dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD = 'D3sarrollo'

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = ['https://localhost:8080', 'https://127.0.0.1:8080']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sistemas.iai@grupo-iai.com.mx'
EMAIL_HOST_PASSWORD = 'hLW*t37l_'
