
apptainer exec ../../myapptainer.sif ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_1bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 2reg \
    --outdir outputs \
    --num-regs 2

apptainer exec ../../myapptainer.sif ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_1bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 3reg \
    --outdir outputs \
    --num-regs 3

apptainer exec ../../myapptainer.sif ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_1bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 4reg \
    --outdir outputs \
    --num-regs 4

apptainer exec ../../myapptainer.sif ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_1bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 5reg \
    --outdir outputs \
    --num-regs 5

