#!/bin/bash

if [ $# -ne 3 ]; then
    echo "This script accepts exactly 3 arguments: the DC name where Catzilla fabric is being deployed and the rack type (Brick or Spine) and the number of the Brick rack or Spine rack"
    echo "For example:"
    echo "$0 IAD7 b 1    or $0 IAD7 s 1"
    exit 1
else
    DC_NAME=$1
    DC_NAME=$(echo $DC_NAME | awk '{print tolower($0)}')
    rack_type=$2
    rack_type=$(echo $rack_type| awk '{print tolower($0)}')
    rack_no=$3
    rack_no=$(echo $rack_no| awk '{print tolower($0)}')
    kinit -f
    echo "You're about to create Catzilla console entries for: $1 $2$3. Is this what you want to do? (Y/N)"
    read ANSWER
    if [ $(echo $ANSWER | awk '{print tolower($0)}') != "y" ]; then
        echo "Exiting..."
        exit 1
    fi
fi

if [ "$rack_type" == b ]; then

# Catzilla Brick rack #1
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2003&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r1&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2004&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r3&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2005&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r5&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2006&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r7&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2007&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r9&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2008&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r11&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2009&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r13&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2010&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r15&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2019&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r1&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2020&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r3&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2021&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r5&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2022&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r7&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2023&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r9&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2024&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r11&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2025&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r13&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2026&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r15&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r1&Server_Port=2018&Host_Name=$DC_NAME-br-ctz-f1mgmt-b$rack_no-r1&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"

# Catzilla Brick rack #1
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2003&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r2&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2004&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r4&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2005&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r6&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2006&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r8&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2007&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r10&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2008&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r12&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2009&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r14&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2010&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t1-r16&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2019&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r2&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2020&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r4&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2021&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r6&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2022&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r8&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2023&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r10&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2024&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r12&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2025&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r14&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2026&Host_Name=$DC_NAME-br-ctz-f1b$rack_no-t2-r16&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-b$rack_no-r2&Server_Port=2018&Host_Name=$DC_NAME-br-ctz-f1mgmt-b$rack_no-r2&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"

else if [ "$rack_type" == s ]; then

# Catzilla spine rack 
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2003&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r1&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2004&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r2&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2005&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r3&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2006&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r4&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2007&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r5&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2008&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r6&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2009&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r7&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2010&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r8&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2019&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r9&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2020&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r10&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2021&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r11&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2022&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r12&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2023&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r13&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2024&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r14&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2025&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r15&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2026&Host_Name=$DC_NAME-br-ctz-f1s$rack_no-t3-r16&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"
curl --negotiate -u : -k --data "Server_Name=$DC_NAME-br-ctz-f1oob-s$rack_no-r1&Server_Port=2018&Host_Name=$DC_NAME-br-ctz-f1mgmt-s$rack_no-r1&action=Add%20To%20Database" "https://network-console.amazon.com/console-port-db/?action=add"

fi
fi
exit 0
