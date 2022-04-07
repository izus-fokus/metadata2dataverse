FROM python:3.9-alpine

LABEL maintainer="anett.seeland@tik.uni-stuttgart.de"

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps git && pip install --no-cache-dir -r requirements.txt && apk del --no-network .build-deps

WORKDIR /app

EXPOSE 5000

COPY v1 .

ENTRYPOINT [ "python" ]
CMD [ "__init__.py" ] 
