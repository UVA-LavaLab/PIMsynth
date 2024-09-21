# bit-serial-compiler

# How to build
```
# clone
git clone --recurse-submodules https://github.com/deyuan/bit-serial-compiler.git

# make sure submodules use originial fetch url but local push url
cd llvm-project
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v
cd abc
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v

# build apptainer
apptainer build myapptainer.sif myapptainer.def

# build abc
cd abc
apptainer exec ../myapptainer.sif make

# build llvm
mkdir llvm-build
cd llvm-build
apptainer exec ../myapptainer.sif cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -G "Unix Makefiles"
apptainer exec ../myapptainer.sif make -j10

```

# Methodology
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

# Source Code Organization

* `bit_serial_compiler.py`: Main entry to call bit-serial compiler
* `abc`: ABC logic synthesizer submodule
* `llvm-project`: LLVM compiler submodule
* `src/`
  * `genlibs/`: GenLib definitions for bit-serial variants
  * `verilog/`: Verilog source code
  * `blif-parser/`: BLIF parser and C/C++ code generator written in Python
* `tests/`: Testcases
* To be deleted / restructured
  * `step1-verilog-to-aig/`: Workflow examples from Verilog to AIG
  * `step2-aig-to-circuit/`: Workflow examples from AIG to BLIF
  * `step3-circuit-to-llvm-ir/`: Workflow examples from BLIF to C++ to LLVM IR
  * `step3-circuit-to-asm/`: Workflow examples from BLIF to C to RISC-V assembly

# Bit-Serial Compiler UI

```
 ---------------------
| Bit-Serial Compiler |
 ---------------------
usage: bit_serial_compiler.py [-h] [--verilog [file]] [--genlib [file]] [--aig [file]]
                              [--blif [file]] [--c [file]] [--asm [file]] [--num-regs N]
                              [--output [filename]] [--outdir [path]] [--from-stage [stage]]
                              [--to-stage [stage]]

options:
  -h, --help            show this help message and exit
  --verilog [file]      Input Verilog file
  --genlib [file]       Input GenLib file
  --aig [file]          Input AIG file
  --blif [file]         Input BLIF file
  --c [file]            Input C file
  --asm [file]          Input ASM file
  --num-regs N          Number of registers 2~7
  --output [filename]   Output filename without suffix
  --outdir [path]       Output location, default current dir
  --from-stage [stage]  From stage: verilog (default), aig, blif, c, asm, pim
  --to-stage [stage]    To stage: verilog, aig, blif, c, asm, pim (default)

how to use:
  Input requirements:
    --from-stage verilog    require --verilog, require --genlib if --to blif or later stages
    --from-stage aig        require --aig and --genlib
    --from-stage blif       require --blif
    --from-stage c          require --c
    --from-stage asm        require --asm
```

