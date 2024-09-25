
../../apptainer-run.sh ../../bit_serial_compiler.py \
    --verilog ../../src/verilog/full_adder_1bit.v \
    --genlib ../../src/genlibs/inv_and_xnor_mux.genlib \
    --output 4reg \
    --outdir outputs

