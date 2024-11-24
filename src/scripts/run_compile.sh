#!/bin/bash
# Helper script to run bit-serial compiler on one testcase
# deyuan, 11/23/2024

echo "== Run Bit-Serial Compiler =="

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <verilog-name> <genlib-name> <num-reg>"
    echo "Argument verilog-name: A verilog filename under src/verilog without .v suffix"
    echo "Argument genlib-name: A genlib filename under src/genlibs without .genlib suffix"
    echo "Argument num-reg: An integer"
    exit 1
fi

ROOT=$(git rev-parse --show-toplevel)
EXEC="$ROOT/apptainer-run.sh $ROOT/bit_serial_compiler.py"
VERILOG_NAME=$1
VERILOG_FILE=$ROOT/src/verilog/$1.v
GENLIB_NAME=$2
GENLIB_FILE=$ROOT/src/genlibs/$2.genlib
NUM_REG=$3
OUT_NAME=$VERILOG_NAME.$GENLIB_NAME.$NUM_REG-reg
OUT_DIR=./outputs
OUT_FILE=$OUT_DIR/$OUT_NAME.log

echo "== ROOT: $ROOT"
echo "== EXEC: $COMPILER"
echo "== VERILOG_NAME: $VERILOG_NAME"
echo "== VERILOG_FILE: $VERILOG_FILE"
echo "== GENLIB_NAME: $GENLIB_NAME"
echo "== GENLIB_FILE: $GENLIB_FILE"
echo "== NUM_REG: $NUM_REG"
echo "== OUT_NAME: $OUT_NAME"
echo "== OUT_DIR: $OUT_DIR"
echo "== OUT_FILE: $OUT_FILE"

mkdir -p $OUT_DIR

if [ ! -d "$OUT_DIR" ]; then
    echo "Error: Output directory '$OUT_DIR' does not exist."
    exit 1
fi
if [ ! -e "$VERILOG_FILE" ]; then
    echo "Error: Verilog file '$VERILOG_FILE' does not exist."
    exit 1
fi
if [ ! -e "$GENLIB_FILE" ]; then
    echo "Error: GenLib file '$GENLIB_FILE' does not exist."
    exit 1
fi

$EXEC \
    --verilog $VERILOG_FILE \
    --genlib $GENLIB_FILE \
    --num-regs $NUM_REG \
    --outdir $OUT_DIR \
    --output $OUT_NAME \
    > $OUT_FILE

echo "== Result: `grep '#R' $OUT_FILE`"

