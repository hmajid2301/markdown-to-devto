FROM python:alpine3.7
LABEL MAINTAINER="Haseeb Majid me@haseebmajid.dev"

COPY dist ./dist/
RUN pip install dist/*
