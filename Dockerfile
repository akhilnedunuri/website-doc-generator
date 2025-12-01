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
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    fonts-liberation \
    libgbm1 \
    libpango1.0-0 \
    libcairo2 \
    libxshmfence1 \
    libxshmfence1 \
    libxkbcommon0 \
    libdrm2 \
    libxext6 \
    libxfixes3 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Copy Python dependencies
# -------------------------------
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Playwright & Chromium installation
RUN pip install playwright
RUN playwright install --with-deps chromium

# -------------------------------
# Copy application code
# -------------------------------
COPY . .

# -------------------------------
# Expose port (Coolify uses PORT env automatically)
# -------------------------------
EXPOSE 8000

# -------------------------------
# Start FastAPI app
# -------------------------------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
