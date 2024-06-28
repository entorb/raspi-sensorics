#!/usr/bin/python3

"""Read size of InfluxDB."""

import subprocess

from InfluxUploader import InfluxUploader

# uses Linux du command to fetch the size of the subdirs in a dir
# in kB

mydir = "/var/lib/influxdb/data"

process = subprocess.run(  # noqa: S603
    ["sudo", "du", "--max-depth=1", mydir],
    capture_output=True,
    text=True,
    check=False,
)
s = process.stdout

L = s.split("\n")
L.pop()  # returns and removes the last empty line
# print (L)

d = {}
for line in L:
    L2 = line.split("\t")
    myBytes = int(L2[0])
    myFolder = L2[1].replace(mydir + "/", "")
    if myFolder == mydir:
        myFolder = "total"
    d[myFolder] = myBytes


influx = InfluxUploader(verbose=True)
influx.upload(measurement="influxdb_du", fields=d, tags={})
