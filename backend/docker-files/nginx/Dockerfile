FROM python:3.10.4

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update
RUN apt install -y cron

RUN apt install -y joe 
RUN apt install -y vim
RUN apt install -y redis
RUN apt install -y nginx
RUN apt install -y postgresql-client
RUN apt install -y supervisor

#COPY src/base3src         /app/base3src
#COPY src/tshared_src      /app/tshared_src
#COPY src/requirements.txt /app/
#COPY src/requirements.sh  /app/
#COPY src/svc_base         /app/svc_base
COPY ./docker-files/nginx/supervisord.conf     /etc/supervisord.conf
COPY ./src                                     /app

RUN pip install --upgrade pip
RUN pip install wheel
RUN /app/requirements.sh

ENV PYTHONPATH /app

RUN python3 /app/service.py

CMD /usr/bin/supervisord -c /etc/supervisord.conf
