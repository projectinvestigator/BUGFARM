import json
import jsonlines
import os
import sys
import utils
from json import loads
from typing import Set, Tuple
from pathlib import Path

projects = [
    "commons-cli","commons-collections","commons-csv",
    "commons-lang","gson","jackson-databind",
    "jfreechart","jsoup","commons-codec",
    "commons-compress","commons-jxpath","commons-math",
    "jackson-core","jackson-dataformat-xml","joda-time"
]

def get_files(dir,saveTo):
    if not os.path.exists(saveTo):
        os.mkdir(saveTo)
    for dirpath, _, files in os.walk(dir):
        for file in files:
            if "_final_mutants" in file and file.endswith(".jsonl"):
                file_path = os.path.join(dirpath,file)
                tag = dirpath.split("/")[-1]
                for project in projects:
                    if project in file:
                        read_file(file_path,project,tag,saveTo)


def read_file(file_path,project,tag,saveTo):
    data = []
    final = []
    with open(file_path, "r") as jl:
        for [each] in [loads(each_line) for each_line in jl]:
            data.append(each)
            mutant_func = each["mutated_method"]
            original_func = each["original_method"]
            
            mutant = {
                "project": project,
                "idx": "idx",
                "target": 0, # latest: mutant = 0
                "func": mutant_func,
                "filename":each["filename"]
            }

            method = {
                "project": project,
                "idx": "idx",
                "target": 1, # latest: method = 1
                "func": original_func,
                "filename": each["filename"]
            }

            final.append(mutant)
            if method not in final:
                final.append(method)

    saveDir_root = os.path.join(saveTo,project)
    if not os.path.exists(saveDir_root):
        os.mkdir(saveDir_root)
    
    jlfile_path =os.path.join(saveDir_root, project + "_" + tag+ "_all.jsonl")
    jlfile = open(jlfile_path,"w")
    jlfile.close()
    idx = 0

    with jsonlines.open(jlfile_path,"a") as jlf:
        for each in final:
            each["idx"] = idx
            idx += 1
            jlf.write_all([each])

    print(file_path, len(data))

if __name__ == "__main__":
    args = sys.argv[1:]
    input_jsons_dir = args[0]
    saveto_dir = args[1]
    get_files(input_jsons_dir,saveto_dir)
    
   