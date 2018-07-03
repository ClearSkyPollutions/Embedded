ifconfig wlan0 down

cp /etc/dhcpcd.conf /etc/dhcpcd.conf.ori
cp dhcpcd.conf /etc/dhcpcd.conf
service dhcpcd stop
systemctl enable dnsmasq
systemctl enable hostapd
systemctl daemon-reload

ifconfig wlan0 up
sleep 3
service hostapd start
service dnsmasq start
service dhcpcd start
