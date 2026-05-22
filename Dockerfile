FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/server-entrypoint.sh

EXPOSE 8000

CMD ["sh", "/app/server-entrypoint.sh"]
