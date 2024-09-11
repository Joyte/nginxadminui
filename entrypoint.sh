echo "Starting PHP"
service php$(ls /etc/php)-fpm start
echo "Starting Nginx"
service nginx start
echo "Starting FastAPI"
/app/.venv/bin/python -m uvicorn 'main:app' --host=0.0.0.0 --port=81 --ssl-keyfile /app/privkey.pem --ssl-certfile /app/fullchain.pem --app-dir /app
echo "Done"