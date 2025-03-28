#!/bin/bash
#===============================================================================
# FILE: run_benchmark.sh
# DESCRIPTION: Script to run bit-serial benchmarks
# AUTHOR: Deyuan Guo <guodeyuan@gmail.com>
# CREATED: 03/28/2025
#===============================================================================

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
PROJ_ROOT="$(realpath "$SCRIPT_DIR/..")"

# Define a list of valid bit-serial ISA
VALID_BIT_SERIAL_ISA=(
    "inv_nand"
    "inv_maj_and"
    "inv_and_xnor_mux"
)

# Define a list of valid benchmark names
VALID_BENCHMARKS=(
    "add_int8"
    "add_int16"
    "add_int32"
    "add_int64"
    "sub_int8"
    "sub_int16"
    "sub_int32"
    "sub_int64"
    "mul_int8"
    "mul_int16"
    "mul_int32"
    "mul_int64"
    "popcount_int32"
)

# Function to display valid bit-serial ISA
show_valid_bit_serial_isa() {
    echo "Valid bit-serial ISA are:"
    for isa in "${VALID_BIT_SERIAL_ISA[@]}"; do
        echo "  - $isa"
    done
}

# Check if the provided bit-serial ISA name is valid
is_valid_bit_serial_isa() {
    for isa in "${VALID_BIT_SERIAL_ISA[@]}"; do
        if [ "$1" == "$isa" ]; then
            return 0
        fi
    done
    return 1
}

# Function to display valid num_reg values
show_valid_num_reg() {
    echo "Valid num_reg values are: 2, 3, 4, 5, 6, 7"
}

# Check if the provided num_reg value is valid
is_valid_num_reg() {
    if [[ "$1" =~ ^[2-7]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to display valid benchmarks
show_valid_benchmarks() {
    echo "Valid benchmarks are:"
    for benchmark in "${VALID_BENCHMARKS[@]}"; do
        echo "  - $benchmark"
    done
}

# Check if the provided benchmark name is valid
is_valid_benchmark() {
    for benchmark in "${VALID_BENCHMARKS[@]}"; do
        if [ "$1" == "$benchmark" ]; then
            return 0
        fi
    done
    return 1
}

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <bit_serial_isa> <num_reg> <benchmark_name>"
    show_valid_bit_serial_isa
    show_valid_num_reg
    show_valid_benchmarks
    exit 0
fi

bit_serial_isa="$1"
num_reg="$2"
benchmark_name="$3"

if ! is_valid_bit_serial_isa $bit_serial_isa; then
    echo "Error: Invalid bit-serial ISA name '$bit_serial_isa'."
    show_valid_bit_serial_isa
    exit 1
fi

if ! is_valid_num_reg $num_reg; then
    echo "Error: Invalid num_reg value '$num_reg'."
    show_valid_num_reg
    exit 1
fi

if ! is_valid_benchmark $benchmark_name; then
    echo "Error: Invalid benchmark name '$benchmark_name'."
    show_valid_benchmarks
    exit 1
fi

# Map the bit-serial ISA name to genlib file
genlib_file=""
case "$bit_serial_isa" in
    "inv_nand")
        genlib_file="$PROJ_ROOT/src/genlibs/inv_nand.genlib"
        ;;
    "inv_maj_and")
        genlib_file="$PROJ_ROOT/src/genlibs/inv_maj_and.genlib"
        ;;
    "inv_and_xnor_mux")
        genlib_file="$PROJ_ROOT/src/genlibs/inv_and_xnor_mux.genlib"
        ;;
    *)
        echo "Unsupported bit-serial ISA name: $bit_serial_isa"
        exit 1
        ;;
esac

# Check if the genlib file exists
if [ ! -f "$genlib_file" ]; then
    echo "Error: GenLib file '$genlib_file' not found."
    exit 1
fi

outdir="$SCRIPT_DIR/outputs__${bit_serial_isa}__${num_reg}__${benchmark_name}"

# Delete the output directory if it already exists
if [ -d "$outdir" ]; then
read -p "The directory '$outdir' already exists. Do you want to delete it and continue? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Aborting."
    exit 1
fi
    rm -rfv "$outdir"
fi

echo "==========================="
echo "Bit-Serial PIM Benchmark"
echo "GenLib File: $genlib_file"
echo "NumReg: $num_reg"
echo "Benchmark Name: $benchmark_name"
echo "Output Directory: $outdir"
echo "==========================="

case "$benchmark_name" in
    "add_int8")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/add_int8.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "add_int16")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/add_int16.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "add_int32")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/add_int32.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "add_int64")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/add_int64.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "sub_int8")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/sub_int8.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_1bit.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "sub_int16")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/sub_int16.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_1bit.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "sub_int32")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/sub_int32.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_1bit.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "sub_int64")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/sub_int64.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_1bit.v" \
                      "$PROJ_ROOT/benchmarks/subtractor_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "mul_int8")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/mul_int8.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "mul_int16")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/mul_int16.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "mul_int32")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/mul_int32.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "mul_int64")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/mul_int64.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    "popcount_int32")
        $PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
            --verilog "$PROJ_ROOT/benchmarks/popcount_int32.v" \
                      "$PROJ_ROOT/benchmarks/adder_1bit.v" \
                      "$PROJ_ROOT/benchmarks/adder_nbit.v" \
            --genlib "$genlib_file" \
            --num-regs "$num_reg" \
            --outdir "$outdir"
        ;;
    *)
        echo "Unsupported benchmark name: $benchmark_name"
        exit 1
        ;;
esac
