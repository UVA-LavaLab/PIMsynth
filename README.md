# bit-serial-compiler

## How to build
Check out current repo:
```
git clone --recurse-submodules https://github.com/deyuan/bit-serial-compiler.git
```

Optional: Setup fetch/push remote if need to modify submodule:
```
# for each submodule, use originial url to fetch, and use local url to push
cd llvm-project
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v
cd abc
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v
cd yosys
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v
```

Build apptainer:
```
# command to build apptainer
apptainer build myapptainer.sif myapptainer.def

# command to run apptainer
apptainer exec myapptainer.sif <command>

# helper utility to build apptainer
./apptainer-build.sh

# helper utility to run apptainer
./apptainer-run.sh <command>
```

Build LLVM:
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

## Methodology
* Step 1: Convert verilog into AIG
  * Input: Verilog implementation of targeted bit-serial functionality
  * Output: AIG
  * Tool: abc
* Step 2: Convert AIG into circuit
  * Input: AIG, customized genlib library with bit-serial ISA
  * Output: Circuit in blif format
  * Tool: abc

Plan A:
* Step 3: Convert circuit into LLVM IR
  * Input: Circuit
  * Output: LLVM IR
  * Tool: Blif parser utility, clang++
* Step 4: Instruction scheduling and register allocation
  * Input: LLVM IR
  * Output:
  * Tool: llvm
* Step 5: Convert to bit-serial micro-program

Plan B:
* Step 3: Convert circuit into C with RISC-V inline assembly and register clobber
  * Input: Circuit
  * Output: C with inline assembly
  * Tool: Blif parser utilty
* Step 4: Perform instruction scheduling, register allocation and spilling
  * Input: C
  * Output: RISC-V .s assembly
  * Tool: clang
* Step 5: Convert to bit-serial micro-program

## Source Code Organization

Main bit-serial compiler flow:
* `bit_serial_compiler.py`: Main entry to call bit-serial compiler

Submodules:
* `abc`: ABC logic synthesizer submodule
* `yosys`: yosys logic synthesizer submodule
* `llvm-project`: LLVM compiler submodule
* `llvm-build`: Required location to build llvm

Source files:
* `src/`
  * `genlibs/`: GenLib definitions for bit-serial variants
  * `verilog/`: Verilog source code
  * `blif-parser/`: BLIF parser and C/C++ code generator written in Python
  * `asm-parser/`: RISC-V ASM parser and PIM code generator written in Python

Test directories:
* `tests/`: Testcases

## Bit-Serial Compiler UI

```
 ---------------------
| Bit-Serial Compiler |
 ---------------------
usage: bit_serial_compiler.py [-h] [--verilog [file]] [--genlib [file]] [--blif [file]]
                              [--c [file]] [--asm [file]] [--num-regs N]
                              [--output [filename]] [--outdir [path]]
                              [--from-stage [stage]] [--to-stage [stage]] [--clang-g]

options:
  -h, --help            show this help message and exit
  --verilog [file]      Input Verilog file
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

