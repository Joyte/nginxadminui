# nginxadminui

Nginx Admin UI is a simple Web interface for managing Nginx servers.

In it's current state, it only provides a simple way to edit the configuration files.

In the future, it will provide more interesting features like custom access lists, using Certbot to generate SSL certificates, viewing the Nginx logs, etc.

It will also be installable using a docker compose, so you can easily deploy it in your server.

## Installation
* Clone the repository
* Install the dependencies
```bash
python -m pip install -r requirements.txt
```
* Run the server
```bash
uvicorn main:app --app-dir %YOUR_CLONED_REPOSITORY_PATH%
```

## Configuration
Copy `.env-example` to `.env` and edit the values to match your configuration.

## Documentation

Documentation is available at [https://nginxadminui.com](https://nginxadminui.com)