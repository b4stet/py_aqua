#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

source ./bin/env.sh

python3 -m web