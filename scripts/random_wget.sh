#!/bin/bash
# list of video numbers
list="18 16 15 10 7 6 5"
# store all vars in ar_links array
i=0
for v in $list
do
	ar_links[$i]="http://www.video"$v"m.com/video"$v"m.mp4"
	i=$((i+1))
done
# size of the array of links
sz_var_ar=${#ar_links[@]}
rand_i=$(($RANDOM % $sz_var_ar))
wget -P /home/sudip/dumps/ --limit-rate=100K ${ar_links[$rand_i]} &
