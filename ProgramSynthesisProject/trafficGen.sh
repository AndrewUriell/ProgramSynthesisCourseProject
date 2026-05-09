#!/bin/bash

TARGET="192.168.56.104"

echo "===== 1. Ping test ====="
ping -c 3 $TARGET

echo
echo "===== 2. SSH test (port 22) ====="
nc -zv -w 2 $TARGET 22


echo
echo "===== 3. DNS test (test.local) ====="
dig @$TARGET test.local

echo
echo "===== 4. HTTP test ====="
curl -I http://$TARGET

echo
echo "===== 5. TCP test on port 4444 ====="
nc -zv -w 2 $TARGET 4444

echo
echo "===== 6. UDP test on port 9999 ====="
echo "UDP test" | nc -u -z -v -w 2 $TARGET 9999


echo
echo "===== 7. Nmap Scan ====="
nmap -A $TARGET


echo
echo "===== Script Complete ====="






