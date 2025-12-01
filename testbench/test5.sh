#!/bin/bash
set +x
source common.sh
benchmark_name="mul_fp32"

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

bit_serial_isa="inv_nand"
num_reg=4
pim_mode="digital"
target="${bit_serial_isa}__${num_reg}__${pim_mode}__${benchmark_name}"
outdir="$SCRIPT_DIR/outputs__$target"
genlib_file="$GENLIB_DIR/${bit_serial_isa}.genlib"

# Call the bit-serial compiler
$PROJ_ROOT/apptainer-run.sh $PROJ_ROOT/bit_serial_compiler.py \
    --verilog "${verilog_files[@]}" \
    --to-stage pim \
    --genlib "$genlib_file" \
    --num-regs "$num_reg" \
    --output "$target" \
    --outdir "$outdir" \
    --num-tests 10 \
    --pim-mode "$pim_mode" \
    2>&1 | tee "$outdir/$target.log"
    