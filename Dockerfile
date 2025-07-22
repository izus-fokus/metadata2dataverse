FROM python:3.13.5-alpine3.22

LABEL maintainer="florian.fritze@ub.uni-stuttgart.de"

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps git && pip install --no-cache-dir -r requirements.txt && apk del --no-network .build-deps

WORKDIR /app

EXPOSE 5000

COPY v1 /app
COPY cred /app/cred/

ENTRYPOINT [ "python" ]
CMD [ "__init__.py" ] 
