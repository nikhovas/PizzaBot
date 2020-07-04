FROM python:3.7

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt