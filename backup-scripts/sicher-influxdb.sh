#!/bin/bash

# Dumps a backup of InfluxDB data
# keeps 4 backups using hardlinks in case DB was unchanged

TARGET=/sicher/influxdb

# keep 4 backups using hardlinks
rm -r $TARGET/influxdb.4
mv $TARGET/influxdb.3 $TARGET/influxdb.4
mv $TARGET/influxdb.2 $TARGET/influxdb.3
mv $TARGET/influxdb.1 $TARGET/influxdb.2
mv $TARGET/influxdb.0 $TARGET/influxdb.1

influxd backup -portable $TARGET/influxdb.0

