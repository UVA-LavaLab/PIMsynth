#!/bin/bash
#===============================================================================
# FILE: run_benchmark.sh
# DESCRIPTION: Script to run bit-serial benchmarks
# AUTHOR: Deyuan Guo <guodeyuan@gmail.com>
# CREATED: 03/28/2025
#===============================================================================

# NOTE: Use apptainer to run this script. Do not call apptainer in this script.

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
PROJ_ROOT=$(git rev-parse --show-toplevel)
SUBMODULE_DIR=$PROJ_ROOT/benchmarks
# Note: Copy this script to another directory and set VERILOG_DIR to ./ for testing
VERILOG_DIR=./

# Define a list of valid bit-serial ISA
VALID_BIT_SERIAL_ISA=(
    "inv_nand"
    "inv_maj_and"
    "inv_and_xnor_mux"
)

# Define a list of valid benchmark names
VALID_BENCHMARKS=(
    "mul_int2"
)

# Function to display valid bit-serial ISA
show_valid_bit_serial_isa() {
    echo "Valid bit-serial ISA: ${VALID_BIT_SERIAL_ISA[*]}"
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
    echo "Valid num_reg values: 2 - 19"
}

# Check if the provided num_reg value is valid
is_valid_num_reg() {
    if [[ "$1" =~ ^[2-9]$|^1[0-9]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to display valid benchmarks
show_valid_benchmarks() {
    echo "Valid benchmark names: ${VALID_BENCHMARKS[*]}"
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
genlib_file="$PROJ_ROOT/src/genlibs/${bit_serial_isa}.genlib"

# Check if the genlib file exists
if [ ! -f "$genlib_file" ]; then
    echo "Error: GenLib file '$genlib_file' not found."
    exit 1
fi

target="${bit_serial_isa}__${num_reg}__${benchmark_name}"
outdir="$SCRIPT_DIR/outputs__$target"

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

# Collect submodule verilog files
verilog_files=()
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    verilog_files+=("$SUBMODULE_DIR/$line")
done < "$SUBMODULE_DIR/submodule_list.txt"

# Add top-level benchmark file
verilog_files+=("$VERILOG_DIR/${benchmark_name}.v")

# Check if verilog files exist
for verilog_file in "${verilog_files[@]}"; do
    if [ ! -f "$verilog_file" ]; then
        echo "Error: Verilog file '$verilog_file' not found."
        exit 1
    fi
done

# Call the bit-serial compiler
$PROJ_ROOT/bit_serial_compiler.py \
    --verilog "${verilog_files[@]}" \
    --genlib "$genlib_file" \
    --num-regs "$num_reg" \
    --output "$target" \
    --outdir "$outdir" \
    --num-tests 10

# Make the test
cd "./outputs__$target"
make

# Run the test
./${target}.test.out
cd ..

