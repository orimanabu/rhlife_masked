#!/bin/sh
# use hash XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX for MY_HOSTNAME.usersys.redhat.com 
HOSTNAME=MY_HOSTNAME
HASH=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
curl "http://ddns.corp.redhat.com/redhat-ddns/updater.php?name=$HOSTNAME&domain=usersys.redhat.com&hash=$HASH"
