# deyuan, 09/25/2024

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_2bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 2reg \
    --outdir outputs \
    --num-regs 2

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_2bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 3reg \
    --outdir outputs \
    --num-regs 3

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_2bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 4reg \
    --outdir outputs \
    --num-regs 4

../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_2bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 5reg \
    --outdir outputs \
    --num-regs 5

echo "lw/sw count:"
echo "2-reg:" `grep -E 'lw|sw' outputs/2reg.s | wc -l`
echo "3-reg:" `grep -E 'lw|sw' outputs/3reg.s | wc -l`
echo "4-reg:" `grep -E 'lw|sw' outputs/4reg.s | wc -l`
echo "5-reg:" `grep -E 'lw|sw' outputs/5reg.s | wc -l`

