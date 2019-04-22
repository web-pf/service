FROM ubuntu:18.04
LABEL maintainer = "zhixiang@live.cn"
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# change apt source list to Aliyun, update and upgrade.
COPY ./env/sys/source.list /etc/apt/sources.list
RUN apt update -y
RUN apt upgrade -y

# install softwares and python dependencies.
RUN apt install -y python3 python3-pip nginx vim
COPY ./env/py/requirements.txt /tmp
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /tmp/requirements.txt

# copy ssl certificate and key
RUN mkdir /etc/nginx/ssl
COPY ./env/nginx/ssl /etc/nginx/ssl/

# create nginx log directory and apply nginx configuration
COPY ./env/nginx/site.conf /etc/nginx/sites-available/
RUN ln -s ../sites-available/site.conf /etc/nginx/sites-enabled/site.conf
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
RUN mkdir /logs

# copy service code
RUN mkdir /web-perf-service
WORKDIR /web-perf-service
COPY ./env/py/gunicorn.conf.py ./
COPY ./src /web-perf-service/

# Done
EXPOSE 80 443
CMD gunicorn app:app -c gunicorn.conf.py && service nginx start
