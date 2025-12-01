# -------------------------------
# Base image
# -------------------------------
FROM python:3.11-slim

# -------------------------------
# Install system dependencies for Playwright
# -------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    fonts-liberation \
    libgbm1 \
    libpango1.0-0 \
    libxshmfence1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Copy requirements and install Python packages
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Install Playwright browsers
# -------------------------------
RUN pip install --no-cache-dir playwright
RUN playwright install

# -------------------------------
# Copy the rest of the project
# -------------------------------
COPY . .
    
# -------------------------------
# Expose port
# -------------------------------
EXPOSE 10000

# -------------------------------
# Run the app using Render's PORT environment variable
# -------------------------------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
