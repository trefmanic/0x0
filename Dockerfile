FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libmagic1 \
    libmpv1 \
    nginx \
    kitty \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /run/nginx /var/cache/nginx
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8420

ENTRYPOINT ["/entrypoint.sh"]
