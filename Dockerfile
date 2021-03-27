FROM python:alpine3.7
LABEL MAINTAINER="Haseeb Majid me@haseebmajid.dev"
LABEL VERSION="0.3.0"

COPY dist ./dist/
RUN pip install dist/*
