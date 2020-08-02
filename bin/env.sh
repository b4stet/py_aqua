#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

if [ -z "$AQUA_APP" ];
then
    export AQUA_APP=./config/app_default.yml
fi

if [ "$#" -lt 2 ];
then
    echo "Usage: $0 <mode> <path/to/quiz_config.yml>"
    exit 1
fi

test_mode=$(echo 'user reviewer' | grep -Fw "$1")
if [ -z "${test_mode}" ];
then
    echo "Unknown mode. Should be 'user' or 'reviewer'."
    exit 1
fi
export AQUA_MODE="$1"

export AQUA_QUIZ="$2"