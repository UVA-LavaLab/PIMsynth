# PIMsynth top-level Makefile
# Builds third-party dependencies and submodules

NPROC := $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

.PHONY: all yosys abc llvm pimeval memir \
        clean-yosys clean-abc clean-llvm clean-pimeval clean-memir clean-all \
        help

help:
	@echo "PIMsynth build targets:"
	@echo "  make all          - Build everything"
	@echo "  make yosys        - Build Yosys logic synthesizer"
	@echo "  make abc          - Build ABC logic synthesizer"
	@echo "  make llvm         - Build LLVM/clang for RISC-V"
	@echo "  make pimeval      - Build PIMeval simulator"
	@echo "  make memir        - Build memir scheduler (requires OR-Tools + Cargo)"
	@echo ""
	@echo "  make clean-all    - Clean everything"
	@echo "  make clean-yosys  - Clean Yosys build"
	@echo "  make clean-abc    - Clean ABC build"
	@echo "  make clean-llvm   - Clean LLVM build"
	@echo "  make clean-pimeval- Clean PIMeval build"
	@echo "  make clean-memir  - Clean memir build"

all: yosys abc llvm pimeval memir

yosys:
	cd yosys && $(MAKE) -j$(NPROC)

abc:
	cd abc && $(MAKE) -j$(NPROC)

llvm:
	mkdir -p llvm-build
	cd llvm-build && cmake ../llvm-project/llvm \
		-DCMAKE_BUILD_TYPE=Release \
		-DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" \
		-G "Unix Makefiles" \
		&& $(MAKE) -j$(NPROC)

pimeval:
	cd PIMeval-PIMbench && $(MAKE) -j$(NPROC)

memir:
	cd src/schedulers/memir && $(MAKE)

clean-yosys:
	cd yosys && $(MAKE) clean

clean-abc:
	cd abc && $(MAKE) clean

clean-llvm:
	rm -rf llvm-build

clean-pimeval:
	cd PIMeval-PIMbench && $(MAKE) clean

clean-memir:
	cd src/schedulers/memir && $(MAKE) clean

clean-all: clean-yosys clean-abc clean-llvm clean-pimeval clean-memir
