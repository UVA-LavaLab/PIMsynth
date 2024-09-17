
apptainer exec ../../myapptainer.sif ../../llvm-build/bin/clang -O3 -target riscv32-unknown-elf -S fulladder1.c -o fulladder1.s

