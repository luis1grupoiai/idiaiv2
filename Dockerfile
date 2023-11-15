FROM python:3.12.0-bookworm

ENV PYTHONUNBUFFERED=1

# Descargar e instalar Microsoft ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app

COPY ./requirements.txt ./

RUN python -m pip install -r requirements.txt

COPY ./ ./

CMD ["sh", "entrypoint.sh"]