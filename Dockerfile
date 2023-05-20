FROM python:3.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libc-dev \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY script.py /app/

CMD ["python", "script.py"]
