FROM python:3.13.11-trixie AS builder

LABEL maintainer="florian.fritze@ub.uni-stuttgart.de"

SHELL ["/bin/bash", "-c"]

WORKDIR /app
COPY . /app

RUN python3 -m venv /app/venv
ENV PATH=/app/venv/bin:$PATH
RUN source /app/venv/bin/activate
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM python:3.13.11-slim-trixie
SHELL ["/bin/bash", "-c"]
WORKDIR /app
COPY --from=builder /app /app
ENV PATH=/app/venv/bin:/usr/local/bin:$PATH
RUN source /app/venv/bin/activate
ENV PORT=5055

ENV ADDRESS=127.0.0.1

EXPOSE $PORT

ENV URL_PATH="/"

ENTRYPOINT gunicorn -b $ADDRESS:$PORT '__init__:app' --chdir v1 --env "SCRIPT_NAME=$URL_PATH"
