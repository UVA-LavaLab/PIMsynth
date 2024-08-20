# bit-serial-compiler

# How to build
```
# clone
git clone --recursive-submodules https://github.com/deyuan/bit-serial-compiler.git

# make sure submodules use originial fetch url but local push url
cd llvm-project
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v
cd abc
git remote set-url --push origin https://github.com/deyuan/bit-serial-compiler.git
git remote -v

# build apptainer
apptainer build myapptainer.sif myapptainer.def

# build llvm
mkdir llvm-build
cd llvm-build
apptainer exec ../myapptainer.sif cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -G "Unix Makefiles"
apptainer exec ../myapptainer.sif make -j10

```
