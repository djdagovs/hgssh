#!/bin/bash
# list all repositorys, and check if repository folder exists

fgfile="/home/repo/hgssh3.conf"

for i in $(cat $cfgfile |egrep location |awk -F '= ' {'print $2'}) ; do 
  [ -d $i ] && echo "$i" || echo "$i => missing"; 
done
