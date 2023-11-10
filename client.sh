#!/bin/bash

if [ -z "$API_KEY" ]; then
    echo "API_KEY is not set. Please set the API_KEY environment variable."
    exit 1
fi

BASE_URL='http://127.0.0.1:5000'

# if neither parameters are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 lock/checklock/unlock network [additional_parameters]"
    exit 1
fi

ENDPOINT="/api/$1"

# can do logic revolving around
# parameters, right now not
# sure what they are
curl -X GET \
     -H "API-KEY: $API_KEY" \
     "$BASE_URL$ENDPOINT?network=$2"