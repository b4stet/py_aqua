#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

usage() { 
    echo "Usage: $0 [-q/--quiz <path/to/quiz_config.yml>] [-a/--app <path/to/app_config.yml>]" 1>&2
    exit 1
}
source ./bin/env.sh

export FLASK_APP=cli.py
flask ${@}