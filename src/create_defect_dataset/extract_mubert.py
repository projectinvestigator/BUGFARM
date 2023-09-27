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

file_paths = []

def get_files(dir,saveTo):
    if not saveTo.endswith(".jsonl"):
        if not os.path.exists(saveTo):
            os.mkdir(saveTo)
    for dirpath, _, files in os.walk(dir):
        for file in files:
            if file.startswith("parsed_") and file.endswith("jsonl"):
                file_path = os.path.join(dirpath,file)
                for project in projects:
                    if project in file:
                        file_paths.append(file_path)

    data = []
    final = []

    for file_path in file_paths:
        with open(file_path, "r") as jl:
            id = 0
            for each in [loads(each_line) for each_line in jl]:
                if "mutated_method" in each:
                    data.append(each)

                    mutant = {
                        "project":each["project"],
                        "file_path": each["file_path"],
                        "func" :each["mutated_method"],
                        "target": 1, # latest: mutant = 0
                        "idx": "idx",
                        "start": each["start"]
                    }
                    final.append(mutant)

                    method = {
                        "project":each["project"],
                        "file_path": each["file_path"],
                        "func" :each["original_method"],
                        "target": 0, # latest: method = 0
                        "idx": "idx",
                        "start": each["start"]
                    }
                    if method not in final:
                        final.append(method)

    print(len(final))


    if not saveTo.endswith(".jsonl"):
        jlfile_path = os.path.join(saveTo,"all_mubert_mutants.jsonl")
    else: 
        jlfile_path = saveTo
    jlfile = open(jlfile_path,"w")
    jlfile.close()
    
    idx = 0
    with jsonlines.open(jlfile_path,"a") as jlf:
        for each in final:
            each["idx"] = idx
            idx += 1
            jlf.write_all([each])

def extract(mutant_dir,saveTo):
    get_files(mutant_dir,saveTo)

if __name__ == "__main__":
    # args = sys.argv[1:]
    # mutant_dir = args[0]
    # saveTo_dir = args[1]

    mutant_dir = "data/defect/regminer_mutants"
    saveTo_dir = "data/defect/regminer_mutants"
    # args: mutants_dir, output_dir; here config output_dir same as input_dir
    get_files(mutant_dir,saveTo_dir)
