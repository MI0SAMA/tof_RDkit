# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY web/frontend/package.json ./
RUN npm install --legacy-peer-deps
COPY web/frontend/ ./
RUN npm run build

# Stage 2: Python backend + Nginx
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor && rm -rf /var/lib/apt/lists/*

COPY web/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY web/backend/ /app/backend/
COPY config/ /app/config/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

COPY web/nginx.conf /etc/nginx/sites-available/default
COPY web/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /app/data /app/outputs /app/web_data
WORKDIR /app

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
