#!/bin/bash
H=www.wavecafe1234.com 
U=vagrant 
pass=vagrant 
# list of video numbers
list="18 16 15 10 7 6 5"
# store all vars in ar_files and ar_links array
i=0
for v in $list
do
	ar_files[$i]="files/mail_body_"$v".txt"
	i=$((i+1))
done
# size of the array of files
sz_var_ar=${#ar_files[@]}
rand_i=$(($RANDOM % $sz_var_ar))

ftp -inv $H <<EOF 
user $U $pass 
mput ${ar_files[$rand_i]} 
bye
EOF

