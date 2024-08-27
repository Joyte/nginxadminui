# nginxadminui

Nginx Admin UI is a simple Web interface for managing Nginx servers.

In it's current state, it only provides a simple way to edit the configuration files.

In the future, it will provide more interesting features like custom access lists, using Certbot to generate SSL certificates, viewing the Nginx logs, etc.

## WARNING!
This is a work in progress, and shouldn't be used in production environments.
Do not expose port 81 to the internet, as the admin UI will be accessible to anyone.

## Installation
* Copy `docker-compose.yml` to a dedicated folder in your server
* Run `docker compose up -d`
* Done! Navigate to `https://localhost:81` to access the web UI

Note: It is ***HTTPS***, not http! If you connect over http, you will get an error akin to "The connection was reset" on firefox and "This page isn’t working" on chrome-based browsers.


## Documentation

Full documentation is available at [https://nginxadminui.com](https://nginxadminui.com)