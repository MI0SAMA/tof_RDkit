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

# Install Python deps with Tsinghua mirror for faster downloads in China
# Pin numpy<2 because rdkit-pypi is compiled against NumPy 1.x
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir "numpy<2" pandas pyyaml networkx tqdm rdkit-pypi \
    && pip install --no-cache-dir fastapi uvicorn sqlalchemy

# Copy backend code
COPY web/backend/ /app/backend/

# Copy the main Python package
COPY tofsims_formula_network/ /app/tofsims_formula_network/

# Copy config and data
COPY config/ /app/config/
COPY data/compounds.csv /app/data/compounds.csv

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Configure nginx and supervisor
COPY web/nginx.conf /etc/nginx/sites-available/default
COPY web/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directories
RUN mkdir -p /app/data /app/outputs /app/web_data

WORKDIR /app
ENV PYTHONPATH=/app

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
