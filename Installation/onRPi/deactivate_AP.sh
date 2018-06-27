ifconfig wlan0 down

mv /etc/dhcpcd.conf.ori /etc/dhcpcd.conf

service dhcpcd stop
service dnsmasq stop
service hostapd stop
systemctl disable dnsmasq
systemctl disable hostapd
systemctl daemon-reload

ifconfig wlan0 up
service dhcpcd start
