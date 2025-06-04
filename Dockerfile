FROM python:3

RUN mkdir /app
WORKDIR /app
COPY . /app

EXPOSE 80
EXPOSE 9001
EXPOSE 9002

CMD ["python3", "app.py"]