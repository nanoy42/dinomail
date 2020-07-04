FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install psycopg2
COPY ./src/ /code/
COPY ./src/dinomail/local_settings.docker.py /code/dinomail/local_settings.py
