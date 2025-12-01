#!/bin/bash
# A wrapper script to run apptainer

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
# Check if we're already inside a container
if [ -n "$APPTAINER_CONTAINER" ] || [ -n "$SINGULARITY_CONTAINER" ]; then
    exec "$@"
fi

# Add ./ prefix to the first file argument
if [[ -f "$1" && "$1" != /* ]]; then
	set -- "./$1" "${@:2}"
fi

apptainer exec $SCRIPT_DIR/myapptainer.sif "$@"
