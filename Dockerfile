FROM ubuntu:24.10

# Container essentials
RUN apt update -y && apt install -y python3 python3-venv nginx 7zip

# Install PHP composer
COPY --from=composer/composer:latest-bin /composer /usr/bin/composer

WORKDIR /app

# Create a self-signed certificate for the admin UI
RUN openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout privkey.pem -out fullchain.pem -subj "/CN=*/O=Nginx Admin UI/OU=Nginx Admin UI" -addext "subjectAltName=DNS:*"

# Copy the source code into the container.
COPY . .

# Create a virtual environment and install dependencies
RUN python3 -m venv /app/.venv

RUN .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

# Clear sites-available and sites-enabled
RUN rm /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Expose the ports that the application listens on.
EXPOSE 81
EXPOSE 80
EXPOSE 443

# Run the application.
CMD nginx; .venv/bin/python -m uvicorn 'main:app' --host=0.0.0.0 --port=81 --app-dir /app --ssl-keyfile /app/privkey.pem --ssl-certfile /app/fullchain.pem
