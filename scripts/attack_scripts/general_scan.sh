#!/bin/bash
# logging
log_path="/home/ubuntu/attack_logs/nmap_scanning_$(date +'%Y-%m-%d_%H:%M:%S').log"
log_server="10.10.2.74"

src_ip="10.10.2.189"
# helper function for logging: usage> scanner "description" "IP" "nmap command"
function scanner {
    echo "$(date +'%Y-%m-%d %H:%M:%S.%N') starting scan : $1 : source - $src_ip destination - $2 " | sshpass -p "admin" ssh ubuntu@$log_server "cat >> $log_path"
    $3 $2
    echo "$(date +'%Y-%m-%d %H:%M:%S.%N') completing scan : $1 : source - $src_ip destination - $2 " | sshpass -p "admin" ssh ubuntu@$log_server "cat >> $log_path"
    echo "$(date +'%Y-%m-%d %H:%M:%S.%N') Sleeping after for 1 min after $1" | sshpass -p "admin" ssh ubuntu@$log_server "cat >> $log_path"
    sleep 20
}
# intense scanning
scanner "intense scanning" "10.10.1.107" "nmap -T4 -A -v"

# intense scanning and UDP
scanner "intense scanning and UDP" "10.10.1.107" "nmap -sS -sU -T4 -A -v"

# intense scanning TCP ports
scanner "intense scanning TCP ports" "10.10.1.107" "nmap -p 1-65535 -T4 -A -v"

# intense scanning no ping
scanner "intense scanning no ping" "10.10.1.107" "nmap -T4 -A -v -Pn"

# ping scan
scanner "intense scanning no ping" "10.10.1.107" "nmap -sn"

# quick scan
scanner "quick scan" "10.10.1.107" "nmap -T4 -F"

# quick scan plus
scanner "quick scan plus" "10.10.1.107" "nmap -sV -T4 -O -F --version-light"

# quick traceroute
scanner "quick traceroute" "10.10.1.107" "nmap -sn --traceroute"

# regular scan
scanner "quick traceroute" "10.10.1.107" "nmap"

# Slow comprehensive scan
scanner "quick traceroute" "10.10.1.107" "nmap -sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script \"default or (discovery and safe)\""

