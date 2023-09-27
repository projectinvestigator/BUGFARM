repo=$1 
targetclass=$2
mutants_dir=$3
outputs_dir=$4 


# path to clone dependencies.
. def_dependencies.sh "$dependencies_dir"
activate_python_env
export_python_path

python3 mbertntcall/mbert_generate_mutants_runner.py \
-repo_path ${repo} \
-target_classes ${targetclass}  \
-mutated_classes_output_path ${mutants_dir} \
-output_dir ${outputs_dir} \
-java_home /usr/lib/jvm/java-1.8.0-openjdk-amd64/