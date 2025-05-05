
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ENV APP_ENV=dev

# WORKDIR /app

# Install all required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
COPY entrypoint.sh .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /local_s3_storage/okyke-files/products

COPY . .

EXPOSE 8080

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
