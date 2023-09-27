timeStamp=$(echo -n $(date "+%Y-%m-%d %H:%M:%S") | shasum | cut -f 1 -d " ")

mubertDir=../../src/mubert
extractDir = ../../src/create_defect_dataset


mkdir -p data/defect/leam_mutants
mkdir -p ${mubertDir}/output
mkdir -p ${mubertDir}/output/mubert_jsonlines
mkdir -p ${mubertDir}/output/$timeStamp
mkdir -p ${mubertDir}/output/$timeStamp/results
mkdir -p ${mubertDir}/output/$timeStamp/logs
mkdir -p ${mubertDir}/output/$timeStamp/res

leam_data=data/defect/leam_mutants
outputDir=${mubertDir}/output/
mubert_jsonlines=${mubertDir}/output/mubert_jsonlines
finalDir=${mubertDir}/output/$timeStamp
results=${mubertDir}/output/$timeStamp/results
logDir=${mubertDir}/output/$timeStamp/logs
resDir=${mubertDir}/output/$timeStamp/res
call_mberta=${mubertDir}/call_mberta.sh
getprojects_inputs=${mubertDir}/generate_input.py
parse_mutants=${mubertDir}/parse_mutants.py
extract_mubert=${extractDir}/extract_mubert.py
# format_mutants=${mubertDir}/format_mutants.py

exec 3>&1 4>&2
trap $(exec 2>&4 1>&3) 0 1 2 3
exec 1>$logDir/$timeStamp.log 2>&1

echo Logs:$logDir
echo STARTING at $(date)
git rev-parse HEAD

parse_mutants(){
    python3 $parse_mutants $outputDir $timeStamp
}

extract_mubert(){
    python3 $extract_mubert $mubert_jsonlines $results
}


python3 $getprojects_inputs $finalDir $resDir

for info in $(cat ${finalDir}/${timeStamp}); 
do
    repo=$(echo $info | cut -d, -f1)
    targetclasses=$(echo $info | cut -d, -f2)
    mutants_dir=$(echo $info | cut -d, -f3)
    outputs_dir=$(echo $info | cut -d, -f4)
    short_name=$(echo $info | cut -d, -f5)
    echo work on: ${targetclasses} START at $(date) >> $logDir/${short_name}.log
    timeout 900s bash -x $call_mberta ${repo} ${targetclasses} ${mutants_dir} ${outputs_dir} >> $logDir/${short_name}.log
    echo work on: ${targetclasses} END at $(date) >> $logDir/${short_name}.log
done

parse_mutants()
extract_mubert()

echo ENDING at $(date)