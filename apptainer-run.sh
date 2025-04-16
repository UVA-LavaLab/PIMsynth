#!/bin/bash
# A wrapper script to run apptainer

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# Add ./ prefix to the first file argument
if [[ -f "$1" && "$1" != /* ]]; then
	set -- "./$1" "${@:2}"
fi

apptainer exec $SCRIPT_DIR/myapptainer.sif "$@"

