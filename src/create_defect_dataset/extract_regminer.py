import os
import sys
import json
import jsonlines
from json import loads
from typing import Set, Tuple
from pathlib import Path
import .leam.utils as utils

def is_not_test(dir):
    flags = ["/test/","/Test/","/TEST/"]
    for flg in flags:
        if flg in dir:
            return False 
    return True

def get_diff(dir1,dir2,preoject_name,patch_dir_num):
    pairs = {}

    source_paths_1 = []
    source_paths_2 = []

    patch_dir = None

    for dirpath, _, files in os.walk(dir1):
        for file in files:
            if file.endswith(".java") and "/src/" in dirpath and is_not_test(dirpath):
                file_path = os.path.join(dirpath,file)
                source_paths_1.append(file_path)

    for dirpath, _, files in os.walk(dir2):
        for file in files:
            if file.endswith(".java") and "/src/" in dirpath and is_not_test(dirpath):
                file_path = os.path.join(dirpath,file)
                source_paths_2.append(file_path)

    for file1 in source_paths_1:
        try:
            cm = file1.split("/rfc/")[1]
        except:
            print("[BUG]  ", dir1, source_paths_1, file1)
            exit(0)
        if cm not in pairs:
            pairs[cm] = []
        pairs[cm].append(file1)

    for file2 in source_paths_2:
        cm2 = file2.split("/ric/")[1]
        if cm2 in pairs:
            pairs[cm2].append(file2)

    for pair in pairs:
        if len(pairs[pair])==2:
            if "rfc" in pairs[pair][0]:
                fixed = pairs[pair][0]
            if "ric" in pairs[pair][1]:
                buggy = pairs[pair][1] 
            # 0 - fixed version, 1 - buggy version
            diff=os.popen('diff '+fixed+' '+buggy).read()
            if diff:
                patch_dir = "final_patch/"+preoject_name + "_final_patches-"+patch_dir_num
                if not os.path.exists(patch_dir):
                    os.mkdir(patch_dir)
                patch_path = os.path.join(patch_dir,pair.replace("/","_")+".patch")
                patch_generation = os.popen('diff -up ' + fixed +' '+ buggy + ' > '+patch_path).read()
    
    if patch_dir is not None:
        return patch_dir
    else:
        print(project_name, "no patch!!!")
        return None

