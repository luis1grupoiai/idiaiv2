import os
from config.logging import *
from config.settings.base import *
from dotenv import load_dotenv


load_dotenv(Path.joinpath(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['grupo-iai.com.mx', 'www.grupo-iai.com.mx', 'iaipc130-pc.grupo-iai.com.mx', 'www.iaipc130-pc.grupo-iai.com.mx', '127.0.0.1', 'iaipc125-pc.grupo-iai.com.mx','localhost','intranet.grupo-iai.com.mx']

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

AD_SERVER = os.environ.get('AD_SERVER_P')   # Cambia esto según tu servidor
AD_PORT =os.environ.get('AD_PORT_P')  # El puerto por defecto es 389 # El puerto por defecto es 389 normalmente 389 para conexiones no seguras o 636 para conexiones seguras con SSL
AD_USER = os.environ.get('AD_USER_P')  # Cambia esto según tus credenciales -----dsquery user -name desarrollo --------dsget user "CN=desarrollo,CN=Users,DC=iai,DC=com,DC=mx"
AD_PASSWORD = os.environ.get('AD_PASSWORD_P')

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:335', 
    'https://localhost:8080', 
    'https://127.0.0.1:8080',
    'https://grupo-iai.com.mx:8080', 
    'https://www.grupo-iai.com.mx:8080', 
    'https://iaipc130-pc.grupo-iai.com.mx:8080', 
    'https://iaipc125-pc.grupo-iai.com.mx:8080', 
    'https://www.iaipc130-pc.grupo-iai.com.mx:443',
    'https://intranet.grupo-iai.com.mx'  # Asegúrate de añadir el esquema correcto según sea http o https
]
