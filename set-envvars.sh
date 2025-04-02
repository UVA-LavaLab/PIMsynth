
ROOT=$(git rev-parse --show-toplevel)

export PIMEVAL_SIM_CONFIG=$ROOT/PIMeval-PIMbench/configs/PIMeval_BitSimdV.cfg
export LIB_PIMEVAL_PATH=$ROOT/PIMeval-PIMbench/libpimeval

echo "ROOT : $ROOT"
echo "PIMEVAL_SIM_CONFIG : $PIMEVAL_SIM_CONFIG"

