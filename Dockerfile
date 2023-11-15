FROM python:3.12.0-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt ./

RUN python -m pip install -r requirements.txt

COPY ./ ./

CMD ["sh", "entrypoint.sh"]