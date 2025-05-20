
ROOT=$(git rev-parse --show-toplevel)

# If $1 is not provided, default to 0; otherwise, use $1 as num bank
NUM_BANK=${1:-0}
if [ "$NUM_BANK" -eq 0 ]; then
    export PIMEVAL_SIM_CONFIG=$ROOT/PIMeval-PIMbench/configs/taco/PIMeval_BitSerial_Rank1.cfg
else
    unset PIMEVAL_SIM_CONFIG
    export PIMEVAL_SIM_TARGET=PIM_DEVICE_BITSIMD_V_AP
    export PIMEVAL_NUM_RANKS=1
    export PIMEVAL_NUM_BANK_PER_RANK=$NUM_BANK
    export PIMEVAL_NUM_SUBARRAY_PER_BANK=16
    export PIMEVAL_NUM_ROW_PER_SUBARRAY=65536
    export PIMEVAL_NUM_COL_PER_SUBARRAY=8192
fi

export LIB_PIMEVAL_PATH=$ROOT/PIMeval-PIMbench/libpimeval

echo "ROOT : $ROOT"
echo "PIMEVAL_SIM_CONFIG : $PIMEVAL_SIM_CONFIG"

