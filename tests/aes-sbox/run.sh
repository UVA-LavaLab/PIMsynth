#!/bin/bash
# deyuan, 09/25/2024

if [ -n "$1" ]; then
    genlib="$1"
else
    genlib=../../src-genlib/inv_and_xor.genlib
fi

verilog=../../src-verilog/benchmarks/aes_sbox_usuba.v

python3 ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs --num-regs 4 --to-stage pim

make clean
make
./test
