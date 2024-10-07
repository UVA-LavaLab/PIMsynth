#!/bin/bash
# deyuan, 09/25/2024

if [ -n "$1" ]; then
    genlib="$1"
else
    genlib=../../src/genlibs/inv_and_xnor_mux.genlib
fi

verilog=../../src/verilog/full_adder_1bit.v

echo "GenLib = $genlib"
echo "Verilog = $verilog"

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 2reg --num-regs 2

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 3reg --num-regs 3

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 4reg --num-regs 4

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 5reg --num-regs 5

echo "lw/sw count:"
echo "2-reg:" `grep -E 'lw|sw' outputs/2reg.s | wc -l`
echo "3-reg:" `grep -E 'lw|sw' outputs/3reg.s | wc -l`
echo "4-reg:" `grep -E 'lw|sw' outputs/4reg.s | wc -l`
echo "5-reg:" `grep -E 'lw|sw' outputs/5reg.s | wc -l`

