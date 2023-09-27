import json
import csv
import os
import sys
from typing import Set, Tuple
from pathlib import Path
import random
import math
import subprocess
import glob
import jsonlines

def get_file(project_name,saveto,res_dir):
    file_name = saveto.split("/")[-1]
    file_path = os.path.join(saveto,file_name) #project_name+"_input.csv")
    file = open(file_path,"a")
    file.close()
    curpath = os.path.abspath(os.getcwd())
    project_path = os.path.join(curpath,f"projects/{project_name}")

    info_root_path = os.path.join(res_dir, project_name+"_res")

    mutants_path = os.path.join(info_root_path, "mutants")
    outputs_path = os.path.join(info_root_path, "outputs")

    try:
        os.mkdir(info_root_path)
        os.mkdir(mutants_path)
        os.mkdir(outputs_path)
    except OSError as error: 
            print(error)


    files = subprocess.Popen(["ls"] + glob.glob(os.path.join(curpath,f'projects/{project_name}/**/src/main/java/**/*.java'), recursive=True), stdout=subprocess.PIPE)
    source_paths = [x.decode('ascii').strip() for x in files.stdout.readlines()]
    #print(source_paths,project_path)

    for src_path in source_paths:
        if "-info" not in src_path:
            with open(file_path,"a") as f:
                writer = csv.writer(f)
                short_name = src_path.split("/")[-1].split(".")[0]
                
                mutant_path = os.path.join(mutants_path,short_name+"_mutant")
                output_path = os.path.join(outputs_path,short_name+"_output")
                try:
                    os.mkdir(mutant_path)
                    os.mkdir(output_path)
                except OSError as error: 
                        print(error)

                writer.writerow([project_path,src_path,mutant_path,output_path,short_name]) #project_path, java_path, mutant_path, output_path


if __name__ == "__main__":
    args = sys.argv[1:]
    saveto = args[0]
    res_dir = args[1]
    
    projects = [
        "jackson-databind","gson", "jfreechart",
        "commons-cli","commons-csv", "jsoup"
        "gson", "jfreechart","commons-codec", 
        "commons-compress", "commons-math", "jackson-core", 
        "jackson-dataformat-xml", "commons-collections","commons-jxpath",
        "commons-lang","jackson-databind", "joda-time"
        ]

    for project in projects:
        get_file(project,saveto,res_dir)