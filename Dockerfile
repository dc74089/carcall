FROM python:3

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install -r /app/requirements.txt

EXPOSE 80
EXPOSE 9001
EXPOSE 9002

CMD ["python3", "app.py"]