# bit-serial-compiler

## Prerequisite

In Linux environment, make sure `apptainer` command is available:
```
$ apptainer --version
apptainer version 1.3.3
```

## How to build

Check out this repo and all submodules:
```
git clone --recurse-submodules https://github.com/UVA-LavaLab/PIMsynth.git
```

Build apptainer sif image:
```
./apptainer-build.sh
```

Build all submodules:
```
./apptainer-run.sh build_all.sh
```

Run an example:
```
cd testbench/
../apptainer-run.sh ./run_benchmark.sh inv_nand 4 digital add_int32
```

## For developers

Setup fetch/push remote (skip if you don't modify these submodules):
```
# for each submodule, use originial url to fetch, and use local url to push
cd llvm-project
git remote set-url --push origin https://github.com/UVA-LavaLab/PIMsynth.git
git remote -v
cd abc
git remote set-url --push origin https://github.com/UVA-LavaLab/PIMsynth.git
git remote -v
cd yosys
git remote set-url --push origin https://github.com/UVA-LavaLab/PIMsynth.git
git remote -v
cd PIMeval-PIMbench
git remote set-url --push origin https://github.com/UVA-LavaLab/PIMsynth.git
git remote -v
```

Build apptainer sif image:
```
# command to build apptainer sif image
apptainer build myapptainer.sif myapptainer.def

# command to run apptainer
apptainer exec myapptainer.sif <command>

# helper utility to build apptainer sif image
./apptainer-build.sh

# helper utility to run apptainer
./apptainer-run.sh <command>
```

Build LLVM (must be under llvm-build):
```
mkdir llvm-build
cd llvm-build
../apptainer-run.sh cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -G "Unix Makefiles"
../apptainer-run.sh make -j10
```

Build abc:
```
cd abc
../apptainer-run.sh make -j10
```

Build yosys:
```
cd yosys
# in case yosys/abc submodule has not been checked out
git submodule update --init
# build
../apptainer-run.sh make -j10
```

Build PIMeval:
```
cd PIMeval-PIMbench
../apptainer-run.sh make -j10
```

Run bit-serial compiler after building all submodules:
```
cd testbench/
../apptainer-run.sh ./run_benchmark.sh inv_nand 4 digital add_int32
```

## Methodology

```
    *.v (verilog input)
     |
     v
    yosys
     |
     v
    *.blif (tech-independent)
     |
     v  <-- *.genlib (bit-serial ISA)
    abc
     |
     v
    *.blif
     |
     v
    blif translator
     |
     v
    *.c (IR)
     |
     v
    clang
     |
     v
    *.s (risc-v assembly)
     |
     v
    asm translator
     |
     v
    *.hpp (bit-serial micro-program) --> PIMeval simulation
```

## Source Code Organization

Main bit-serial compiler flow:
* `bit_serial_compiler.py`: Main entry to call bit-serial compiler

Submodules:
* `abc`: ABC logic synthesizer submodule
* `yosys`: Yosys logic synthesizer submodule
* `llvm-project`: LLVM compiler submodule
* `PIMeval-PIMbench`: PIM simulator

Source files:
* `src/`
  * `genlibs/`: GenLib definitions as bit-serial ISA
  * `verilog/`: Verilog source code
  * `blif-translator/`: BLIF translator written in Python
  * `asm-parser/`: RISC-V ASM parser and PIM code generator written in Python
  * `scripts/`: Utility scripts
* `benchmarks/`: Verilog source code written in bit-serial manner
* `testbench/`
  * `run_benchmark.sh`: Script to compile a benchmark Verilog with a specific bit-serial ISA and number of registers

Test directories:
* `tests/`: Testcases

## Bit-Serial Compiler UI

```
 ---------------------
| Bit-Serial Compiler |
 ---------------------
usage: bit_serial_compiler.py [-h] [--verilog [files] [[files] ...]] [--genlib [file]] [--blif [file]]
                              [--c [file]] [--asm [file]] [--num-regs N]
                              [--output [filename]] [--outdir [path]]
                              [--from-stage [stage]] [--to-stage [stage]] [--clang-g]

options:
  -h, --help            show this help message and exit
  --verilog [files] [[files] ...]
                        Input Verilog files
  --genlib [file]       Input GenLib file
  --blif [file]         Input BLIF file
  --c [file]            Input C file
  --asm [file]          Input ASM file
  --num-regs N          Number of registers 2~7
  --output [filename]   Output filename without suffix
  --outdir [path]       Output location, default current dir
  --from-stage [stage]  From stage: verilog (default), blif, c, asm, pim
  --to-stage [stage]    To stage: verilog, blif, c, asm, pim (default)
  --clang-g             Toggle clang -g, default true

how to use:
  Input requirements:
    --from-stage verilog    require --verilog and --genlib
    --from-stage blif       require --blif
    --from-stage c          require --c
    --from-stage asm        require --asm
```

