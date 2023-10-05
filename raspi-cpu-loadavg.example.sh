#!/bin/bash

VALUE="`cat /proc/loadavg | cut -f1 -d" "`"
echo $VALUE

# curl -i -XPOST "http://localhost:8086/write?db=statsdemo" --data-binary "cpu,host=serverA value=0.21"
 curl -i \
	-u uwrite:mypassword \
 	-XPOST "http://localhost:8086/write?db=mydb&precision=s" \
 	--data-binary "cpu,host=serverA value=$VALUE"


# 	--data-urlencode "u=uwrite" \
#	--data-urlencode "p=fuK1EwDGQIQWlGdhzl4w" \
