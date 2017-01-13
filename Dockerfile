FROM redis:3.2.6
FROM postgres:9.6
FROM python:3.5
MAINTAINER FoxMaSk <foxmask@trigger-happy.eu>
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
COPY requirements-docker.txt /app/
RUN pip install -r requirements-docker.txt
COPY . /app/


#EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=django_th.settings_docker"]