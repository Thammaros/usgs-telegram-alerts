FROM python:3.13.7-alpine3.21

ENV TZ=Asia/Bangkok \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install build tools 
RUN apk add --no-cache build-base 

WORKDIR /app
COPY . .

# use uv for faster installs
RUN pip install -U uv --no-cache-dir --root-user-action=ignore \
 && uv pip install --no-cache-dir -r requirements.txt --system

CMD ["python", "main.py"]