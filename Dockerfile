# Usa la imagen oficial de Python 3.11.6-bookworm como base
FROM python:3.11.6-bookworm

# Configura la variable de entorno para que Python no almacene en búfer la salida
ENV PYTHONUNBUFFERED=1

# Descarga e instala Microsoft ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos al directorio de trabajo
COPY ./requirements.txt ./

# Instala las dependencias de Python desde el archivo de requisitos
RUN python -m pip install -r requirements.txt

# Copia todos los archivos del directorio local al directorio de trabajo en el contenedor
COPY ./ ./

# Define el comando predeterminado al iniciar el contenedor
CMD ["sh", "entrypoint.sh"]
