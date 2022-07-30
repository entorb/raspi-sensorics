#!/bin/bash

# copies Grafana data
# keeps 4 backups using hardlinks

SOURCE=/var/lib/grafana
TARGET=/sicher/grafana


sudo rm -r $TARGET/grafana.4
mv $TARGET/grafana.3 $TARGET/grafana.4
mv $TARGET/grafana.2 $TARGET/grafana.3
mv $TARGET/grafana.1 $TARGET/grafana.2
mv $TARGET/grafana.0 $TARGET/grafana.1

sudo cp -al $SOURCE $TARGET/grafana.0

