#!/usr/bin/env bash

# --- SCRIPT SETUP -------------------------------------------------------------

shout() {
    echo ""
    echo "----------------------------------------"
    echo "$1"
    echo "----------------------------------------"
    echo ""
}

# Exit if any command fails.
set -e

exit_trap() {
    # Print an error if the last command failed
    # (in which case the script is exiting because of set -e).
    [[ $? == 0 ]] && return
    shout "EARLY EXIT: SCRIPT FAILED"

    # Kill (send SIGTERM) to the whole process group, also killing
    # any background processes.
    # I think the trap command resets SIGTERM before resending it to the whole
    # group. (cf. https://stackoverflow.com/a/2173421)
    trap - SIGTERM && kill -- -$$
}
trap "exit_trap" SIGINT SIGTERM EXIT



# --- CHALLENGE SETUP ----------------------------------------------------------

workdir=$(cd $(dirname $0);cd ..; pwd)
echo workdir:"$workdir"

# AI model (7B-LLaMA model)
PROGRAM_PATH="./mlgo/ml_mips/ml_mips.bin"
MODEL_NAME="LLAMA"
MODEL_PATH="$workdir/mlgo/examples/llama/models/llama-7b-fp32.bin"
PROMPT="How to combine AI and blockchain?"
# MODEL_NAME="MNIST"
# MODEL_PATH="$workdir/mlgo/examples/mnist/models/mnist/ggml-model-small-f32.bin"
# DATA_PATH="./mlgo/examples/mnist/models/mnist/input_7"

export BASEDIR=/tmp/cannon_stats_llama

export PROGRAM_PATH=$PROGRAM_PATH
export MODEL_NAME=$MODEL_NAME
export MODEL_PATH=$MODEL_PATH
# export PROMPT=$PROMPT
export DATA_PATH=$DATA_PATH

# challenge ID, read by respond.js and assert.js
export ID=0

# clear data from previous runs
# rm -rf /tmp/cannon/* /tmp/cannon_fault/*
# mkdir -p /tmp/cannon/data
# mkdir -p /tmp/cannon/checkpoint
# mkdir -p /tmp/cannon_fault/data
# mkdir -p /tmp/cannon_fault/checkpoint
rm -rf $BASEDIR/*
mkdir -p $BASEDIR/data
mkdir -p $BASEDIR/checkpoint

# stored in /tmp/cannon/golden.json
# shout "GENERATING INITIAL MEMORY STATE CHECKPOINT"
# mlvm/mlvm --basedir=/tmp/cannon --program="$PROGRAM_PATH" --modelName="$MODEL_NAME" --model="$MODEL_PATH" --prompt="$PROMPT" --target=0 --nodeID 0

export LOGDIR=logs/stats/$(TZ="Asia/Shanghai" date -Imin)
rm -rf $LOGDIR/$MODEL_NAME
mkdir -p $LOGDIR/$MODEL_NAME

shout "GENERATING INIT DATA FILE"

# mlvm/mlvm --outputBenchmark --outputMode=2 --basedir=$BASEDIR --program="$PROGRAM_PATH" --modelName="$MODEL_NAME" --model="$MODEL_PATH" --prompt="$PROMPT" --target=0 --nodeID 0
/usr/bin/time -v mlvm/mlvm --outputBenchmark --outputMode=2 --basedir=$BASEDIR --program="$PROGRAM_PATH" --modelName="$MODEL_NAME" --model="$MODEL_PATH" --prompt="$PROMPT" --target=0 --nodeID 0 2>&1 | tee -a $LOGDIR/$MODEL_NAME/node_0.log

shout "CALCULATING MIPS STEPS OF EACH TENSOR NODE"

node scripts_layered/stats.js
