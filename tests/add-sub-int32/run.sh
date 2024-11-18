#!/bin/bash
# deyuan, 09/25/2024

if [ -n "$1" ]; then
    genlib="$1"
else
    genlib=../../src/genlibs/inv_and_xnor_mux.genlib
fi

verilog=../../src/verilog/add_sub_int32.v

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs

