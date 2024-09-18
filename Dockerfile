# Use the official Ubuntu 24.10 base image
FROM ubuntu:24.10

# Set PHP version as an argument for flexibility
ARG PHP_VERSION=8.3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PHP_VERSION=${PHP_VERSION}

# Update package list and install dependencies
RUN apt update && apt install -y \
    python3 python3-venv nginx 7zip \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Install PHP composer
COPY --from=composer/composer:latest-bin /composer /usr/bin/composer

# Set working directory
WORKDIR /app

# Create a self-signed certificate for the admin UI
RUN openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout /app/privkey.pem -out /app/fullchain.pem \
    -subj "/CN=*/O=Nginx Admin UI/OU=Nginx Admin UI" \
    -addext "subjectAltName=DNS:*"

# Copy the source code into the container
COPY . .

# Create a virtual environment and install Python dependencies
RUN python3 -m venv /app/.venv \
    && .venv/bin/pip install --upgrade pip \
    && .venv/bin/pip install -r requirements.txt

# Clear default Nginx site configurations
RUN rm /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Create storage for logs, certificates, etc.
RUN mkdir -p /etc/nginxadminui/logs /etc/nginxadminui/certificates

# Expose necessary ports
EXPOSE 80 81 443

# Start services: PHP-FPM, Nginx, and the Python application
CMD sh /app/entrypoint.sh