def extract_patch(patch_path,project_name,jlfile_path):
    jlfile = open(jlfile_path,"a")
    jlfile.close()

    with open(patch_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rfc_changed_lines = {}
    ric_changed_lines = {}

    fixed_changed_lines = {}
    ric_changed_lines = {}

    actual_fixed_lines = {} # changed lines in fixed file
    actual_buggy_lines = {} # changed line in buggy file

    fixed_methods = []
    buggy_methods = []

    final = []
    final_fixed_methods = []
    final_buggy_methods = []

    index = 0
    for line in lines:
        if line.startswith("---"):
            rfc_file = line.replace("\t"," ").split(" ")[1]
            if rfc_file not in rfc_changed_lines:
                rfc_changed_lines[rfc_file] = []
        elif line.startswith("+++"):
            ric_file = line.replace("\t"," ").split(" ")[1]
            if ric_file not in ric_changed_lines:
                ric_changed_lines[ric_file] = []
        elif line.startswith("@@"):
            rfc_line_start = line.split(" ")[1].split(",")[0].replace("-","").replace("+","")
            rfc_line_length = line.split(" ")[1].split(",")[1]

            ric_line_start = line.split(" ")[2].split(",")[0].replace("-","").replace("+","")
            if len(line.split(" ")[2].split(","))<2:
                continue
            ric_line_length = line.split(" ")[2].split(",")[1]

            rfc_changed_lines[rfc_file].append([int(rfc_line_start),int(rfc_line_length),int(index)+1])
            ric_changed_lines[ric_file].append([int(ric_line_start),int(ric_line_length),int(index)+1])
        index += 1
        

    
    rfc_set = utils.read_java(rfc_file)
    with open(rfc_file, 'r') as f:
        rfc_content = f.readlines()
    
    ric_set = utils.read_java(ric_file)
    with open(ric_file, 'r') as f:
        ric_content = f.readlines()

    original_methods_list = []

    for file in rfc_changed_lines:
        if file not in actual_fixed_lines:
            actual_fixed_lines[file] = []
        for rfc_changed_part in rfc_changed_lines[file]:
            fixed_snippet_start = rfc_changed_part[0]
            fixed_snippet_length = rfc_changed_part[1]
            fixed_start_patch_idx = rfc_changed_part[2]

            fixed_snippet = []
            add = 0
            for line in lines[fixed_start_patch_idx+1:]:
                if len(fixed_snippet) < fixed_snippet_length:
                    if line.startswith(" "):
                        fixed_snippet.append(line)
                        add += 1
                    elif line.startswith("-"):
                        fixed_snippet.append(line)
                        add += 1
                        #line_patch_idx = lines.index(line)
                        changed_line_no = fixed_snippet_start + add
                        if not (line.replace(" ","").startswith("-//")) and not (line.replace(" ","").startswith("-*")):                    
                            actual_fixed_lines[file].append(changed_line_no)
                            for original_method_info in rfc_set:
                                start = int(original_method_info[0])
                                end = int(original_method_info[1])
                                if int(changed_line_no) >= start and int(changed_line_no) <= end:
                                    original_method = original_method_info[2]
                                    items = {"project":project_name,"file_path":file,"start":start,"end":end,"idx":"idx","patch":patch_path,"target":0,"func":original_method}
                                    if items not in fixed_methods:
                                        fixed_methods.append(items)
                    
    for file in ric_changed_lines:
        if file not in actual_buggy_lines:
            actual_buggy_lines[file] = []
        for ric_changed_part in ric_changed_lines[file]:
            buggy_snippet_start = ric_changed_part[0]
            buggy_snippet_length = ric_changed_part[1]
            buggy_start_patch_idx = ric_changed_part[2]

            buggy_snipped = []
            add = 0
            for line in lines[buggy_start_patch_idx+1:]:
                if len(buggy_snipped) < buggy_snippet_length:
                    if line.startswith(" "):
                        buggy_snipped.append(line)
                        add += 1
                    elif line.startswith("+"):
                        buggy_snipped.append(line)
                        add += 1
                        #line_patch_idx = lines.index(line)
                        changed_line_no = buggy_snippet_start + add
                        actual_buggy_lines[file].append(changed_line_no)
                        #print(line,changed_line_no,buggy_snippet_start)
                        for mutant_info in ric_set:
                            start = int(mutant_info[0])
                            end = int(mutant_info[1])
                            if int(changed_line_no) >= start and int(changed_line_no) <= end:
                                mutant_func = mutant_info[2]
                                items = {"project":project_name,"file_path":file,"start":start,"end":end,"idx":"idx","patch":patch_path,"target":1,"func":mutant_func}
                                if items not in buggy_methods:
                                    buggy_methods.append(items)
                                
    idx = 0
    for each in fixed_methods:
        if each["target"] == 0:
            for b in buggy_methods:
                if b["target"] == 1 and b["func"].split("{")[0].replace(" ","") == each ["func"].split("{")[0].replace(" ",""):
                    with jsonlines.open(jlfile_path,"a") as jlf:
                        each["idx"] = idx
                        idx += 1
                        b["idx"] = idx
                        idx +=1
                        jlf.write_all([each])
                        jlf.write_all([b])
                        final.append(each)
                        final.append(b)
                        final_fixed_methods.append(each)
                        final_buggy_methods.append(b)
    
    return len(final_buggy_methods),len(final_fixed_methods),len(final)
                

def process_dir(patch_dir,project_name,jlfile_path,patch_dir_num):
    mutants_num = 0
    methods_num = 0
    items_num = 0
    for dirpath, _, files in os.walk(patch_dir):
        for file in files:
            if file.endswith(".patch"):
                patch_path = os.path.join(dirpath,file)
                mutant_num,method_num,item_num = extract_patch(patch_path,project_name,jlfile_path)
                mutants_num += mutant_num
                methods_num += method_num
                items_num += item_num
    
    print(project_name,patch_dir_num,"total mutant:",mutants_num,"total methods:",methods_num,"total items:",items_num)


def extract_per_project(reg_dir,save_dir):
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    for sub_dir in os.walk(reg_dir):
        project_name = sub_dir.split("_")[-1]
        if project_name not in projects_dir:
            projects_dir[project_name] = sub_dir

    for project_name in projects_dir:
        dir = projects_dir[project_name]

        for file in os.listdir(dir):
            d = os.path.join(dir, file)
            if os.path.isdir(d):
                rfc_dir = os.path.join(d,"rfc")
                ric_dir = os.path.join(d,"ric")
                patch_dir_id = d.split("/")[-1]
                jlfile_path = os.path.join(save_dir,project_name+"-"+patch_dir_id+".jsonl")
                patch_dir = get_diff(rfc_dir,ric_dir,project_name,patch_dir_id)
                if patch_dir:
                    process_dir(patch_dir,project_name,jlfile_path,patch_dir_id)
                else:
                    print(project_name, "no patches")

def combine_final_results(save_dir):
    data = []
    jlfile_path = os.path.join(save_dir,"final_regminer.jsonl")
    jlfile = open(jlfile_path,"w")
    jlfile.close()

    for dirpath, _, files in os.walk(dir):
        for file in files:
            if ".jsonl" in file:
                file_path = os.path.join(dirpath,file)
                with open(file_path, "r") as jl:
                    for method in [loads(each_line) for each_line in jl]:
                        mod = method["func"].replace("\t"," ")
                        method["func"] = mod
                        data.append(method)
    idx = 0
    with jsonlines.open(jlfile_path,"a") as jlf:
        for method in data:
            method["idx"] = idx
            idx += 1
            jlf.write_all([method])

def extract(reg_dir,save_dir):
    extract_per_project(reg_dir,save_dir)
    combine_final_results(save_dir)

if __name__ == "__main__":
    # args = sys.argv[1:]
    # reg_dir = args[0]
    # save_dir = args[1]

    reg_dir = "data/defect/regminer_mutants"
    save_dir = "data/defect/regminer_mutants"
    # args: mutants_dir, output_dir; here config output_dir same as input_dir
    extract_per_project(reg_dir,save_dir)
    combine_final_results(save_dir)
