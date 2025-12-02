#!/bin/bash
# list of video numbers
list="18 16 15 10 7 6 5"
# store all vars in ar_links array
i=0
for v in $list
do
	ar_atch[$i]="files/video"$v"m.mp4"
	ar_body[$i]="files/mail_body_"$v".txt"
	i=$((i+1))
done
# size of the array of links
sz_var_ar=${#ar_atch[@]}
rand_i=$(($RANDOM % $sz_var_ar))
mutt -s ""$rand_i" no. mail with "${ar_atch[$rand_i]}"" -a ${ar_atch[$rand_i]} -- tnikola230@gmail.com < ${ar_body[$rand_i]} &
