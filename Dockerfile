FROM python:3.11-slim

# Install Node.js and Chromium
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    chromium \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/requirements.txt ./src/
RUN pip install -r src/requirements.txt

COPY src/js/package*.json ./src/js/
RUN cd src/js && npm install

COPY src ./src/

ENV PYTHONUNBUFFERED=1

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]