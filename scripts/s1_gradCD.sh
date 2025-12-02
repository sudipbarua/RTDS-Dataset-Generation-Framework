#!/bin/bash
rate=100M
# list of video number
list="16 15 10 8 7 6 5"
# download video. We use & at the end of the command to execute it in the background
wget -P /home/sudip/dumps/ --limit-rate=$rate http://www.video18m.com/video18m.mp4 &
sleep 50
# start gradual rate increment
for v in $list
do
        wget -P /home/sudip/dumps/ --limit-rate=$rate http://www.video"$v"m.com/video"$v"m.mp4 &
        # sleep to simulate gradual increment of rate
        sleep 10
done
# remove the files forcefully
rm -rf /home/sudip/dumps/** 
