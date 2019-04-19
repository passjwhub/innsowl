FROM python:3.6-alpine

ENV FLASK_APP InnsOwl.py
ENV FLASK_CONFIG production

RUN adduser -D  InnsOwl
USER InnsOwl

WORKDIR /home/InnsOwl

COPY requirements requirements
RUN python3 -m venv venv
RUN venv/bin/pip3 install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY InnsOwl.py config.py boot.sh ./

# run-time configuration
EXPOSE 8089
ENTRYPOINT ["./boot.sh"]
