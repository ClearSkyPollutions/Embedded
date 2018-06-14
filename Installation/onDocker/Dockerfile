FROM debian:latest

# To build on x86
# RUN [ "cross-build-start" ]

# Enable systemd
ENV INITSYSTEM on

# Install necessary packages in non-interactive mode 
# and don't install the recommanded packages
RUN apt-get update && apt-get install -y --no-install-recommends \
apache2 \
php \
mysql-server \
php-mysql

# Copy needed files from github or from disk ?
# Data from disk 
COPY html/.htaccess /var/www/html
COPY api.php /var/www/html
COPY aqi.php /var/www/html
COPY config.php /var/www/html
COPY apache2.conf /etc/apache2/apache2.conf
COPY 50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf

# Base apache app location
RUN chmod -R 755 /var/www/html

COPY config.json /var/www/html
RUN chmod 766 /var/www/html/config.json

COPY init_mysql.sh /init_mysql.sh
RUN chmod 755 /init_mysql.sh

COPY mysqldump.sql /mysqldump.sql
RUN chmod 755 /mysqldump.sql

COPY run.sh /run.sh
RUN chmod 755 /run.sh

RUN a2enmod rewrite

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 3306

# Define environment variable
ENV NAME dev

CMD ["/run.sh"]
