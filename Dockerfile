FROM python:3.9
# FROM ubuntu:20.04

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get clean
RUN apt-get update && apt-get install -y curl git wget ffmpeg libsm6 libxext6
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

RUN chmod ugoa+rwx /app
RUN chmod ugoa+rwx -R /usr/local/bin/

# Install npm
ENV NODE_VERSION=16.13.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

RUN pip install --upgrade pip

ENV ipfs_root="/app/ipfs"
ENV worker_root="/app"
RUN mkdir -p $ipfs_root
RUN mkdir -p $ipfs_root/input
RUN mkdir -p $ipfs_root/output

RUN git clone https://github.com/pollinations/pollinations-ipfs.git
RUN cd /app/pollinations-ipfs && npm run install_backend

COPY . /app
 
RUN pip install .

ENV AWS_REGION="us-east-1"

CMD ["python", "rest_pollen/main.py", "--host", "0.0.0.0", "--port", "5000"]