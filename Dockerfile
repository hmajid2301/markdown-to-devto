FROM python:alpine3.8 as BUILDER

ARG PIP_PYYAML_VERSION=5.4.1
ARG PIP_REGEX_VERSION=2021.3.17

RUN apk --no-cache add gcc musl-dev yaml-dev yaml 
RUN pip wheel --wheel-dir=/tmp/wheels PyYAML==${PIP_PYYAML_VERSION}
RUN pip wheel --wheel-dir=/tmp/wheels regex==${PIP_REGEX_VERSION}

FROM python:alpine3.8
LABEL MAINTAINER="Haseeb Majid hello@haseebmajid.dev"
LABEL VERSION="0.3.0"

COPY dist ./dist/
COPY --from=BUILDER /tmp/wheels /tmp/wheels
RUN pip install --no-index --find-links=/tmp/wheels/ PyYAML && \
    pip install --no-index --find-links=/tmp/wheels/ regex && \
    pip install dist/*
