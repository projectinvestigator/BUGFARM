# !/usr/bin/env bash

WORKDIR=`pwd`
export PYTHONPATH=$WORKDIR
export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/parse_response.sh LOG_FILE_NAME MODEL_NAME MODEL_SIZE NUM_WORKERS";
    echo "LOG_FILE_NAME is required";
    echo "MODEL_NAME is required [one of codebert, codet5, NatGen]";
    echo "MODEL_SIZE is required [base]";
    echo "THRESHOLD is required";
    echo "NUM_WORKERS is required";    
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

if [[ $# < 4 ]]; then
  prompt;
fi

LOG_FILE_NAME=$1;
MODEL_NAME=$2;
MODEL_SIZE=$3;
NUM_WORKERS=$4;

projects=("commons-cli" "commons-codec" "commons-collections" "commons-compress" "commons-csv" "commons-jxpath" "commons-lang" "commons-math" "gson" "jackson-core" "jackson-databind" "jackson-dataformat-xml" "jfreechart" "joda-time" "jsoup");

for project in "${projects[@]}"
do
    python3 src/bug_generator/parse_chatgpt.py --project_name $project --model_type $MODEL_NAME --model_size $MODEL_SIZE --log_file $LOG_FILE_NAME --num_workers $NUM_WORKERS;
done
