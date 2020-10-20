#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

usage() { 
    echo "Usage: $0 -m/--mode <user|reviewer> [-q/--quiz <path/to/quiz_config.yml>] [-a/--app <path/to/app_config.yml>]" 1>&2
    exit 1
}
source ./bin/env.sh

# verify mode
verify_mode=$(echo 'user reviewer' | grep -Fw "${AQUA_MODE}")
if [ -z "${verify_mode}" ];
then
    die '--mode'
fi


python3 -m web