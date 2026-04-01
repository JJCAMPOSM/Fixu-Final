#!/bin/bash
set -e

echo "[Fixu] Starting Laravel entrypoint..."

# Inject DB credentials from environment variables into .env
if [ -n "$DB_HOST" ]; then
    sed -i "s/^# DB_HOST=.*/DB_HOST=${DB_HOST}/" /var/www/html/.env
    sed -i "s/^DB_HOST=.*/DB_HOST=${DB_HOST}/" /var/www/html/.env
fi
if [ -n "$DB_PORT" ]; then
    sed -i "s/^# DB_PORT=.*/DB_PORT=${DB_PORT}/" /var/www/html/.env
    sed -i "s/^DB_PORT=.*/DB_PORT=${DB_PORT}/" /var/www/html/.env
fi
if [ -n "$DB_DATABASE" ]; then
    sed -i "s/^# DB_DATABASE=.*/DB_DATABASE=${DB_DATABASE}/" /var/www/html/.env
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_DATABASE}/" /var/www/html/.env
fi
if [ -n "$DB_USERNAME" ]; then
    sed -i "s/^# DB_USERNAME=.*/DB_USERNAME=${DB_USERNAME}/" /var/www/html/.env
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USERNAME}/" /var/www/html/.env
fi
if [ -n "$DB_PASSWORD" ]; then
    sed -i "s/^# DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" /var/www/html/.env
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" /var/www/html/.env
fi

# Generate a valid APP_KEY if not already set
CURRENT_KEY=$(grep "^APP_KEY=" /var/www/html/.env | cut -d'=' -f2)
if [ -z "$CURRENT_KEY" ] || [ "$CURRENT_KEY" = "" ]; then
    echo "[Fixu] Generating APP_KEY..."
    php /var/www/html/artisan key:generate --force
else
    echo "[Fixu] APP_KEY already set."
fi

# Clear config cache to pick up new values
php /var/www/html/artisan config:clear || true

echo "[Fixu] Starting Apache..."
exec apache2-foreground
