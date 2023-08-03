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
    echo "server ${NTP_SERVER_HOSTNAME} prefer" >> /etc/ntp.conf
    echo "restrict ${NTP_SERVER_HOSTNAME} " >> /etc/ntp.conf
fi
service ntp restart
#/etc/init.d/ntp restart
#/usr/sbin/ntpd -d
service cron restart
crontab /opt/cdm/sync.cnf
