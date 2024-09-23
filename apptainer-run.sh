#!/bin/bash
# A wrapper script to run apptainer

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

apptainer exec $SCRIPT_DIR/myapptainer.sif "$@"

