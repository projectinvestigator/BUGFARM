import json
import jsonlines
from json import loads
import os
import sys

projects = [
    "commons-cli","commons-collections","commons-csv",
    "commons-lang","gson","jackson-databind",
    "jfreechart","jsoup","commons-codec",
    "commons-compress","commons-jxpath","commons-math",
    "jackson-core","jackson-dataformat-xml","joda-time"
]

def get_files(dir,saveTo):
    file_sets = {}

    if not os.path.exists(saveTo):
        os.mkdir(saveTo)

    for dirpath, _, files in os.walk(dir):
        for file in files:
            if file.endswith("_all.jsonl"):
                file_path = os.path.join(dirpath,file)
                project_name = dirpath.split("/")[-1]
                for project in projects:
                    if project in file and project_name == project:
                        if project not in file_sets:
                            file_sets[project] = []
                        file_sets[project].append(file_path)
    
    generate_files(file_sets,saveTo)


def generate_files(file_sets,saveTo):
    all_final = []
    for project in file_sets:
        final = []
        data = []
        for file_path in file_sets[project]:
            with open(file_path, "r") as jl:
                for each in [loads(each_line) for each_line in jl]:
                    data.append(each)
                    all_final.append(each)
        
        save_path = os.path.join(saveTo,project + "_final_all.jsonl")
        jlfile = open(save_path,"w")
        jlfile.close()

        idx = 0
        for line in data:
            line["idx"] = idx
            idx += 1
            final.append(line)

        with jsonlines.open(save_path,"a") as jlf:
            for each in final:
                jlf.write_all([each])

        print(save_path,len(final))
    
    save_all_file = open(jsonline_file,"w")
    save_all_file.close()
    id = 0
    with jsonlines.open(save_all_path,"a") as jlfa:
            for each in all_final:
                each["idx"] = id
                id += 1
                jlfa.write_all([each])
    print(save_all_path,len(all_final))

def extract(input_jsons_dir,saveto_dir,jsonline_file):
    get_files(input_jsons_dir,saveto_dir,jsonline_file)

if __name__ == "__main__":
    # args = sys.argv[1:]
    # input_jsons_dir = args[0]
    # saveto_dir = args[1]
    # jsonline_file = args[2]

    # args: mutants_input_dir, output_dir, json_file; here config output_dir same as input_dir
    input_jsons_dir = "data/defect/leam_mutants"
    saveto_dir = "data/defect/leam_mutants"
    jsonline_file = "data/defect/all_leam_mutants.jaonl"
    get_files(input_jsons_dir,saveto_dir,jsonline_file)