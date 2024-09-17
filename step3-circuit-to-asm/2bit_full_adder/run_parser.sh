
apptainer exec ../../myapptainer.sif python3 ../../src/blif-parser/main.py -f asm -i ../../step2-aig-to-circuit/2bit_full_adder/result.blif -m "fullAdder2" -o ./fulladder2.c

