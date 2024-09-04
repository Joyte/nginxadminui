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
    php${PHP_VERSION}-fpm php${PHP_VERSION}-cli php${PHP_VERSION}-curl \
    php${PHP_VERSION}-gd php${PHP_VERSION}-mbstring php${PHP_VERSION}-xml \
    php${PHP_VERSION}-zip php${PHP_VERSION}-mysql php${PHP_VERSION}-sqlite3 \
    php${PHP_VERSION}-pgsql php${PHP_VERSION}-bcmath php${PHP_VERSION}-intl \
    php${PHP_VERSION}-imagick php${PHP_VERSION}-dev php${PHP_VERSION}-soap \
    php${PHP_VERSION}-xdebug php${PHP_VERSION}-opcache php${PHP_VERSION}-ldap \
    php${PHP_VERSION}-redis php${PHP_VERSION}-memcached php${PHP_VERSION}-apcu \
    php${PHP_VERSION}-msgpack php${PHP_VERSION}-igbinary php${PHP_VERSION}-amqp \
    php${PHP_VERSION}-mongodb \
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
CMD service php${PHP_VERSION}-fpm start && \
    nginx -g "daemon off;" && \
    .venv/bin/python -m uvicorn 'main:app' \
    --host=0.0.0.0 --port=81 \
    --ssl-keyfile /app/privkey.pem --ssl-certfile /app/fullchain.pem \
    --app-dir /app
