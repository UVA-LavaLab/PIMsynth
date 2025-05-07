#!/bin/bash
# deyuan, 09/25/2024

if [ -n "$1" ]; then
    genlib="$1"
else
    genlib=../../src-genlib/inv_and_xnor_mux.genlib
fi

verilog=../../src-verilog/benchmarks/aes_inverse_sbox.v

../../apptainer-run.sh python3 ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs --num-regs 3

