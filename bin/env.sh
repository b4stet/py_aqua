#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

# application config
if [ -z "${AQUA_APP}" ];
then
    export AQUA_APP=./config/app_default.yml
fi

# usage
if [ "$#" -lt 1 ];
then
    echo "Usage: $0 <mode> [<path/to/quiz_config.yml>]"
    exit 1
fi

# set mode
test_mode=$(echo 'user reviewer' | grep -Fw "$1")
if [ -z "${test_mode}" ];
then
    echo "Unknown mode. Should be 'user' or 'reviewer'."
    exit 1
fi
export AQUA_MODE="$1"

# set quiz config if provided
quiz_config='./config/quiz_default.yml'
if [ "$#" -eq 2 ];
then
    quiz_config="$2"
fi
export AQUA_QUIZ=${quiz_config}
