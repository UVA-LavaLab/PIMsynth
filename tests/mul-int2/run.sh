#!/bin/bash

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
PROJ_ROOT=$(git rev-parse --show-toplevel)

#$PROJ_ROOT/apptainer-run.sh $SCRIPT_DIR/run_benchmark.sh "$@"
#$PROJ_ROOT/apptainer-run.sh $SCRIPT_DIR/run_benchmark.sh inv_nand 4 mul_int2
$PROJ_ROOT/apptainer-run.sh $SCRIPT_DIR/run_benchmark.sh inv_and_xnor_mux 4 mul_int2

