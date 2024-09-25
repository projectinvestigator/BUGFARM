import os
import sys
import json
import jsonlines
from json import loads
import subprocess
import random
import hashlib
from typing import Set, Tuple
from pathlib import Path
import .leam.utils as utils


def read_locations(location_json_path,project_name, mutants_dir,parsed_jlfile_path, unparsed_jlfile_path):

    f = open(location_json_path)
    data = json.load(f)
    f.close()

    id_src_set = {}
    original_methods_set = {}
    original_methods_list = []
    all_mutants_set = {}
    final_original_methods_list = []

    sampled_mutants_list = []
    #sampled_original_methods_list = []

    results = [] # temp structure: all mutants + original methods
    final = [] # final list to save: mutants + original methods
    unparsed_mutants = []

    for prediction in data:
        file_path = prediction["file_path"]
        mutant_class_name = file_path.split("/")[-1].split(".")[0]
        abs_mutants_dir = os.path.join(mutants_dir,"mutants",mutant_class_name+"_mutant")
        mutant_file_dir = os.path.join(abs_mutants_dir,project_name)
        mutant_line_dir = os.path.join(abs_mutants_dir,project_name+"_patches")

        mutant_file_dir = os.path.join(mutants_dir,project_name)
        mutant_line_dir = os.path.join(mutants_dir,project_name+"_patches")

        for dirpath, _, files in os.walk(mutant_file_dir):
            for file in files:
                src_file_path = os.path.join(dirpath,file)
                id = dirpath.split("/")[-1]
                id_key = id + file
                if id_key not in id_src_set:
                    id_src_set[id_key] = {"id":id, "mutated_src_file":src_file_path,"mutated_line":None}


        # get mutated src file path, mutated line numbers
        for dirpath, _, files in os.walk(mutant_line_dir):
            for file in files:
                line_patch_path = os.path.join(dirpath,file)
                patch = open(line_patch_path)
                content = patch.readlines()
                info = content[0]
                mutatedLineNo = info.split("-")[-1].split(" ")[0]
                for id_key in id_src_set:
                    if file.startswith(id_key):
                        id_src_set[id_key]["mutated_line"] = mutatedLineNo

        
        # get all original methods into original_methods_list
        for classpredictions in prediction["classPredictions"]:
            classname = classpredictions["qualifiedName"]
            for method in classpredictions["methodPredictions"]:
                methodSignature = method["methodSignature"]
                startLineNumber = method["startLineNumber"]
                endLineNumber = method["endLineNumber"]
                detailslines = method["line_predictions"]
                for line_predictions in detailslines:
                    mutatedLineNumber = line_predictions["line_number"]
                    # unique md5 for each method, file_path + startLineNumber
                    hash = hashlib.md5((file_path + str(startLineNumber) + "original method").encode('utf-8')).hexdigest() 
                    original_file = open(file_path)
                    original_src_content = original_file.readlines()
                    original_method_content = "".join(original_src_content[startLineNumber-1:endLineNumber+1])
                    # original method, target = 1
                    items = {"project":project_name,"file_path":file_path,"md5":hash,"start":startLineNumber,"end":endLineNumber,
                              "mutated line":mutatedLineNumber,"target":1,"func":original_method_content,"idx":"idx"} # add idx
                    if items["md5"] not in original_methods_set:
                        original_methods_set[items["md5"]] = []
                    original_methods_set[items["md5"]].append(items)
                    results.append(items)
        
        for original_sha in original_methods_set:
            sampled_original_method = random.sample(original_methods_set[original_sha], 1)
            original_methods_list.append(sampled_original_method[0])

            for each in original_methods_set[original_sha]:
                original_methods_list.append(each)

        
        # get mutants for methods in original_methods_list
        id = 0
        for id_key in id_src_set:
            id += 1
            mutant_file_path = id_src_set[id_key]["mutated_src_file"]
            mutated_lineno = id_src_set[id_key]["mutated_line"]
            for method in original_methods_list:
                if method["target"] == 1 and str(method["mutated line"]) == str(mutated_lineno):
                    startLineNumber = method["start"]
                    endLineNumber = method["end"]
                    mutant_file = open(mutant_file_path)
                    mutant_src_content = mutant_file.readlines()
                    mutant_method_content = "".join(mutant_src_content[startLineNumber-1:endLineNumber+1])
                    parsed,result = utils.read_java(mutant_file_path)
                    parsed,result = utils.parse_java_func_intervals("\n".join(mutant_src_content),mutant_file)
                    # print(parsed,result)
                    if result == True:
                        mutant_hash = hashlib.md5((file_path + str(startLineNumber) + "mutant").encode('utf-8')).hexdigest() 
                        mutant_items = {"project":project_name,"file_path":file_path,"md5":mutant_hash,"start":startLineNumber,"end":endLineNumber,
                                "mutated line":mutatedLineNumber,"target":0,"func":mutant_method_content,"original_method":method["func"],"idx":"idx"} # add idx
                        if mutant_hash not in all_mutants_set:
                            all_mutants_set[mutant_hash] = []
                        all_mutants_set[mutant_hash].append(mutant_items)
                        results.append(mutant_items)
                    else:
                        mutant_hash = hashlib.md5((file_path + str(startLineNumber) + "mutant").encode('utf-8')).hexdigest() 
                        mutant_items = {"project":project_name,"file_path":file_path,"md5":mutant_hash,"start":startLineNumber,"end":endLineNumber,
                                "mutated line":mutatedLineNumber,"target":0,"mutated_method":mutant_method_content,"original_method":method["func"],"idx":"idx"} # add idx
                        unparsed_mutants.append(mutant_items)

    # print(len(unparsed_mutants))
                        
    
    for sha in all_mutants_set:
        # if len(all_mutants_set[sha])>3:
        #     sampled_mutants_set = random.sample(all_mutants_set[sha], 3)
        # else:
        sampled_mutants_set = all_mutants_set[sha]
        for each in sampled_mutants_set:
            final.append(each)
            sampled_mutants_list.append(each)
            # id = 0
            for original_method in original_methods_list:
                original_method["mutated line"] = "null"
                if original_method["file_path"] == each["file_path"] and original_method["start"] == each["start"] and original_method not in final_original_methods_list and original_method not in final:
                    final.append(original_method)
                    final_original_methods_list.append(original_method)
                    break
                    
    # parsed mutants
    write_to_jsonl(parsed_jlfile_path,final)

    # unparsed mutants
    write_to_jsonl(unparsed_jlfile_path,unparsed_mutants)

    return len(final),len(sampled_mutants_list),len(final_original_methods_list),len(all_mutants_set),len(unparsed_mutants)
    

