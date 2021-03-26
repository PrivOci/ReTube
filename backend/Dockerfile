# # https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
# FROM tiangolo/uvicorn-gunicorn:python3.8

# COPY ./ /app
# WORKDIR /app/
# ENV PYTHONPATH=/app

# RUN pip install -r requirements.txt



# FOR Raspi
FROM python:3.7
COPY ./ /app
WORKDIR /app/
ENV PYTHONPATH=/app

RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]