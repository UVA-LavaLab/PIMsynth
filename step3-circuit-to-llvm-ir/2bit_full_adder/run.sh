apptainer exec ../../myapptainer.sif python3 ../script/main.py -i ../../step2-aig-to-circuit/2bit_full_adder/result.blif -m "fullAdder2" -o ./fulladder2.cpp

apptainer exec ../../myapptainer.sif /u/uab9qt/worktable/llvm_repos/bit-serial-compiler/llvm-build/bin/clang++ -S -emit-llvm fulladder2.cpp -o fulladder2.ll
