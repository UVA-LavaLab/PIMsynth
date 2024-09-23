
apptainer exec ../../myapptainer.sif python3 ../../src/blif-parser/main.py -f asm -i ../../step2-aig-to-circuit/1bit_full_adder/result.blif -m "fullAdder1" -o ./fulladder1.c

