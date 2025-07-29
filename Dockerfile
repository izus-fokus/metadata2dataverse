FROM python:3.13.5-alpine3.22

LABEL maintainer="florian.fritze@ub.uni-stuttgart.de"

WORKDIR /app
COPY . /app

RUN python3 -m venv /app/venv
ENV PATH=/app/venv/bin:$PATH
RUN source /app/venv/bin/activate
RUN apk add --no-cache --virtual .build-deps git
RUN pip install --upgrade pip
RUN pip install -r requirements.txt && apk del --no-network .build-deps


ENV PORT=5055

ENV ADDRESS=127.0.0.1

EXPOSE $PORT

ENTRYPOINT exec gunicorn -b $ADDRESS:$PORT '__init__:app' --chdir v1
