#!/bin/bash
#===============================================================================
# FILE: run_regressions.sh
# DESCRIPTION: Batch runner for PIMsynth compiler tasks.
#   Takes a task list file as input. Each line: isa num_regs mode benchmark
#   Outputs go to testbench/outputs/<isa>__<regs>__<mode>__<benchmark>/
#   Prints summary table at the end for the tasks just run.
# AUTHOR: Deyuan Guo <guodeyuan@gmail.com>
#===============================================================================

set -euo pipefail

TESTBENCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(cd "$TESTBENCH_DIR/.." && pwd)"

source "$TESTBENCH_DIR/common.sh"

OUTPUT_ROOT="$TESTBENCH_DIR/outputs"
COLLECTOR="$TESTBENCH_DIR/collect_results.py"

# --- Parse arguments ---
COMPILE_ONLY=false
CONTINUE_MODE=false
TASK_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --compile-only)
            COMPILE_ONLY=true
            shift
            ;;
        --continue)
            CONTINUE_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 <task_list_file> [--compile-only] [--continue]"
            echo ""
            echo "  <task_list_file>  File with one task per line: isa num_regs mode benchmark"
            echo "  --compile-only    Skip make + test execution (compile and collect stats only)"
            echo "  --continue        Resume from previous run (skip completed tasks)"
            echo ""
            echo "Examples:"
            echo "  $0 tasks_regression.txt"
            echo "  $0 tasks_quick.txt --compile-only"
            echo "  $0 tasks_regression.txt --continue"
            exit 0
            ;;
        -*)
            echo "Error: Unknown option '$1'"
            exit 1
            ;;
        *)
            if [ -z "$TASK_FILE" ]; then
                TASK_FILE="$1"
            else
                echo "Error: Unexpected argument '$1'"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$TASK_FILE" ]; then
    echo "Error: No task list file specified."
    echo "Usage: $0 <task_list_file> [--compile-only] [--continue]"
    exit 1
fi

if [ ! -f "$TASK_FILE" ]; then
    echo "Error: Task list file '$TASK_FILE' not found."
    exit 1
fi

# --- Read task list ---
TASKS=()
while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [ -z "$line" ] && continue
    TASKS+=("$line")
done < "$TASK_FILE"

