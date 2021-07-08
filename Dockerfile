FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /app

EXPOSE 80

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD python3 networkNode.py 80 $node