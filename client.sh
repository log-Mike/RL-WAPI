#!/bin/bash

if [ -z "$API_KEY" ]; then
    echo "API_KEY is not set. Please set the API_KEY environment variable."
    exit 1
fi

BASE_URL='http://127.0.0.1:5000'

# !=2  arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 lock/checklock/unlock user/network/network"
    exit 2
fi

if [ "$1" == "lock" ] || [ "$1" == "unlock" ]; then
    method="PATCH"
elif [ "$1" == "checklock" ]; then
    method="GET"
else
    echo "Not an action"
    exit 3
fi

curl -X "$method" \
     -H "API-KEY: $API_KEY" \
     "$BASE_URL/api/$1?input=$2"