def write_to_jsonl(jlfile_path,mutants_list):
    index = 0
    jlfile = open(jlfile_path,"a")
    jlfile.close()

    for each in mutants_list:
        each["idx"] = index
        index += 1
        with jsonlines.open(jlfile_path,"a") as jlf:
            items = [each]
            jlf.write_all(items)


def process_projects(root_dir,sha):
    # go through the output dir and process results under output/res/
    sub_dir = os.path.join(root_dir,sha,"res")
    for dir in os.listdir(sub_dir):
        if dir.endswith("_res"):
            project_name = dir.split("/")[-1].split("_res")[0]
            outputs_dir = os.path.join(dir,"outputs")
            mutants_dir = os.path.join(dir,"mutants")
            dir_jsonl_files = os.path.join(root_dir,"mubert_jsonlines")
            Path(dir_jsonl_files).mkdir(parents=True, exist_ok=True)
            parsed_save_jsonl = os.path.join(dir_jsonl_files,"parsed_mubert_"+project_name+".jsonl")
            unparsed_save_jsonl = os.path.join(dir_jsonl_files,"unparsed_mubert_"+project_name+".jsonl")
            classnames = []
            input_locs = []

            for dirpath, _, files in os.walk(mutants_dir):
                for file in files:
                    if file.endswith(".patch"):
                        classname = dirpath.split("/")[-2].replace("_mutant","_output")
                        if classname not in classnames:
                            classnames.append(classname)
            for class_output in classnames:
                loc_file_path = os.path.join(outputs_dir,class_output,project_name,"locations.json")
                input_locs.append(loc_file_path)
            
            all_num = 0
            parsed_mutants = 0
            original = 0
            unparsed_mutants = 0
            # v = 0
            
            for loc_json in input_locs:
                all,parsed_mutant_num,original_method_num,verify,unparsed_mutant_num = read_locations(loc_json,project_name,dir,parsed_save_jsonl,unparsed_save_jsonl)
                all_num += all
                parsed_mutants += parsed_mutant_num
                original += original_method_num
                # v += verify
                unparsed_mutants += unparsed_mutant_num

            print(project_name, "items:",all_num, "parsed mutants:",parsed_mutants, \
                " methods:",original, " unparsed mutants:", unparsed_mutants)

                    
if __name__ == "__main__":
    args = sys.argv[1:]
    root_dir = args[0]
    sha = args[1]
    process_projects(root_dir,sha)