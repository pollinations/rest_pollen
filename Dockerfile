FROM python:3.9
# FROM ubuntu:20.04

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get clean
RUN apt-get update && apt-get install -y curl git wget ffmpeg libsm6 libxext6
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

RUN pip install --upgrade pip

COPY . /app
 
RUN pip install .

ENV AWS_REGION="us-east-1"

CMD ["python", "rest_pollen/main.py", "--host", "0.0.0.0", "--port", "5000"]