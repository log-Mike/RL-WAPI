#!/bin/bash

if [ -z "$API_KEY" ]; then
    echo "API_KEY is not set. set the API_KEY environment variable."
    exit 1
fi

BASE='127.0.0.1'
BASE_PORT='5000'

# check if reachable after n seconds
nc -z -w 5 $BASE $BASE_PORT
if [ $? -ne 0 ]; then
    echo "API not reachable"
    exit 2
fi
	
# !=2  arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 lock/checklock/unlock user/network/network"
    exit 3
fi

if [ "$1" == "lock" ] || [ "$1" == "unlock" ]; then
    method="PATCH"
elif [ "$1" == "checklock" ]; then
    method="GET"
else
    echo "Not an action, needs to be (lock/unlock/checklock)"
    exit 4
fi

api_output=$(curl -sX  "$method" \
     -H "API-KEY: $API_KEY" \
     "http://$BASE:$BASE_PORT/api/$1?input=$2")

IFS='-' read -r exit_code message <<< "$api_output"

message="$(echo "${message}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

echo $message
exit $exit_code
