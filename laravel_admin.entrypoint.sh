#!/bin/bash
set -e

echo "[Fixu] Starting Laravel entrypoint..."

# Inject DB credentials from environment variables into .env
# Only update if the env var is actually set and non-empty
if [ -n "$DB_HOST" ]; then
    sed -i "s/^DB_HOST=.*/DB_HOST=${DB_HOST}/" /var/www/html/.env
fi
if [ -n "$DB_PORT" ]; then
    sed -i "s/^DB_PORT=.*/DB_PORT=${DB_PORT}/" /var/www/html/.env
fi
if [ -n "$DB_DATABASE" ]; then
    sed -i "s/^DB_DATABASE=.*/DB_DATABASE=${DB_DATABASE}/" /var/www/html/.env
fi
if [ -n "$DB_USERNAME" ]; then
    sed -i "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USERNAME}/" /var/www/html/.env
fi
if [ -n "$DB_PASSWORD" ]; then
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" /var/www/html/.env
fi

# IMPORTANT: Unset APP_KEY from environment so Laravel uses the one from .env
# (Render may set APP_KEY as empty which takes precedence over .env)
unset APP_KEY

# Clear config cache to pick up new values
php /var/www/html/artisan config:clear || true

echo "[Fixu] Starting Apache..."
exec apache2-foreground
