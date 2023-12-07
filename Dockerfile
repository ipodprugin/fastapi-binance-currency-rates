FROM python:3.10-slim-bullseye

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

# RUN apt-get update \
#     && apt-get -y install build-essential \
#     && apt-get -y install libpq-dev gcc \
#     && apt-get -y install netcat

RUN pip install --no-cache-dir --upgrade -r requirements.txt
