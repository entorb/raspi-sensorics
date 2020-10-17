#!/bin/bash

# calls sicher-all.sh to create backups of all data and configs
# uses scp to copy these to my desktop pc

echo ... sicher-all.sh
/home/pi/bin/sicher-all.sh

echo ... rsnapshot for /etc and /home
sudo rsnapshot alpha
cd /sicher-rsnapshot/alpha.0/localhost/
TAR=/tmp/raspbian-rsnapshot.tgz
sudo rm -f $TAR
sudo tar cfz $TAR *
scp $TAR torben@192.168.178.112:/media/data/sicher/raspi/raspbian/

# echo sicher-influxdb.sh
# /home/pi/bin/sicher-influxdb.sh

echo ... influxdb
DIR=/sicher/influxdb/influxdb.0
cd $DIR
TAR=/tmp/raspbian-influxdb.tgz
sudo rm -f $TAR
sudo tar cfz $TAR *
scp $TAR torben@192.168.178.112:/media/data/sicher/raspi/raspbian/

echo ... grafana
DIR=/sicher/grafana/grafana.0
cd $DIR
TAR=/tmp/raspbian-grafana.tgz
sudo rm -f $TAR
sudo tar cfz $TAR *
scp $TAR torben@192.168.178.112:/media/data/sicher/raspi/raspbian/

