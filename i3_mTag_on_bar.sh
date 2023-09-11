#!/bin/bash

i3status --config /etc/i3status.conf | while :
do
	read line
	l1=$(mtag -custom)
	echo "$l1 | $line" || exit 1	
done
