FROM python:alpine3.7
LABEL MAINTAINER="Haseeb Majid me@haseebmajid.dev"
LABEL VERSION="0.2.1.beta.1"

COPY dist ./dist/
RUN pip install dist/*
