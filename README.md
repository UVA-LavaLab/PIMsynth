# PIMsynth: Bit-Serial Compiler

![License](https://img.shields.io/badge/license-MIT-green.svg)

## Description

PIMsynth is a compiler framework that translates Verilog-described operations into bit-serial microprograms for Processing-In-Memory (PIM) architectures. It supports both digital and analog PIM modes, multiple bit-serial ISAs, and configurable register counts.

## How to Build

Check out this repo and all git submodules:
```
git clone --recurse-submodules https://github.com/UVA-LavaLab/PIMsynth.git
```

### Build with Apptainer

Prerequisite: A Linux environment with `apptainer` is recommended to ease the build of third-party dependencies:
```bash
$ apptainer --version
apptainer version 1.3.3
# Build apptainer sif image:
./apptainer-build.sh
# Build all git submodules:
./apptainer-run.sh build_all.sh
```

### Build without Apptainer

You may directly run `build_all.sh` to build all submodules, and resolve any library dependencies in your Linux or macOS system as needed.

Please see section "For Developers" below.

### Run an Example

```bash
cd testbench/
# With apptainer
../apptainer-run.sh ./run_regressions.sh tasks_demo.txt
# Without apptainer
./run_regressions.sh tasks_demo.txt
```

Example outputs:
```
[1/1] inv_nand__4__digital__add_int8
  Compiling...
  Building tests...
  Running tests...
  PASSED

-------------------------------------------------------------------------------------------
ISA                | Regs | Mode    | Benchmark         |     #R |     #W |     #L | Status
-------------------------------------------------------------------------------------------
inv_nand           |    4 | digital | add_int8          |     39 |     31 |     94 | PASS
-------------------------------------------------------------------------------------------
```

## Compilation Pipeline

```
                *.v  (Verilog)
                 |
       +---------+---------+
       |       Yosys       |
       +---------+---------+
                 |
            *.blif  (tech-independent)
                 |
       +---------+---------+
       |        ABC        |  <-- *.genlib (bit-serial ISA)
       +---------+---------+
                 |
            *.blif  (mapped DAG)
                 |
       +---------+---------+
       |  BLIF Translator  |
       +---------+---------+
                 |
          *.pim_ir1  (PIM IR-1: pre-scheduling)
                 |
       +---------+---------+
       |     Scheduler     |  e.g. llvm-riscv
       +---------+---------+
                 |
          *.pim_ir2  (PIM IR-2: post-scheduling)
                 |
       +---------+---------+
       |      Code-Gen     |  e.g. PIMeval backend
       +---------+---------+
                 |
            *.hpp  (PIM microprogram)
                 |
       +---------+---------+
       |      Test-Gen     |
       +---------+---------+
                 |
           *.cpp + Makefile --> PIMeval simulation
```

### Compiler Stages

| Stage | Input | Output | Description |
|-------|-------|--------|-------------|
| `verilog` -> `blif` | `*.v`, `*.genlib` | `*.blif` | Logic synthesis via yosys + abc |
| `blif` -> `pim_ir1` | `*.blif` | `*.pim_ir1` | BLIF DAG translation to PIM IR-1 |
| `pim_ir1` -> `pim_ir2` | `*.pim_ir1` | `*.pim_ir2` | Scheduling, register allocation, spilling |
| `pim_ir2` -> `pim` | `*.pim_ir2` | `*.hpp` | Code generation for target PIM simulator |
| `pim` -> `test` | `*.hpp` | `*.cpp`, `Makefile` | Test program generation |

## Source Code Organization

Top-level entry:
* `bit_serial_compiler.py`: Main compiler driver

Source files (`src/`):
* `blif-translator/`: BLIF DAG parser and PIM IR-1 generator
* `schedulers/`: Scheduler dispatcher and implementations
  * `run_scheduler.py`: Common scheduler dispatcher
  * `llvm-riscv/`: LLVM/RISC-V based scheduler (IR-1 -> clang -> IR-2)
* `code-gen/`: Code generation from PIM IR-2 to target backends
  * `run_code_gen.py`: Code-gen dispatcher
  * `pim_ir2_to_pimeval_hpp_translator.py`: PIMeval HPP backend
  * `code_gen_pimeval_digital.py`: Digital PIM code generation
  * `code_gen_pimeval_analog.py`: Analog PIM code generation
  * `stats_generator.py`: Compiler statistics (#R/#W/#L)
* `utils/`: Shared utilities
  * `pim_ir1_reader.py`: PIM IR-1 parser
  * `pim_ir2_reader.py`: PIM IR-2 parser
  * `pim_target.py`: PIM target configuration and opcode definitions
  * `util.py`: Common helper functions
* `test-gen/`: PIMeval test program generator

ISA and benchmark inputs:
* `src-genlib/`: GenLib standard library definitions (bit-serial ISAs for logic synthesis)
* `src-verilog/`
  * `benchmarks/`: RTL of PIM operations optimized for bit-serial compilation
  * `submodules/`: Fundamental RTL modules (IMPL_TYPE: 0 xor-preferred, 1 maj-preferred)

Third-party dependencies:
* `yosys/`: Yosys logic synthesizer
* `abc/`: ABC logic synthesizer
* `llvm-project/`: LLVM compiler (clang for RISC-V)
* `PIMeval-PIMbench/`: PIM simulator and benchmarks

Testing:
* `testbench/`
  * `run_benchmark.sh`: Compile and test a single benchmark
  * `run_regressions.sh`: Batch regression runner with summary table
  * `tasks_regression.txt`: Full regression task list
  * `tasks_debug.txt`: Quick debug task list
  * `collect_results.py`: Results table collector

## Usage

```
./bit_serial_compiler.py [options]

Key options:
  --verilog [files]            Input Verilog files
  --genlib [file]              Input GenLib file (bit-serial ISA)
  --num-regs N                 Number of registers 
  --pim-mode {digital,analog}  PIM architecture mode (default: digital)
  --scheduler {llvm-riscv}     Scheduler to use (default: llvm-riscv)
  --output [filename]          Output filename without suffix
  --outdir [path]              Output directory (default: current dir)
```

### Example: Compile and Test

```bash
cd testbench/
./run_benchmark.sh inv_and_xnor_mux 4 digital add_int32
```

### Example: Run Regressions

```bash
cd testbench/
./run_regressions.sh tasks_regression.txt               # compile + simulate
./run_regressions.sh tasks_debug.txt --compile-only     # compile only
```

### Example Bit-Serial ISAs

| GenLib | Gates |
|--------|-------|
| `inv_nand` | INV, NAND |
| `inv_and_xnor_mux` | INV, AND, XNOR, MUX |
| `inv_and_xor` | INV, AND, XOR |
| `inv_maj_and_or` | INV, MAJ3, AND, OR (supports analog) |

## For Developers

Setup fetch/push remote (skip if you don't modify these git submodules):
```bash
# for each git submodule, use original url to fetch, and use local url to push
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
```bash
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
```bash
mkdir llvm-build
cd llvm-build
../apptainer-run.sh cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -G "Unix Makefiles"
../apptainer-run.sh make -j10
```

Build abc:
```bash
cd abc
../apptainer-run.sh make -j10
```

Build yosys:
```bash
cd yosys
# in case yosys/abc submodule has not been checked out
git submodule update --init
# build
../apptainer-run.sh make -j10
```

Build PIMeval:
```bash
cd PIMeval-PIMbench
../apptainer-run.sh make -j10
```

## Citation

If you use this repository in your research, please cite our paper:
* **PIMsynth: A Unified Compiler Framework for Bit-Serial Processing-In-Memory Architectures**  
* DOI: https://doi.org/10.1109/LCA.2025.3600588

```
@article{guo2025pimsynth,
  title={PIMsynth: A Unified Compiler Framework for Bit-Serial Processing-In-Memory Architectures},
  author={Guo, Deyuan and Gholamrezaei, Mohammadhosein and Hofmann, Matthew and Venkat, Ashish and Zhang, Zhiru and Skadron, Kevin},
  journal={IEEE Computer Architecture Letters},
  year={2025},
  publisher={IEEE}
}
```

## Contact

* Deyuan Guo - dg7vp AT virginia DOT edu
* Mohammadhosein Gholamrezaei - uab9qt AT virginia DOT edu
* Kevin Skadron - skadron AT virginia DOT edu
