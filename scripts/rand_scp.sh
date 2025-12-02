#!/bin/bash
password="vagrant"
username="vagrant"
Ip="192.168.33.15"
FILES="files/*"
i=0
# store all the filepaths of the files from files folder in ar_files array
for f in $FILES
do
	ar_files[$i]="$f"
	i=$((i+1))
done
# size of the array of files
sz_var_ar=${#ar_files[@]}
rand_i=$(($RANDOM % $sz_var_ar))
sshpass -p "$password" scp -l 100 ${ar_files[$rand_i]} $username@$Ip:/home/vagrant/files &
