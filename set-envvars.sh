
ROOT=$(git rev-parse --show-toplevel)

export PIMEVAL_CONFIG_PATH=$ROOT/PIMeval-PIMbench/configs
export PIMEVAL_CONFIG_SIM=PIMeval_BitSimdV.cfg
export LIB_PIMEVAL_PATH=$ROOT/PIMeval-PIMbench/libpimeval

echo "ROOT : $ROOT"
echo "PIMEVAL_CONFIG_PATH : $PIMEVAL_CONFIG_PATH"
echo "PIMEVAL_CONFIG_PATH : $PIMEVAL_CONFIG_SIM"

