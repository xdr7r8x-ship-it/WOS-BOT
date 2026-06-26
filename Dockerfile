FROM python:3.12-slim-bookworm

LABEL maintainer="WOS-BOT"
LABEL org.opencontainers.image.source=https://github.com/xdr7r8x-ship-it/WOS-BOT

ENV PYTHONUNBUFFERED=1
ENV WEB_DASHBOARD_HOST=0.0.0.0
ENV WEB_DASHBOARD_PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN if [ -d "src/web/frontend" ]; then \
    apt-get update && apt-get install --no-install-recommends -y nodejs npm && \
    cd src/web/frontend && npm install && npm run build && \
    apt-get -y autoremove && apt-get -y autoclean; \
    fi

EXPOSE 8080

CMD ["python", "main.py"]
