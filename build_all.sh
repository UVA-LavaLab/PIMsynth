#!/bin/bash
# Build all submodules

# build llvm
mkdir -p llvm-build
cd llvm-build
cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -G "Unix Makefiles"
make -j10
cd ..

# build abc
cd abc
make -j10
cd ..

# build yosys
cd yosys
make -j10
cd ..

# build PIMeval
cd PIMeval-PIMbench
make -j10
cd ..

