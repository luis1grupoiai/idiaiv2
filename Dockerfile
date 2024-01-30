# Usa la imagen oficial de Python 3.11.6-bookworm como base
FROM python:3.11.6-bookworm

# Configura la variable de entorno para que Python no almacene en búfer la salida
ENV PYTHONUNBUFFERED=1

# Instalar libGL 
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Exponer el dispositivo GL
ENV DISPLAY=:0
ENV LIBGL_ALWAYS_INDIRECT=0
ENV GPU_DEVICE /dev/dri

# Descarga e instala Microsoft ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get install -y nano

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /django-project 

# Copia el archivo de requisitos al directorio de trabajo
COPY ./requirements.txt .

# Instala las dependencias de Python desde el archivo de requisitos
RUN python -m pip install -r requirements.txt

# Copia todos los archivos del directorio local al directorio de trabajo en el contenedor
COPY . .

# Copia las migraciones personalizadas
COPY ./venv/Lib/site-packages/django/contrib/auth/migrations/0013_permission_created_at_permission_descripcion_and_more.py /usr/local/lib/python3.11/site-packages/django/contrib/auth/migrations/0013_permission_created_at_permission_descripcion_and_more.py
COPY ./venv/Lib/site-packages/django/contrib/auth/models.py /usr/local/lib/python3.11/site-packages/django/contrib/auth/models.py

# Copia la configuración de Gunicorn
COPY gunicorn_config.py /django-project/gunicorn_config.py

# Define el comando predeterminado al iniciar el contenedor
CMD ["sh", "entrypoint.sh"]

