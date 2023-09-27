import os
import sys
import csv

# input: dir - locations directory which includes input files for leam, 
#        save_dir - directory to save file, 
#        save_file - file path to save
# output: a file `save_file` which includes input index to run in a batch
def readProjectName(dir, save_dir, save_file):
    saveTo = os.path.join(save_dir,save_file)
    file = open(saveTo,"a")
    file.close()
    list = []
    for dirpath, _, files in os.walk(dir):
        for file in files:
            if file == "parsed_ochiai_result":
                project = dirpath.split("/")[-2] + "_" + dirpath.split("/")[-1]
                list.append(project)
    list.sort()

    for project in list:
        with open(saveTo, "a") as f:
            f.writelines(project)
            f.writelines("\n")

if __name__ == "__main__":
    args = sys.argv[1:]
    dir = args[0]
    save_dir = args[1]
    save_file = args[2]
    readProjectName(dir, save_dir, save_file)
