#!/bin/bash
# deyuan, 09/25/2024

if [ -n "$1" ]; then
    genlib="$1"
else
    genlib=../../src/genlibs/inv_and_xnor_mux.genlib
fi

verilog=../../src/verilog/add_int32_e.v

echo "GenLib = $genlib"
echo "Verilog = $verilog"

mkdir -p outputs

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 2reg --num-regs 2 | tee ./outputs/2reg.log

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 3reg --num-regs 3 | tee ./outputs/3reg.log

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 4reg --num-regs 4 | tee ./outputs/4reg.log

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog $verilog --genlib $genlib --outdir outputs \
    --output 5reg --num-regs 5 | tee ./outputs/5reg.log

echo "Verilog = $verilog"
echo "2-reg:" `grep -E '#R' outputs/2reg.log`
echo "3-reg:" `grep -E '#R' outputs/3reg.log`
echo "4-reg:" `grep -E '#R' outputs/4reg.log`
echo "5-reg:" `grep -E '#R' outputs/5reg.log`

