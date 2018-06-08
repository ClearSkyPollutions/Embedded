apt-get install php apache2 mysql-server php-mysql
python CreateBaseUsers.py
python CreateBaseConPM.py

mv html/* /var/www/html/
mv apache2.conf /etc/apache2/apache2.conf
a2enmod rewrite

echo "Please reboot"
