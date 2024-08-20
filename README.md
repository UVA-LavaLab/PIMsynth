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
* Step 3: Convert circuit into LLVM IR
  * Input: Circuit
  * Output: LLVM IR
  * Tool:
* Step 4: Instruction scheduling and register allocation
  * Input: LLVM IR
  * Output:
  * Tool: llvm
* Step 5: Convert to bit-serial micro-program


