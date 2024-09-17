
apptainer exec ../../myapptainer.sif ../../llvm-build/bin/clang -O3 -target riscv32-unknown-elf -S fulladder2.c -o fulladder2.s

