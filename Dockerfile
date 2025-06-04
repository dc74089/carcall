FROM python:3

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 && apt-get install ffmpeg libav-tools

RUN pip install -r /app/requirements.txt

EXPOSE 80
EXPOSE 9001
EXPOSE 9002

CMD ["python3", "app.py"]