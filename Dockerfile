# -----------------------------------------------------
# Base image
# -----------------------------------------------------
FROM python:3.11-slim

# -----------------------------------------------------
# Install system dependencies
# -----------------------------------------------------
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libdrm2 \
    libxext6 \
    libxfixes3 \
    libcairo2 \
    libpango-1.0-0 \
    libxshmfence1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------
# Working directory
# -----------------------------------------------------
WORKDIR /app

# -----------------------------------------------------
# Copy dependencies
# -----------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------
# Copy app code
# -----------------------------------------------------
COPY . .

# -----------------------------------------------------
# Add runtime install script
# -----------------------------------------------------
RUN echo '#!/bin/sh\n\
pip install playwright && playwright install chromium --with-deps\n\
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}\n' \
> /app/start.sh

RUN chmod +x /app/start.sh

# -----------------------------------------------------
# Expose port
# -----------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------
# RUN APPLICATION
# -----------------------------------------------------
CMD ["/app/start.sh"]
