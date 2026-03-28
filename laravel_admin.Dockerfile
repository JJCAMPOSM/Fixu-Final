FROM php:8.4-apache

# Enable Apache modules
RUN a2enmod rewrite headers

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libzip-dev \
    libpng-dev \
    libjpeg-dev \
    unzip \
    && docker-php-ext-configure gd --with-jpeg \
    && docker-php-ext-install pdo pdo_pgsql zip gd bcmath

# Set DocumentRoot to public/ directory
ENV APACHE_DOCUMENT_ROOT /var/www/html/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf
RUN sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

WORKDIR /var/www/html

# Copy the Laravel project files
COPY laravel_admin/ .

# Create .env file from example and set proper environment variables
RUN cp .env.example .env && \
    sed -i 's/DB_CONNECTION=sqlite/DB_CONNECTION=pgsql/' .env && \
    sed -i 's/# DB_HOST=127.0.0.1/DB_HOST=db/' .env && \
    sed -i 's/# DB_PORT=3306/DB_PORT=5432/' .env && \
    sed -i 's/# DB_DATABASE=laravel/DB_DATABASE=fixu/' .env && \
    sed -i 's/# DB_USERNAME=root/DB_USERNAME=fixu_user/' .env && \
    sed -i 's/# DB_PASSWORD=/DB_PASSWORD=fixu_password/' .env && \
    sed -i 's/APP_KEY=/APP_KEY=base64:1vZsQu7C3mE5o9kL2wXr4YhJ8UiA0sDfT6gHjKlMnBo=/' .env && \
    sed -i 's|APP_URL=http://localhost|APP_URL=http://localhost:8000|' .env && \
    sed -i 's/SESSION_DRIVER=database/SESSION_DRIVER=file/' .env && \
    sed -i 's/CACHE_STORE=database/CACHE_STORE=file/' .env && \
    sed -i 's/QUEUE_CONNECTION=database/QUEUE_CONNECTION=sync/' .env

# Install Composer and dependencies directly in the image
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN composer update --no-interaction --no-dev --optimize-autoloader

# Fix permissions for storage and cache directories
RUN chown -R www-data:www-data storage bootstrap/cache vendor || true

# Create storage directories if they don't exist and fix permissions
RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs \
    && chown -R www-data:www-data storage bootstrap/cache \
    && chmod -R 775 storage bootstrap/cache
