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
# Install Python dependencies
# -----------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------
# Install Playwright browsers (Chromium only)
# -----------------------------------------------------
RUN pip install playwright
RUN playwright install chromium

# -----------------------------------------------------
# Copy application code
# -----------------------------------------------------
COPY . .

# -----------------------------------------------------
# Expose internal port
# -----------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------
# START COMMAND (Chromium needs --no-sandbox)
# -----------------------------------------------------
CMD ["sh", "-c", "export PLAYWRIGHT_BROWSERS_PATH=0 && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
