#!/bin/bash

# move to project root folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 
cd "${DIR}/../"

die() {
    printf 'Error: Invalid argument for %s\n' "$1" >&2
    usage
    exit 1
}


PARAMS=""
while (( "$#" )); do
  case "$1" in
    -h|--help)
      usage
      exit
      ;;
    -m|--mode)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        export AQUA_MODE=$2
        shift 2
      else
        die $1
      fi
      ;;
    -q|--quiz)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        export AQUA_QUIZ=$2
        shift 2
      else
        die $1
      fi
      ;;
    -a|--app)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        export AQUA_APP=$2
        shift 2
      else
        die $1
      fi
      ;;

    # unsupported flags
    -*|--*=) 
      echo "Error: Unsupported flag $1" >&2
      usage
      exit 1
      ;;

    # preserve positional arguments
    *) 
      PARAMS="$@"
      break
      ;;
  esac
done

# set positional arguments in their proper place
eval set -- "$PARAMS"
