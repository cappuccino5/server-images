#!/bin/bash

#set -e
if [ "$NODE_TYPE" == "server" ]; then
	if  [ -e /etc/ntp.conf ];then
	   echo "ntp conf already exits"
 else
cat >> /etc/ntp.conf <<EOF
server 0.ubuntu.pool.ntp.org
server 1.ubuntu.pool.ntp.org
server  127.127.1.0     # local clock
fudge   127.127.1.0 stratum 10
EOF
fi
else
cat << EOF > /etc/ntp.conf
server  127.127.1.0     # local clock
fudge   127.127.1.0 stratum 10
server 0.ubuntu.pool.ntp.org
server 1.ubuntu.pool.ntp.org
server cn.pool.ntp.org
server ${NTP_SERVER_HOSTNAME} prefer
restrict ${NTP_SERVER_HOSTNAME}
EOF
fi
service ntp restart
#/etc/init.d/ntp restart
#/usr/sbin/ntpd -d
service cron restart
crontab /opt/cdm/sync.cnf
