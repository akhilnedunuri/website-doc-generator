# -------------------------------
# Base image
# -------------------------------
FROM python:3.11-slim

# -------------------------------
# Install system dependencies for Playwright + Chromium
# -------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libx11-6 \
    libx11-data \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    fonts-liberation \
    libgbm1 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libxshmfence1 \
    libxkbcommon0 \
    libdrm2 \
    libxext6 \
    libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Install Python deps + Playwright
# -------------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir playwright
RUN playwright install chromium --with-deps

# -------------------------------
# Copy project
# -------------------------------
COPY . .

# -------------------------------
# Expose port (Coolify uses $PORT automatically)
# -------------------------------
EXPOSE 3000

# -------------------------------
# Start FastAPI app
# -------------------------------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
