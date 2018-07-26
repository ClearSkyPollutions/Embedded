FROM php:7.0-apache
RUN docker-php-ext-install mysqli pdo pdo_mysql
COPY ./html/ /var/www/html/
COPY apache2.conf /etc/apache2/apache2.conf
RUN a2enmod rewrite
