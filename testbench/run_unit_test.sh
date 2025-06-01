#!/bin/bash
#===============================================================================
# FILE: run_unit_test.sh
# DESCRIPTION: Script to run unit tests
# AUTHOR: Deyuan Guo <guodeyuan@gmail.com>
# AUTHOR: Mohammadhosein Gholamrezaei <uab9qt@virginia.edu>
# CREATED: 05/31/2025
#===============================================================================

# NOTE: Use apptainer to run this script. Do not call apptainer in this script.

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
PROJ_ROOT=$(git rev-parse --show-toplevel)
GOLDEN_MODELS_DIR="golden-model"

# Note: This script finds verilog inputs from below locations
VERILOG_DIR1=.
VERILOG_DIR2=$PROJ_ROOT/src-verilog/benchmarks
VERILOG_DIR3=$PROJ_ROOT/src-verilog/misc
GENLIB_DIR=$PROJ_ROOT/src-genlib
SUBMODULE_LIST=$PROJ_ROOT/src-verilog/submodule_list.txt
SUBMODULE_DIR=$PROJ_ROOT/src-verilog/submodules

# Define a list of valid bit-serial ISA
VALID_BIT_SERIAL_ISA=(
    "inv_nand"
    "inv_maj_and"
    "inv_maj_and_or"
    "inv_and_xnor_mux"
    "inv_and_xor"
)

# Define a list of valid benchmark names
VALID_BENCHMARKS=(
  "aes_sbox"
)

# Define a list of valid PIM modes
VALID_PIM_MODES=(
    "digital" "analog"
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
    # allow untracked bit-serial ISA
    echo "Warning: Bit-serial ISA $1 is experimental."
    return 0
}

# Function to display valid num_reg values
show_valid_num_reg() {
    echo "Valid num_reg values: 2 - 14"
}

# Check if the provided num_reg value is valid
is_valid_num_reg() {
    if [[ "$1" =~ ^[2-9]$|^1[0-4]$ ]]; then
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
    # allow untracked verilog
    echo "Warning: Input verilog $1 is experimental."
    return 0
}

# Function to display valid PIM modes
show_valid_pim_modes() {
    echo "Valid PIM modes: ${VALID_PIM_MODES[*]}"
}

# Check if the provided PIM mode is valid
is_valid_pim_mode() {
    for benchmark in "${VALID_PIM_MODES[@]}"; do
        if [ "$1" == "$pim_mode" ]; then
            return 0
        fi
    done
    return 1
}

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <bit_serial_isa> <num_reg> <digital|analog> <benchmark_name>"
    show_valid_bit_serial_isa
    show_valid_num_reg
    show_valid_pim_modes
    show_valid_benchmarks
    exit 0
fi

bit_serial_isa="$1"
num_reg="$2"
pim_mode="$3"
benchmark_name="$4"

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

if ! is_valid_pim_mode $pim_mode; then
    echo "Error: Invalid pim mode '$pim_mode'."
    show_valid_pim_modes
    exit 1
fi

if ! is_valid_benchmark $benchmark_name; then
    echo "Error: Invalid benchmark name '$benchmark_name'."
    show_valid_benchmarks
    exit 1
fi

# Map the bit-serial ISA name to genlib file
genlib_file="$GENLIB_DIR/${bit_serial_isa}.genlib"

# Check if the genlib file exists
if [ ! -f "$genlib_file" ]; then
    echo "Error: GenLib file '$genlib_file' not found."
    exit 1
fi

target="${bit_serial_isa}__${num_reg}__${pim_mode}__${benchmark_name}"
golden_function_header_file="$SCRIPT_DIR/$GOLDEN_MODELS_DIR/${benchmark_name}_golden.hpp"
outdir="$SCRIPT_DIR/outputs__$target"

# Check if the golden model headr file exitst
if [ ! -f "$golden_function_header_file" ]; then
    echo "Error: Header file '$golden_function_header_file' not found."
    exit 1
fi

# Delete the output directory if it already exists
if [ -d "$outdir" ]; then
read -p "The directory '$outdir' already exists. Do you want to delete it and continue? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Aborting."
    exit 1
fi
    rm -rfv "$outdir"
fi

# Create the output directory
mkdir -p "$outdir"

echo "==========================="
echo "Bit-Serial PIM Benchmark"
echo "GenLib File: $genlib_file"
echo "NumReg: $num_reg"
echo "PIM Mode: $pim_mode"
echo "Benchmark Name: $benchmark_name"
echo "Output Directory: $outdir"
echo "==========================="

# Collect submodule verilog files from submodule_list.txt
verilog_files=()
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    verilog_files+=("$SUBMODULE_DIR/$line")
done < "$SUBMODULE_LIST"

# Check if verilog submodule files exist
for verilog_file in "${verilog_files[@]}"; do
    if [ ! -f "$verilog_file" ]; then
        echo "Error: Verilog submodule file '$verilog_file' not found."
        exit 1
    fi
done

# Add top-level benchmark file
if [ -f "$VERILOG_DIR1/${benchmark_name}.v" ]; then
    verilog_files+=("$VERILOG_DIR1/${benchmark_name}.v")
elif [ -f "$VERILOG_DIR2/${benchmark_name}.v" ]; then
    verilog_files+=("$VERILOG_DIR2/${benchmark_name}.v")
elif [ -f "$VERILOG_DIR3/${benchmark_name}.v" ]; then
    verilog_files+=("$VERILOG_DIR3/${benchmark_name}.v")
else
    echo "Error: Top-level Verilog file '$benchmark_name.v' not found in any of the expected directories."
    exit 1
fi

# Copy the golden function header file to the output directory
local_golden_function_header_file="$outdir/$target.golden.hpp"
cp $golden_function_header_file $local_golden_function_header_file

# Call the bit-serial compiler
$PROJ_ROOT/bit_serial_compiler.py \
    --verilog "${verilog_files[@]}" \
    --genlib "$genlib_file" \
    --num-regs "$num_reg" \
    --output "$target" \
    --outdir "$outdir" \
    --num-tests 10 \
    --pim-mode "$pim_mode" \
    --golden-function-name "$local_golden_function_header_file" \
    2>&1 | tee "$outdir/$target.log"

# Make the test
cd $outdir
make

# Run the test
./${target}.test.out 2>&1 | tee -a "$outdir/$target.log"
./${target}.test_bitwise.out 2>&1 | tee -a "$outdir/$target.log"
cd ..

# Final outputs for debugging
{
    echo "################################################################################"
    echo "SUMMARY"
    echo "Output Directory:         $outdir"
    echo "Output Directory Name:    outputs__$target"
    grep "Info:  #R" "$outdir/$target.log"
    grep -E '\b(row_r|row_w|rreg\..*) :' "$outdir/$target.log"
    grep -E '\b(row_ap@.*|row_aap@.*) :' "$outdir/$target.log"
    grep "Num Read, Write, Logic" "$outdir/$target.log"
    grep "PIM test: " "$outdir/$target.log"
    grep "Bitwise test: " "$outdir/$target.log"
    echo "################################################################################"
} 2>&1 | tee -a "$outdir/$target.summary.log"

