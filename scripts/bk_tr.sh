#!/bin/bash

# array for commands to be excuted

ar_cmd[0]="./random_wget.sh &"
ar_cmd[1]="./rand_scp.sh &"
ar_cmd[2]="./rand_email.sh &"
ar_cmd[3]="hydra -L username.txt -P pass.txt 192.168.33.15 ssh &"
ar_cmd[4]="./random_ftp.sh &"

sz_cmd_ar=${#ar_cmd[@]}
rm -rf /home/sudip/dumps/** 
while true
do
	rand_i=$(($RANDOM % $sz_cmd_ar))
	rand_sleep=$(( $RANDOM % 10 + 1 ))
	eval ${ar_cmd[$rand_i]}
	sleep $rand_sleep
	#echo $(( $RANDOM % 10 + 1 ))
done
