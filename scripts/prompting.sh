# !/usr/bin/env bash

WORKDIR=`pwd`
export PYTHONPATH=$WORKDIR
export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/prompting.sh MODEL_NAME MODEL_SIZE";
    echo "MODEL_NAME is required [one of codebert, codet5, NatGen]";
    echo "MODEL_SIZE is required [base]";
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

if [[ $# < 2 ]]; then
  prompt;
fi

MODEL_NAME=$1;
MODEL_SIZE=$2;

projects=("commons-cli" "commons-codec" "commons-collections" "commons-compress" "commons-csv" "commons-jxpath" "commons-lang" "commons-math" "gson" "jackson-core" "jackson-databind" "jackson-dataformat-xml" "jfreechart" "joda-time" "jsoup");

for project in "${projects[@]}"
do
    python3 src/bug_generator/chatgpt.py --project_name $project --model_type $MODEL_NAME --model_size $MODEL_SIZE;
done
