# bit-serial-compiler

# How to build
```
# clone
git clone --recursive-submodules https://github.com/deyuan/bit-serial-compiler.git

# update fetch and push url of submodules
# do not push to original llvm-project repo
cd llvm-project
git remote set-url origin https://github.com/llvm/llvm-project.git
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
