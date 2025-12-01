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
RUN pip install playwright
RUN playwright install chromium --with-deps

# -----------------------------------------------------
# Copy application code
# -----------------------------------------------------
COPY . .

# -----------------------------------------------------
# Make run.sh executable
# -----------------------------------------------------
RUN chmod +x backend/run.sh

# -----------------------------------------------------
# Expose port
# -----------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------
# Start server
# -----------------------------------------------------
CMD ["sh", "backend/run.sh"]
