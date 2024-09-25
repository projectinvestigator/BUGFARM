import csv
import glob
import jsonlines
import json
import math
import os
import sys
import subprocess
import random
import utils
from typing import Set, Tuple
from pathlib import Path

# numbers of methods to sample for each project
projects_method = {
    "commons-cli":30, "commons-codec":58, "commons-compress":94,
    "commons-csv":41, "gson":19, "jfreechart":287, 
    "jsoup":35, "commons-math":107, "jackson-core":90,
    "jackson-dataformat-xml":126, "commons-collections":98,"commons-jxpath":166,
    "commons-lang":101, "jackson-databind":248, "joda-time":194
    }

# generate input parsed_ochiai_result files for each project, 
# input: project name
# output: `parsed_ochiai_result` files will be in dir `location2/project_name`, which are inputs for leam mutant generation 
def get_files(project_name):
    files = subprocess.Popen(["ls"] + glob.glob(f'projects/{project_name}/**/src/main/java/**/*.java', recursive=True), stdout=subprocess.PIPE)
    source_paths = [x.decode('ascii').strip() for x in files.stdout.readlines()]

    counter = 0
    set_pre_class = []
    for path in source_paths:
        if "main/java/" not in path:
            continue
        if ".java" not in path:
            continue
        set = utils.read_java(path)
        for item in set:   
            set_pre_class.append(item)

    if set_pre_class:
        print(len(set_pre_class),project_name)
        list_per_file = {}
        sampled_set = random.sample(set_pre_class, projects_method[project_name])
        for pair in sampled_set:
            list = []
            if (pair[1]-pair[0]-1 <= 3) and (pair[1]-pair[0]-1 >=0) :
                list = random.sample(range(pair[0]+1, pair[1]), round(pair[1]-pair[0]-1) )
            elif (pair[1]-pair[0]-1 > 3):
                list = random.sample(range(pair[0]+1, pair[1]), 3)
            if pair[3] not in list_per_file:
                list_per_file[pair[3]]=[]
            list_per_file[pair[3]].extend(list)

        for path in list_per_file:
            list_per_file[path].sort()
            test_class = path.split("main/java/")[1].split(".java")[0].replace("/",".")
            if list_per_file[path]:
                counter += 1
                root_dir_path = os.path.join(main_dir,"location2")
                Path(root_dir_path).mkdir(parents=True, exist_ok=True)

                project_dir_path = os.path.join(root_dir_path, project_name)
                Path(project_dir_path).mkdir(parents=True, exist_ok=True)
                
                dir_path = os.path.join(project_dir_path, str(counter))
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                location_file_path = os.path.join(dir_path,"parsed_ochiai_result")
                file = open(location_file_path,"w")
                file.close()
                
                with open(location_file_path, "a") as f:
                    for line in list_per_file[path]:
                        strs = test_class + "#" + str(line) + "	 1  " + path
                        f.writelines(strs)
                        f.writelines("\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    main_dir = args[0]
    
    for project in projects_method:
        get_files(project,main_dir)
        print(project, "done")