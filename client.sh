#!/bin/bash

if [ -z "$API_KEY" ]; then
    echo "API_KEY is not set. Please set the API_KEY environment variable."
    exit 1
fi

BASE_URL='http://127.0.0.1:5000'

# base line: need two parameters, action & id
# API is querying based on network:'name' 
# and userInfo:username'
if [ -z "$2" ]; then
    echo "Usage: $0 lock/checklock/unlock input"
    exit 2
fi

ENDPOINT="/api/$1"


curl -X GET \
     -H "API-KEY: $API_KEY" \
     "$BASE_URL$ENDPOINT?input=$2"