NUM_TASKS=${#TASKS[@]}
if [ "$NUM_TASKS" -eq 0 ]; then
    echo "Error: No tasks found in '$TASK_FILE'."
    exit 1
fi

echo "==============================================================================="
echo "PIMsynth Batch Runner"
echo "Task file:    $TASK_FILE"
echo "Tasks:        $NUM_TASKS"
echo "Compile only: $COMPILE_ONLY"
echo "Continue:     $CONTINUE_MODE"
echo "Output root:  $OUTPUT_ROOT"
echo "==============================================================================="

mkdir -p "$OUTPUT_ROOT"

# --- Collect submodule verilog files ---
submodule_files=()
while IFS= read -r line || [ -n "$line" ]; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    submodule_files+=("$SUBMODULE_DIR/$line")
done < "$SUBMODULE_LIST"

for vf in "${submodule_files[@]}"; do
    if [ ! -f "$vf" ]; then
        echo "Error: Verilog submodule file '$vf' not found."
        exit 1
    fi
done

# --- Run each task ---
PASSED=0
FAILED=0
SKIPPED=0
TASK_IDX=0
COMPLETED_TARGETS=()

for task in "${TASKS[@]}"; do
    TASK_IDX=$((TASK_IDX + 1))
    read -r isa num_reg pim_mode benchmark <<< "$task"
    target="${isa}__${num_reg}__${pim_mode}__${benchmark}"
    outdir="$OUTPUT_ROOT/$target"
    logfile="$outdir/$target.log"

    echo ""
    echo "[$TASK_IDX/$NUM_TASKS] $target"

    # --continue: skip if log already exists and contains stats
    if $CONTINUE_MODE && [ -f "$logfile" ]; then
        if grep -q "Info:  #R" "$logfile" 2>/dev/null; then
            echo "  Skipping (already completed)"
            SKIPPED=$((SKIPPED + 1))
            COMPLETED_TARGETS+=("$target")
            continue
        fi
    fi

    # Clean output directory
    rm -rf "$outdir"
    mkdir -p "$outdir"

    # Locate top-level verilog file
    verilog_top=""
    if [ -f "$VERILOG_DIR2/${benchmark}.v" ]; then
        verilog_top="$VERILOG_DIR2/${benchmark}.v"
    elif [ -f "$VERILOG_DIR3/${benchmark}.v" ]; then
        verilog_top="$VERILOG_DIR3/${benchmark}.v"
    else
        echo "  ERROR: Verilog file '${benchmark}.v' not found."
        FAILED=$((FAILED + 1))
        COMPLETED_TARGETS+=("$target")
        continue
    fi

    # Build verilog file list
    verilog_files=("${submodule_files[@]}" "$verilog_top")

    # Map ISA to genlib
    genlib_file="$GENLIB_DIR/${isa}.genlib"
    if [ ! -f "$genlib_file" ]; then
        echo "  ERROR: GenLib file '$genlib_file' not found."
        FAILED=$((FAILED + 1))
        COMPLETED_TARGETS+=("$target")
        continue
    fi

    # --- Compile ---
    echo "  Compiling..."
    if ! $PROJ_ROOT/bit_serial_compiler.py \
        --verilog "${verilog_files[@]}" \
        --genlib "$genlib_file" \
        --num-regs "$num_reg" \
        --output "$target" \
        --outdir "$outdir" \
        --num-tests 10 \
        --pim-mode "$pim_mode" \
        > "$logfile" 2>&1; then
        echo "  ERROR: Compilation failed."
        FAILED=$((FAILED + 1))
        COMPLETED_TARGETS+=("$target")
        continue
    fi

    if $COMPILE_ONLY; then
        echo "  Compiled (skipping build+test)."
        PASSED=$((PASSED + 1))
        COMPLETED_TARGETS+=("$target")
        continue
    fi

    # --- Build tests ---
    echo "  Building tests..."
    if ! make -C "$outdir" >> "$logfile" 2>&1; then
        echo "  ERROR: Build failed."
        FAILED=$((FAILED + 1))
        COMPLETED_TARGETS+=("$target")
        continue
    fi

    # --- Run tests ---
    echo "  Running tests..."
    task_passed=true

    if [ -f "$outdir/${target}.test.out" ]; then
        "$outdir/${target}.test.out" >> "$logfile" 2>&1 || true
    fi
    if [ -f "$outdir/${target}.test_bitwise.out" ]; then
        "$outdir/${target}.test_bitwise.out" >> "$logfile" 2>&1 || true
    fi

    if grep -q "PIM test: SOME FAILED" "$logfile" 2>/dev/null; then
        task_passed=false
    fi
    if grep -q "Bitwise test: NOT OK" "$logfile" 2>/dev/null; then
        task_passed=false
    fi

    if $task_passed; then
        echo "  PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "  FAILED (test failure)"
        FAILED=$((FAILED + 1))
    fi
    COMPLETED_TARGETS+=("$target")
done

echo ""
echo "==============================================================================="
echo "Run complete: $PASSED passed, $FAILED failed, $SKIPPED skipped (of $NUM_TASKS)"
echo "==============================================================================="

# --- Print summary table for tasks just run ---
if [ -f "$COLLECTOR" ] && [ ${#COMPLETED_TARGETS[@]} -gt 0 ]; then
    TARGET_ARGS=()
    for t in "${COMPLETED_TARGETS[@]}"; do
        TARGET_ARGS+=("$t")
    done
    python3 "$COLLECTOR" "$OUTPUT_ROOT" "${TARGET_ARGS[@]}"
fi
