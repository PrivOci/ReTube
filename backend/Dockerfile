# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
FROM tiangolo/uvicorn-gunicorn:python3.8

COPY ./ /app
WORKDIR /app/
ENV PYTHONPATH=/app

RUN pip install -r requirements.txt