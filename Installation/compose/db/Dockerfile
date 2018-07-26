FROM mariadb:latest
COPY 50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf

COPY mysqldump.sql /mysqldump.sql
RUN chmod 755 /mysqldump.sql
COPY init_mysql.sh /docker-entrypoint-initdb.d/init_mysql.sh
RUN chmod 755 /docker-entrypoint-initdb.d/init_mysql.sh

# To create a mariadb user with permisison only on docker network
RUN sed -i "s/skip-name-resolve/# skip-name-resolve/" /etc/mysql/conf.d/docker.cnf
RUN sed -i "s/skip_log_error/# skip_log_error/" /etc/mysql/conf.d/mysqld_safe_syslog.cnf

EXPOSE 3306
