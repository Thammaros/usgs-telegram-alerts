FROM python:3.12-alpine3.21

ENV TZ=Asia/Bangkok

RUN apk update && apk add --no-cache \
    build-base \
    geos-dev \
    proj-dev \
    proj-data \
    proj-util \
    py3-numpy \
    py3-pillow \
    py3-matplotlib \
    py3-setuptools \
    py3-wheel \
    py3-pip \
    python3-dev \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    libpng-dev \
    gfortran \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
