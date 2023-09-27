timeStamp=$(echo -n $(date "+%Y-%m-%d %H:%M:%S") | shasum | cut -f 1 -d " ")

leamDir=../../src/leam
extractDir = ../../src/create_defect_dataset

mkdir -p ${leamDir}/mutants
mkdir -p ${leamDir}/jsonfiles
mkdir -p ${leamDir}/output
mkdir -p ${leamDir}/output/$timeStamp
mkdir -p ${leamDir}/output/$timeStamp/logs
mkdir -p ${leamDir}/output/$timeStamp/results

finalDir=${leamDir}/output/$timeStamp
logDir=${leamDir}/output/$timeStamp/logs
locations=${leamDir}/location2
generateInputs=${leamDir}/generate_input.py
getAllProjects=${leamDir}/combine_input_index.py
testDefect4jV1Fixed=${leamDir}/testDefect4jV1Fixed.py
mutants=${leamDir}/mutants
projects=${leamDir}/projects
result=${leamDir}/output/$timeStamp/results
jsonl_dir=${leamDir}/leam_jsonlfiles_temp
format_mutants=${leamDir}/format_mutants.py
parse_mutants=${leamDir}/parse_mutants.py
extract_all_mutants=${extractDir}/extract_leam.py

exec 3>&1 4>&2
trap $(exec 2>&4 1>&3) 0 1 2 3
exec 1>$logDir/$timeStamp.log 2>&1

echo Logs:$logDir
echo STARTING at $(date)
git rev-parse HEAD

# generate input files for leam, outputs saved in `location2``
genarate_input(){
    python3 $generateInputs $leamDir
}

# generate ${finalDir}/${timeStamp} for outputs
generate_output_dir(){
    python3 $getAllProjects $locations $finalDir $timeStamp 
}

# run leam
run_leam(){
    for info in $(cat ${finalDir}/${timeStamp}); 
    do
        idxInput=$(echo $info | cut -d, -f1)
        echo work on: $idxInput START at $(date)
        CUDA_VISIBLE_DEVICES=0,1 python3 $testDefect4jV1Fixed $idxInput > $logDir/${idxInput}.log # run LEAM
        echo work on: $idxInput END at $(date)
    done
}

# parse mutants
parse_mutants(){
    python3 $parse_mutants $mutants $jsonl_dir $timeStamp
}

# format parsable mutants
format_mutants(){
    python3 $format_mutants $jsonl_dir $result
}

# put mutants of all projects into one jsonl file
extract_all_mutants(){
    python3 $extract_all_mutants $result $result ${result}/all_leam_mutants.jsonl
}

genarate_input()
generate_output_dir()
run_leam()
parse_mutants()
format_mutants()
extract_all_mutants()


cp -r $mutants $finalDir
cp -r $jsonl_dir $finalDir

echo ENDING at $(date)